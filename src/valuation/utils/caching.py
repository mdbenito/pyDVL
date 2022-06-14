"""
Distributed caching of functions, using memcached.
TODO: wrap this to allow for different backends
"""
import socket
from dataclasses import dataclass, field, make_dataclass
from functools import wraps
from hashlib import blake2b
from io import BytesIO
from time import time
from typing import Callable, Iterable

from cloudpickle import Pickler
from pymemcache import MemcacheUnexpectedCloseError
from pymemcache.client import Client, RetryingClient
from pymemcache.serde import PickleSerde

from valuation.utils.logging import logger
from valuation.utils.types import unpackable

PICKLE_VERSION = 5  # python >= 3.8


@unpackable
@dataclass
class ClientConfig:
    server: str = ("localhost", 11211)
    connect_timeout: float = 1.0
    timeout: float = 1.0
    no_delay: bool = True
    serde: PickleSerde = PickleSerde(pickle_version=PICKLE_VERSION)


@unpackable
@dataclass
class MemcachedConfig:
    client_config: ClientConfig = field(default_factory=ClientConfig)
    threshold: float = 0.3
    ignore_args: Iterable[str] = None


def _serialize(x):
    pickled_output = BytesIO()
    pickler = Pickler(pickled_output, PICKLE_VERSION)
    pickler.dump(x)
    return pickled_output.getvalue()


def memcached(
    client_config: ClientConfig = None,
    threshold: float = 0.3,
    ignore_args: Iterable[str] = None,
):
    """Decorate a callable with this in order to have transparent caching.

    The function's code, constants and all arguments (except for those in
    `ignore_args` are used to generate the key for the remote cache.

    **FIXME?**:
        Due to the need to pickle memcached functions, this returns a class
        instead of a function. This has the drawback of a messy docstring.

    :param client_config: config for pymemcache.client.Client().
        Will be merged on top of the default configuration.


    :param threshold: computations taking below this value (in seconds) are not
        cached
    :param ignore_args: Do not take these keyword arguments into account when
        hashing the wrapped function for usage as key in memcached
    :return: A wrapped function

    The default configuration is::

        default_config = dict(
            server=('localhost', 11211),
            connect_timeout=1.0,
            timeout=0.1,
            # IMPORTANT! Disable small packet consolidation:
            no_delay=True,
            serde=serde.PickleSerde(pickle_version=PICKLE_VERSION)
        )
    """
    if ignore_args is None:
        ignore_args = []

    # Do I really need this?
    def connect(config: ClientConfig):
        """First tries to establish a connection, then tries setting and
        getting a value."""
        try:
            test_config = dict(**config)
            # test_config.update(timeout=config.connect_timeout)  # allow longer delays
            client = RetryingClient(
                Client(**test_config),
                attempts=3,
                retry_delay=0.1,
                retry_for=[MemcacheUnexpectedCloseError],
            )
        except Exception as e:
            logger.error(
                f"@memcached: Timeout connecting "
                f'to {config["server"]} after '
                f"{config.connect_timeout} seconds: {str(e)}"
            )
            raise e
        else:
            try:
                import uuid

                temp_key = str(uuid.uuid4())
                client.set(temp_key, 7)
                assert client.get(temp_key) == 7
                client.delete(temp_key, 0)
                return client
            except AssertionError as e:
                logger.error(
                    f"@memcached: Failure saving dummy value "
                    f'to {config["server"]}: {str(e)}'
                )

    def wrapper(fun: Callable):
        # noinspection PyUnresolvedReferences
        signature: bytes = _serialize((fun.__code__.co_code, fun.__code__.co_consts))

        @wraps(fun, updated=[])  # don't try to use update() for a class
        class Wrapped:
            def __init__(self, config: ClientConfig):
                self.config = config
                self.cache_info = make_dataclass(
                    "CacheInfo",
                    ["sets", "misses", "hits", "timeouts", "errors", "reconnects"],
                )(0, 0, 0, 0, 0, 0)
                self.client = connect(self.config)

            def __call__(self, *args, **kwargs):
                key_kwargs = {k: v for k, v in kwargs.items() if k not in ignore_args}
                arg_signature: bytes = _serialize((args, list(key_kwargs.items())))

                # FIXME: do I really need to hash this?
                # FIXME: ensure that the hashing algorithm is portable
                # FIXME: determine right bit size
                # NB: I need to create the hasher object here because it can't be
                #  pickled
                key = blake2b(signature + arg_signature).hexdigest().encode("ASCII")
                result = None
                try:
                    result = self.client.get(key)
                except socket.timeout as e:
                    self.cache_info.timeouts += 1
                    logger.warning(f"{type(self).__name__}: {str(e)}")
                except OSError as e:
                    self.cache_info.errors += 1
                    logger.warning(f"{type(self).__name__}: {str(e)}")
                except AttributeError as e:
                    # FIXME: this depends on _recv() failing on invalid sockets
                    # See pymemcache.base.py,
                    self.cache_info.reconnects += 1
                    logger.warning(f"{type(self).__name__}: {str(e)}")
                    self.client = connect(self.config)

                start = time()
                if result is None:
                    result = fun(*args, **kwargs)
                    end = time()
                    # TODO: make the threshold adaptive
                    if end - start >= threshold:
                        self.client.set(key, result, noreply=True)
                        self.cache_info.sets += 1
                    self.cache_info.misses += 1
                else:
                    self.cache_info.hits += 1
                return result

            def __getstate__(self):
                """Enables pickling after a socket has been opened to the
                memacached server, by removing the client from the stored data.
                """
                odict = self.__dict__.copy()
                del odict["client"]
                return odict

            def __setstate__(self, d: dict):
                """Restores a client connection after loading from a pickle."""
                self.config = d["config"]
                self.cache_info = d["cache_info"]
                self.client = Client(**self.config)

        Wrapped.__doc__ = (
            f"A wrapper around {fun.__name__}() with remote caching enabled.\n"
            + (Wrapped.__doc__ or "")
        )
        Wrapped.__name__ = f"memcached_{fun.__name__}"
        path = list(reversed(fun.__qualname__.split(".")))
        patched = [f"memcached_{path[0]}"] + path[1:]
        Wrapped.__qualname__ = ".".join(reversed(patched))

        # TODO: pick from some config file or something
        config = ClientConfig()
        if client_config is not None:
            config.update(client_config)
        return Wrapped(config)

    return wrapper
