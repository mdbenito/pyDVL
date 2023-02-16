r"""
Monte Carlo approximations to Shapley Data values.

.. warning::
   You probably want to use the common interface provided by
   :func:`~pydvl.value.shapley.compute_shapley_values` instead of directly using
   the functions in this module.

Because exact computation of Shapley values requires $\mathcal{O}(2^n)$
re-trainings of the model, several Monte Carlo approximations are available.
The first two sample from the powerset of the training data directly:
:func:`combinatorial_montecarlo_shapley` and :func:`owen_sampling_shapley`. The
latter uses a reformulation in terms of a continuous extension of the utility.

Alternatively, employing another reformulation of the expression above as a sum
over permutations, one has the implementation in
:func:`permutation_montecarlo_shapley`, or using an early stopping strategy to
reduce computation :func:`truncated_montecarlo_shapley`.

.. seealso::
   It is also possible to use :func:`~pydvl.value.shapley.gt.group_testing_shapley`
   to reduce the number of evaluations of the utility. The method is however
   typically outperformed by others in this module.

.. seealso::
   Additionally, you can consider grouping your data points using
   :class:`~pydvl.utils.dataset.GroupedDataset` and computing the values of the
   groups instead. This is not to be confused with "group testing" as
   implemented in :func:`~pydvl.value.shapley.gt.group_testing_shapley`: any of
   the algorithms mentioned above, including Group Testing, can work to valuate
   groups of samples as units.
"""

import logging
import math
import operator
from enum import Enum
from functools import reduce
from itertools import cycle, takewhile
from time import sleep
from typing import NamedTuple, Optional, Sequence, cast
from warnings import warn

import numpy as np
from numpy.typing import NDArray
from tqdm import tqdm

from pydvl.utils.config import ParallelConfig
from pydvl.utils.numeric import random_powerset
from pydvl.utils.parallel import MapReduceJob, init_parallel_backend
from pydvl.utils.progress import maybe_progress
from pydvl.utils.utility import Utility
from pydvl.value.result import ValuationResult
from pydvl.value.stopping import StoppingCriterion

from .actor import get_shapley_coordinator, get_shapley_worker
from .types import PermutationBreaker


class MonteCarloResults(NamedTuple):
    # TODO: remove this class and use Valuation
    values: NDArray[np.float_]
    stderr: NDArray[np.float_]
    counts: NDArray[np.int_]


logger = logging.getLogger(__name__)

__all__ = [
    "truncated_montecarlo_shapley",
    "permutation_montecarlo_shapley",
    "combinatorial_montecarlo_shapley",
    "owen_sampling_shapley",
]


