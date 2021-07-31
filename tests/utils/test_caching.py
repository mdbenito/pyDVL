import numpy as np

from typing import Iterable
from valuation.utils import memcached, map_reduce, MapReduceJob
from valuation.utils.logging import start_logging_server, logger


def test_memcached_single_job(memcached_client):
    start_logging_server()
    client, config = memcached_client

    # TODO: maybe this should be a fixture too...
    @memcached(config=config, threshold=0)  # Always cache results
    def foo(indices: Iterable[int]) -> float:
        return float(np.sum(indices))

    n = 1000
    foo(np.arange(n))
    hits_before = client.stats()[b'get_hits']
    foo(np.arange(n))
    hits_after = client.stats()[b'get_hits']

    assert hits_after > hits_before


def test_memcached_parallel_jobs(memcached_client):
    start_logging_server()
    client, config = memcached_client

    @memcached(config=config,
               threshold=0,  # Always cache results
               # Note that we typically do NOT want to ignore run_id
               ignore_args=['job_id', 'run_id'])
    def foo(indices: Iterable[int], job_id: int, run_id: int) -> float:
        logger.info(f"run_id: {run_id}, running...")
        return float(np.sum(indices))

    n = 1234
    nruns = 10
    hits_before = client.stats()[b'get_hits']
    job = MapReduceJob.from_fun(foo, np.sum)
    result = map_reduce(job, data=np.arange(n), num_jobs=4, num_runs=nruns)
    hits_after = client.stats()[b'get_hits']

    assert result[0] == n*(n-1)/2  # Sanity check
    # FIXME! This is non-deterministic: if packets are delayed for longer than
    #  the timeout configured then we won't have nruns hits. So we add this
    #  good old hard-coded magic number here.
    assert hits_after - hits_before >= nruns - 2
