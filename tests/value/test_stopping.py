import math
from time import sleep

import numpy as np
import pytest

from pydvl.utils import Status
from pydvl.value import ValuationResult
from pydvl.value.stopping import (
    AbsoluteStandardError,
    HistoryDeviation,
    MaxChecks,
    MaxTime,
    MaxUpdates,
    MinUpdates,
    StoppingCriterion,
    make_criterion,
)


def test_stopping_criterion():
    with pytest.raises(TypeError):
        StoppingCriterion()

    StoppingCriterion.__abstractmethods__ = set()
    done = StoppingCriterion()
    assert done.name == "StoppingCriterion"
    assert done.modify_result is True


def test_stopping_criterion_composition():
    StoppingCriterion.__abstractmethods__ = set()

    c = Status.Converged
    p = Status.Pending
    f = Status.Failed

    class C(StoppingCriterion):
        def _check(self, result: ValuationResult) -> Status:
            return c

    class P(StoppingCriterion):
        def _check(self, result: ValuationResult) -> Status:
            return p

    class F(StoppingCriterion):
        def _check(self, result: ValuationResult) -> Status:
            return f

    v = ValuationResult.empty()

    assert (~C())(v) == f
    assert (~P())(v) == c
    assert (~F())(v) == c

    assert (C() & C())(v) == c
    assert (P() | P())(v) == p

    assert (C() & P())(v) == (c & p)
    assert (C() | P())(v) == (c | p)

    assert (C() & C() & C())(v) == c
    assert (P() | P() | P())(v) == p

    assert (C() & P()).name == "Composite StoppingCriterion: C AND P"
    assert (C() | P()).name == "Composite StoppingCriterion: C OR P"
    assert (~C()).name == "Composite StoppingCriterion: NOT C"
    assert (~P()).name == "Composite StoppingCriterion: NOT P"


def test_make_criterion():
    def always_converged(result: ValuationResult) -> Status:
        return Status.Converged

    def always_pending(result: ValuationResult) -> Status:
        return Status.Pending

    def always_failed(result: ValuationResult) -> Status:
        return Status.Failed

    v = ValuationResult.empty()

    C = make_criterion(always_converged)
    P = make_criterion(always_pending)
    F = make_criterion(always_failed)

    assert C()(v) == Status.Converged
    assert P()(v) == Status.Pending
    assert F()(v) == Status.Failed

    assert C().name == "always_converged"
    assert P().name == "always_pending"
    assert F().name == "always_failed"

    assert (~C())(v) == Status.Failed
    assert (~P())(v) == Status.Converged
    assert (~F())(v) == Status.Converged

    assert (C() & C())(v) == Status.Converged
    assert (P() | P())(v) == Status.Pending
    assert (F() & F())(v) == Status.Failed
    assert (C() | F())(v) == Status.Converged


def test_minmax_updates():
    maxstop = MaxUpdates(10)
    assert maxstop.name == "MaxUpdates"
    v = ValuationResult.from_random(5)
    v._counts = np.zeros(5)
    assert maxstop(v) == Status.Pending
    v._counts += np.ones(5) * 9
    assert maxstop(v) == Status.Pending
    v._counts[0] += 1
    assert maxstop(v) == Status.Converged

    minstop = MinUpdates(10)
    assert minstop.name == "MinUpdates"
    v._counts = np.zeros(5)
    assert minstop(v) == Status.Pending
    v._counts += np.ones(5) * 9
    assert minstop(v) == Status.Pending
    v._counts[0] += 1
    assert minstop(v) == Status.Pending
    v._counts += np.ones(5)
    assert minstop(v) == Status.Converged


def test_max_time():
    v = ValuationResult.from_random(5)
    done = MaxTime(0.3)
    assert done(v) == Status.Pending
    sleep(0.3)
    assert done(v) == Status.Converged


@pytest.mark.parametrize("n_steps", [1, 42, 100])
@pytest.mark.parametrize("rtol", [0.01, 0.05])
def test_history_deviation(n_steps, rtol):
    """Values are equal and set to 1/t. The criterion will be fulfilled after
    t > (1+1/rtol) * n_steps iterations.
    """
    n = 5
    done = HistoryDeviation(n_steps=n_steps, rtol=rtol)
    threshold = math.ceil((1 + 1 / rtol) * n_steps)
    for t in range(1, threshold):
        v = ValuationResult(values=np.ones(n) / t, counts=np.full(n, t))
        assert done(v) == Status.Pending

    # FIXME: rounding errors mean that the threshold is not exactly as computed,
    #  but might be off by 1, so we check a couple of iterations to be sure that
    #  this works for any choice of n_steps and rtol
    status = Status.Pending
    for t in range(threshold, threshold + 2):
        v = ValuationResult(values=np.ones(n) / t, counts=np.full(n, t))
        status |= done(v)

    assert status == Status.Converged


def test_standard_error():
    """Test the AbsoluteStandardError stopping criterion."""
    eps = 0.1
    n = 5

    done = AbsoluteStandardError(threshold=eps)

    # Trivial case: no variance.
    v = ValuationResult(values=np.ones(n), variances=np.zeros(n))
    assert done(v)

    # Reduce the variance until the criterion is triggered.
    v = ValuationResult(values=np.ones(n), variances=np.ones(n))
    assert not done(v)

    # One value is being left out
    for _ in range(10):
        for idx in range(1, n):
            v.update(idx, 1)
    assert not done(v)

    # Update the final value
    for _ in range(10):
        v.update(0, 1)
    assert done(v)


def test_max_checks():
    """Test the MaxChecks stopping criterion."""
    v = ValuationResult.from_random(size=5)

    done = MaxChecks(None)
    for _ in range(10):
        assert not done(v)

    done = MaxChecks(5)
    for _ in range(5):
        assert not done(v)
    assert done(v)