def truncated_montecarlo_shapley(
    u: Utility,
    *,
    done: StoppingCriterion,
    permutation_tolerance: Optional[float] = None,
    n_jobs: int = 1,
    config: ParallelConfig = ParallelConfig(),
    coordinator_update_period: int = 10,
    worker_update_period: int = 5,
) -> ValuationResult:
    """Monte Carlo approximation to the Shapley value of data points.

    This implements the permutation-based method described in
    :footcite:t:`ghorbani_data_2019`. It is a Monte Carlo estimate of the sum
    over all possible permutations of the index set, with a double stopping
    criterion.

    .. todo::
       Think of how to add Robin-Gelman or some other more principled stopping
       criterion.

    Instead of naively implementing the expectation, we sequentially add points
    to a dataset from a permutation. Once a marginal utility is close enough to
    the total utility we set all marginals to 0 for the remainder of the
    permutation. We keep sampling permutations and updating all shapley values
    until the stopping criterion returns ``True``.

    :param u: Utility object with model, data, and scoring function
    :param done: Check on the results which decides when to stop
        sampling permutations.
    :param permutation_tolerance: Tolerance for the interruption of computations
        within a permutation. This is called "performance tolerance" in
        :footcite:t:`ghorbani_data_2019`. Leave empty to set to
        ``total_utility / len(u.data) / 100``.
    :param n_jobs: number of jobs processing permutations. If None, it will be
        set to :func:`available_cpus`.
    :param config: Object configuring parallel computation, with cluster
        address, number of cpus, etc.
    :param coordinator_update_period: in seconds. Check status with the job
        coordinator every so often.
    :param worker_update_period: interval in seconds between different
        updates to and from the coordinator
    :return: Object with the data values.

    """
    if config.backend == "sequential":
        raise NotImplementedError(
            "Truncated MonteCarlo Shapley does not work with "
            "the Sequential parallel backend."
        )

    parallel_backend = init_parallel_backend(config)
    n_jobs = parallel_backend.effective_n_jobs(n_jobs)
    u_id = parallel_backend.put(u)

    coordinator = get_shapley_coordinator(config=config, done=done)  # type: ignore

    workers = [
        get_shapley_worker(  # type: ignore
            u=u_id,
            coordinator=coordinator,
            worker_id=worker_id,
            update_period=worker_update_period,
            config=config,
            permutation_breaker=low_marginal_breaker(u, permutation_tolerance),
        )
        for worker_id in range(n_jobs)
    ]
    for worker in workers:
        worker.run(block=False)

    while not coordinator.check_convergence():
        sleep(coordinator_update_period)

    return coordinator.accumulate()

    # Something like this would be nicer, but it doesn't seem to be possible
    # to start the workers from the coordinator.
    # coordinator.add_workers(
    #     n_workers=n_jobs,
    #     u=u_id,
    #     update_period=worker_update_period,
    #     config=config,
    #     permutation_breaker=permutation_breaker,
    # )
    #
    # return coordinator.run(delay=coordinator_update_period)


def low_marginal_breaker(u: Utility, rtol: Optional[float]) -> PermutationBreaker:
    """Break a permutation if the marginal utility is too low.

    This is a helper function for :func:`permutation_montecarlo_shapley`.
    It is used as a default value for the ``permutation_breaker`` argument.

    :param u: Utility object with model, data, and scoring function
    :param rtol: Relative tolerance. The permutation is broken if the
        marginal utility is less than ``total_utility * rtol``. Leave empty to
        set to ``total_utility / len(u.data) / 100``.
    :return: A function which decides whether to interrupt processing a
        permutation and set all subsequent marginals to zero.
    """

    logger.info("Computing total utility for low marginal permutation interruption.")
    total = u(u.data.indices)
    if rtol is None:
        rtol = total / len(u.data) / 100

    def _break(idx: int, marginals: NDArray[np.float_]) -> bool:
        return abs(float(marginals[idx])) < total * cast(float, rtol)

    return _break


def _permutation_montecarlo_shapley(
    u: Utility,
    *,
    done: StoppingCriterion,
    permutation_breaker: Optional[PermutationBreaker] = None,
    algorithm_name: str = "permutation_montecarlo_shapley",
    progress: bool = False,
    job_id: int = 1,
) -> ValuationResult:
    """Helper function for :func:`permutation_montecarlo_shapley`.

    Computes marginal utilities of each training sample in
    :obj:`pydvl.utils.utility.Utility.data` by iterating through randomly
    sampled permutations.

    :param u: Utility object with model, data, and scoring function
    :param done: Check on the results which decides when to stop
    :param permutation_breaker: A callable which decides whether to interrupt
        processing a permutation and set all subsequent marginals to zero.
    :param algorithm_name: For the results object. Used internally by different
        variants of Shapley using this subroutine
    :param progress: Whether to display progress bars for each job.
    :param job_id: id to use for reporting progress (e.g. to place progres bars)
    :return: An object with the results
    """
    n = len(u.data)
    result = ValuationResult.empty(algorithm_name, n)

    pbar = tqdm(disable=not progress, position=job_id, total=100, unit="%")
    while not done(result):
        pbar.n = 100 * done.completion()
        pbar.refresh()
        prev_score = 0.0
        permutation = np.random.permutation(u.data.indices)
        permutation_done = False
        for i, idx in enumerate(permutation):
            if permutation_done:
                score = prev_score
            else:
                score = u(permutation[: i + 1])
            marginal = score - prev_score
            result.update(idx, marginal)
            prev_score = score
            if (
                not permutation_done
                and permutation_breaker
                and permutation_breaker(idx, result.values)
            ):
                permutation_done = True
    return result


