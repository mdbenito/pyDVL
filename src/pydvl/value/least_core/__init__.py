"""
.. versionadded:: 0.4.0

This package holds all routines for the computation of Least Core data values.

Please refer to :ref:`data valuation` for an overview.

In addition to the standard interface via
:func:`~pydvl.value.least_core.compute_least_core_values`, because computing the
Least Core values requires the solution of a linear and a quadratic problem
*after* computing all the utility values, there is the possibility of performing
each step separately. This is useful when running multiple experiments: use
:func:`~pydvl.value.least_core.montecarlo.mclc_prepare_problem` to prepare a
list of problems to solve, then solve them in parallel with
:func:`~pydvl.value.least_core.common.lc_solve_problems`.

"""
from enum import Enum
from typing import Optional

from ...utils import Utility
from pydvl.value.results import ValuationResult
from .montecarlo import *
from .naive import *


class LeastCoreMode(Enum):
    MonteCarlo = "montecarlo"
    Exact = "exact"


def compute_least_core_values(
    u: Utility,
    *,
    n_jobs: int = 1,
    n_iterations: Optional[int] = None,
    mode: LeastCoreMode = LeastCoreMode.MonteCarlo,
    **kwargs,
) -> ValuationResult:
    """Umbrella method to compute Least Core values with any of the available
    algorithms.

    See :ref:`data valuation` for an overview.

    The following algorithms are available. Note that the exact method can only
    work with very small datasets and is thus intended only for testing.

    - ``exact``: uses the complete powerset of the training set for the constraints
      :func:`~pydvl.value.shapley.naive.combinatorial_exact_shapley`.
    - ``montecarlo``:  uses the approximate Monte Carlo Least Core algorithm.
      Implemented in :func:`~pydvl.value.least_core.montecarlo.montecarlo_least_core`.


    .. versionadded:: 0.4.1
    """
    progress: bool = kwargs.pop("progress", False)

    if mode == LeastCoreMode.MonteCarlo:
        # TODO fix progress showing and maybe_progress in remote case
        progress = False
        if n_iterations is None:
            raise ValueError("n_iterations cannot be None for Monte Carlo Least Core")
        return montecarlo_least_core(
            u=u,
            n_iterations=n_iterations,
            n_jobs=n_jobs,
            progress=progress,
            **kwargs,
        )
    elif mode == LeastCoreMode.Exact:
        return exact_least_core(u=u, n_jobs=n_jobs, progress=progress, **kwargs)

    raise ValueError(f"Invalid value encountered in {mode=}")
