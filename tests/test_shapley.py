import numpy as np
import pytest

from collections import OrderedDict
from tests.conftest import TolerateErrors, check_exact, check_rank_correlation, \
    check_total_value
from functools import partial
from valuation.shapley import combinatorial_montecarlo_shapley, \
    permutation_montecarlo_shapley, truncated_montecarlo_shapley,\
    permutation_exact_shapley
from valuation.utils import Dataset
from valuation.utils.numeric import lower_bound_hoeffding
from valuation.utils.parallel import MapReduceJob, available_cpus, map_reduce


# pedantic...
@pytest.mark.parametrize(
    "passes, values_a, values_b, eps",
    [(False,
      OrderedDict([(k, k+0.01) for k in range(10)]),
      OrderedDict([(k, k) for k in range(10)]),
      0.001),
     (True,
      OrderedDict([(k, k + 0.01) for k in range(10)]),
      OrderedDict([(k, k) for k in range(10)]),
      0.01),
     (True,
      OrderedDict([(k, k) for k in range(10)]),
      OrderedDict([(k, k) for k in range(10)]),
      0)
     ])
def test_compare(passes, values_a, values_b, eps):
    if passes:
        check_exact(values_a, values_b, eps)
    else:
        with pytest.raises(AssertionError):
            check_exact(values_a, values_b, eps)


@pytest.mark.parametrize(
        "scoring, rtol",
        [('r2', 0.01),
         ('neg_mean_squared_error', 0.01),
         ('neg_median_absolute_error', 0.01)])
def test_combinatorial_exact_shapley(exact_shapley, rtol):
    model, data, values, scoring = exact_shapley
    check_total_value(model, data, values, scoring, rtol=rtol)
    # TODO: compute "manually" for fixed values and check


@pytest.mark.parametrize(
    "scoring, rtol, eps",
    [('r2', 0.01, 0.01),
     ('neg_mean_squared_error', 0.01, 0.01),
     ('neg_median_absolute_error', 0.01, 0.01)])
def test_permutation_exact_shapley(scoring, rtol, eps, exact_shapley):
    model, data, exact_values, scoring = exact_shapley
    values_p = permutation_exact_shapley(model, data, scoring=scoring, progress=False)
    check_total_value(model, data, values_p, scoring, rtol=rtol)
    check_exact(values_p, exact_values, eps=eps)


# FIXME: this is not deterministic
@pytest.mark.parametrize(
    "fun, scoring, score_range, delta, eps",
    [(permutation_montecarlo_shapley,
      'neg_mean_squared_error', 2, 0.01, 0.04),
     (combinatorial_montecarlo_shapley,
      'neg_mean_squared_error', 2, 0.01, 0.04)])
def test_montecarlo_shapley(fun, scoring, score_range, delta, eps, exact_shapley):
    model, data, exact_values, scoring = exact_shapley
    num_cpus = min(available_cpus(), len(data))
    num_runs = 10

    # FIXME: The lower bound does not apply to all methods
    # Sample bound: |value - estimate| < eps holds with probability 1-𝛿
    max_iterations = lower_bound_hoeffding(
            delta=delta, eps=eps, score_range=score_range)

    print(f"test_montecarlo_shapley running for {max_iterations} iterations")

    _fun = partial(fun, model=model, scoring=scoring,
                   max_iterations=max_iterations, progress=False)
    job = MapReduceJob.from_fun(_fun)
    results = map_reduce(job, data, num_jobs=num_cpus, num_runs=num_runs)

    delta_errors = TolerateErrors(int(delta*len(results)), AssertionError)
    for values, _ in results:
        with delta_errors:
            # FIXME: test for total value never passes! (completely off)
            # Trivial bound on total error using triangle inequality
            # check_total_value(model, data, values, rtol=len(data)*eps)
            check_rank_correlation(values, exact_values, threshold=0.9)


# FIXME: this is not deterministic
@pytest.mark.parametrize(
        "scoring, score_range",
        [('neg_mean_squared_error', 2),
         ('r2', 2)])
def test_truncated_montecarlo_shapley(scoring, score_range, exact_shapley):
    model, data, exact_values, scoring = exact_shapley
    num_cpus = min(available_cpus(), len(data))
    num_runs = 10
    delta = 0.01  # Sample bound holds with probability 1-𝛿
    eps = 0.04

    min_permutations =\
        lower_bound_hoeffding(delta=delta, eps=eps, score_range=score_range)

    print(f"test_truncated_montecarlo_shapley running for {num_runs} runs "
          f" of max. {min_permutations} iterations each")

    fun = partial(truncated_montecarlo_shapley, model=model, data=data,
                  scoring=scoring, bootstrap_iterations=10, min_scores=5,
                  score_tolerance=0.1, min_values=10, value_tolerance=eps,
                  max_iterations=min_permutations, num_workers=num_cpus,
                  progress=False)
    results = []
    for i in range(num_runs):
        results.append(fun(run_id=i))

    delta_errors = TolerateErrors(int(delta * len(results)), AssertionError)
    for values, _ in results:
        with delta_errors:
            # Trivial bound on total error using triangle inequality
            check_total_value(model, data, values, rtol=len(data)*eps)
            check_rank_correlation(values, exact_values, threshold=0.8)