def permutation_montecarlo_shapley(
    u: Utility,
    done: StoppingCriterion,
    *,
    permutation_breaker: Optional[PermutationBreaker] = None,
    n_jobs: int = 1,
    config: ParallelConfig = ParallelConfig(),
    progress: bool = False,
) -> ValuationResult:
    r"""Computes an approximate Shapley value by sampling independent index
    permutations to approximate the sum:

    $$v_u(x_i) = \frac{1}{n!} \sum_{\sigma \in \Pi(n)}
    [u(\sigma_{i-1} \cup {i}) − u(\sigma_{i})].$$

    See :ref:`data valuation` for details.

    :param u: Utility object with model, data, and scoring function.
    :param done: function checking whether computation must stop.
    :param permutation_breaker: An optional callable which decides whether to
        interrupt processing a permutation and set all subsequent marginals to
        zero. Typically used to stop computation when the marginal is small.
    :param n_jobs: number of jobs across which to distribute the computation.
    :param config: Object configuring parallel computation, with cluster
        address, number of cpus, etc.
    :param progress: Whether to display progress bars for each job.
    :return: Object with the data values.
    """

    map_reduce_job: MapReduceJob[Utility, ValuationResult] = MapReduceJob(
        u,
        map_func=_permutation_montecarlo_shapley,
        reduce_func=lambda results: reduce(operator.add, results),
        map_kwargs=dict(
            algorithm_name="permutation_montecarlo_shapley",
            done=done,
            permutation_breaker=permutation_breaker,
            progress=progress,
        ),
        config=config,
        n_jobs=n_jobs,
    )
    return map_reduce_job()


def _combinatorial_montecarlo_shapley(
    indices: Sequence[int],
    u: Utility,
    done: StoppingCriterion,
    *,
    progress: bool = False,
    job_id: int = 1,
) -> ValuationResult:
    """Helper function for :func:`combinatorial_montecarlo_shapley`.

    This is the code that is sent to workers to compute values using the
    combinatorial definition.

    :param u: Utility object with model, data, and scoring function
    :param done: Check on the results which decides when to stop sampling
        subsets for an index.
    :param progress: Whether to display progress bars for each job.
    :param job_id: id to use for reporting progress
    :return: A tuple of ndarrays with estimated values and standard errors
    """
    n = len(u.data)

    if len(np.unique(indices)) != len(indices):
        raise ValueError("Repeated indices passed")

    # Correction coming from Monte Carlo integration so that the mean of the
    # marginals converges to the value: the uniform distribution over the
    # powerset of a set with n-1 elements has mass 2^{n-1} over each subset. The
    # additional factor n corresponds to the one in the Shapley definition
    correction = 2 ** (n - 1) / n
    variances = np.zeros(shape=n)
    result = ValuationResult.empty("combinatorial_montecarlo_shapley", n)

    repeat_indices = takewhile(lambda _: not done(result), cycle(indices))
    pbar = tqdm(disable=not progress, position=job_id, total=100, unit="%")
    for idx in repeat_indices:
        pbar.n = 100 * done.completion()
        pbar.refresh()
        # Randomly sample subsets of full dataset without idx
        subset = np.setxor1d(u.data.indices, [idx], assume_unique=True)
        s = next(random_powerset(subset, n_samples=1))
        marginal = (u({idx}.union(s)) - u(s)) / math.comb(n - 1, len(s))
        result.update(idx, correction * marginal)

    return result


def combinatorial_montecarlo_shapley(
    u: Utility,
    done: StoppingCriterion,
    *,
    n_jobs: int = 1,
    config: ParallelConfig = ParallelConfig(),
    progress: bool = False,
) -> ValuationResult:
    r"""Computes an approximate Shapley value using the combinatorial
    definition:

    $$v_u(i) = \frac{1}{n} \sum_{S \subseteq N \setminus \{i\}}
    \binom{n-1}{ | S | }^{-1} [u(S \cup \{i\}) − u(S)]$$

    This consists of randomly sampling subsets of the power set of the training
    indices in :attr:`~pydvl.utils.utility.Utility.data`, and computing their
    marginal utilities. See :ref:`data valuation` for details.

    Note that because sampling is done with replacement, the approximation is
    poor even for $2^{m}$ subsets with $m>n$, even though there are $2^{n-1}$
    subsets for each $i$. Prefer
    :func:`~pydvl.shapley.montecarlo.permutation_montecarlo_shapley`.

    Parallelization is done by splitting the set of indices across processes and
    computing the sum over subsets $S \subseteq N \setminus \{i\}$ separately.

    :param u: Utility object with model, data, and scoring function
    :param done: Stopping criterion for the computation.
    :param n_jobs: number of parallel jobs across which to distribute the
        computation. Each worker receives a chunk of
        :attr:`~pydvl.utils.dataset.Dataset.indices`
    :param config: Object configuring parallel computation, with cluster
        address, number of cpus, etc.
    :param progress: Whether to display progress bars for each job.
    :return: Object with the data values.
    """

    map_reduce_job: MapReduceJob[NDArray, ValuationResult] = MapReduceJob(
        u.data.indices,
        map_func=_combinatorial_montecarlo_shapley,
        reduce_func=lambda results: reduce(operator.add, results),
        map_kwargs=dict(u=u, done=done, progress=progress),
        n_jobs=n_jobs,
        config=config,
    )
    return map_reduce_job()


class OwenAlgorithm(Enum):
    Standard = "standard"
    Antithetic = "antithetic"


def _owen_sampling_shapley(
    indices: Sequence[int],
    u: Utility,
    method: OwenAlgorithm,
    n_iterations: int,
    max_q: int,
    *,
    progress: bool = False,
    job_id: int = 1,
) -> ValuationResult:
    r"""This is the algorithm as detailed in the paper: to compute the outer
    integral over q ∈ [0,1], use uniformly distributed points for evaluation
    of the integrand. For the integrand (the expected marginal utility over the
    power set), use Monte Carlo.

    .. todo::
        We might want to try better quadrature rules like Gauss or Rombert or
        use Monte Carlo for the double integral.

    :param indices: Indices to compute the value for
    :param u: Utility object with model, data, and scoring function
    :param method: Either :attr:`~OwenAlgorithm.Full` for $q \in [0,1]$ or
        :attr:`~OwenAlgorithm.Halved` for $q \in [0,0.5]$ and correlated samples
    :param n_iterations: Number of subsets to sample to estimate the integrand
    :param max_q: number of subdivisions for the integration over $q$
    :param progress: Whether to display progress bars for each job
    :param job_id: For positioning of the progress bar
    :return: Object with the data values, errors.
    """
    values = np.zeros(len(u.data))

    q_stop = {OwenAlgorithm.Standard: 1.0, OwenAlgorithm.Antithetic: 0.5}
    q_steps = np.linspace(start=0, stop=q_stop[method], num=max_q)

    index_set = set(indices)
    for i in maybe_progress(indices, progress, position=job_id):
        e = np.zeros(max_q)
        subset = np.array(list(index_set.difference({i})))
        for j, q in enumerate(q_steps):
            for s in random_powerset(subset, n_samples=n_iterations, q=q):
                marginal = u({i}.union(s)) - u(s)
                if method == OwenAlgorithm.Antithetic and q != 0.5:
                    s_complement = index_set.difference(s)
                    marginal += u({i}.union(s_complement)) - u(s_complement)
                e[j] += marginal
        e /= n_iterations
        # values[i] = e.mean()
        # Trapezoidal rule
        values[i] = (e[:-1] + e[1:]).sum() / (2 * max_q)

    return ValuationResult(
        algorithm="owen_sampling_shapley_" + str(method), values=values
    )


def owen_sampling_shapley(
    u: Utility,
    n_iterations: int,
    max_q: int,
    *,
    method: OwenAlgorithm = OwenAlgorithm.Standard,
    n_jobs: int = 1,
    config: ParallelConfig = ParallelConfig(),
    progress: bool = False,
) -> ValuationResult:
    r"""Owen sampling of Shapley values as described in
    :footcite:t:`okhrati_multilinear_2021`.

    .. warning::
       Antithetic sampling is unstable and not properly tested

    This function computes a Monte Carlo approximation to

    $$v_u(i) = \int_0^1 \mathbb{E}_{S \sim P_q(D_{\backslash \{i\}})}
    [u(S \cup \{i\}) - u(S)]$$

    using one of two methods. The first one, selected with the argument ``mode =
    OwenAlgorithm.Standard``, approximates the integral with:

    $$\hat{v}_u(i) = \frac{1}{Q M} \sum_{j=0}^Q \sum_{m=1}^M [u(S^{(q_j)}_m
    \cup \{i\}) - u(S^{(q_j)}_m)],$$

    where $q_j = \frac{j}{Q} \in [0,1]$ and the sets $S^{(q_j)}$ are such that a
    sample $x \in S^{(q_j)}$ if a draw from a $Ber(q_j)$ distribution is 1.

    The second method, selected with the argument ``mode =
    OwenAlgorithm.Anthithetic``,
    uses correlated samples in the inner sum to reduce the variance:

    $$\hat{v}_u(i) = \frac{1}{Q M} \sum_{j=0}^Q \sum_{m=1}^M [u(S^{(q_j)}_m
    \cup \{i\}) - u(S^{(q_j)}_m) + u((S^{(q_j)}_m)^c \cup \{i\}) - u((S^{(
    q_j)}_m)^c)],$$

    where now $q_j = \frac{j}{2Q} \in [0,\frac{1}{2}]$, and $S^c$ is the
    complement of $S$.

    :param u: :class:`~pydvl.utils.utility.Utility` object holding data, model
        and scoring function.
    :param n_iterations: Numer of sets to sample for each value of q
    :param max_q: Number of subdivisions for q ∈ [0,1] (the element sampling
        probability) used to approximate the outer integral.
    :param method: Selects the algorithm to use, see the description. Either
        :attr:`~OwenAlgorithm.Full` for $q \in [0,1]$ or
        :attr:`~OwenAlgorithm.Halved` for $q \in [0,0.5]$ and correlated samples
    :param n_jobs: Number of parallel jobs to use. Each worker receives a chunk
        of the total of `max_q` values for q.
    :param config: Object configuring parallel computation, with cluster
        address, number of cpus, etc.
    :param progress: Whether to display progress bars for each job.
    :return: Object with the data values.

    .. versionadded:: 0.3.0

    """
    if n_jobs > 1:
        raise NotImplementedError("Parallel Owen sampling not implemented yet")

    if OwenAlgorithm(method) == OwenAlgorithm.Antithetic:
        warn("Owen antithetic sampling not tested and probably bogus")

    map_reduce_job: MapReduceJob[NDArray, ValuationResult] = MapReduceJob(
        u.data.indices,
        map_func=_owen_sampling_shapley,
        reduce_func=lambda results: reduce(operator.add, results),
        map_kwargs=dict(
            u=u,
            method=OwenAlgorithm(method),
            n_iterations=n_iterations,
            max_q=max_q,
            progress=progress,
        ),
        n_jobs=n_jobs,
        config=config,
    )

    return map_reduce_job()
