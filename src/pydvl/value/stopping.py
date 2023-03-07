"""
Stopping criteria for value computations.

This module provides a basic set of stopping criteria, like :class:`MaxUpdates`,
:class:`MaxTime`, or :class:`HistoryDeviation` among others. These can behave in
different ways depending on the context. For example, :class:`MaxUpdates` limits
the number of updates to values, which depending on the algorithm may mean a
different number of utility evaluations or imply other computations like solving
a linear or quadratic program.

.. rubric:: Creating stopping criteria

The easiest way is to declare a function implementing the interface
:data:`StoppingCriterionCallable` and wrap it with :func:`make_criterion`. This
creates a :class:`StoppingCriterion` object that can be composed with other
stopping criteria.

Alternatively, and in particular if reporting of completion is required, one can
inherit from this class and implement the abstract methods
:meth:`~pydvl.value.stopping.StoppingCriterion._check` and
:meth:`~pydvl.value.stopping.StoppingCriterion.completion`.

.. rubric:: Composing stopping criteria

Objects of type :class:`StoppingCriterion` can be composed with the binary
operators ``&`` (*and*), and ``|`` (*or*), following the truth tables of
:class:`~pydvl.utils.status.Status`. The unary operator ``~`` (*not*) is also
supported.
"""

import abc
import logging
from time import time
from typing import Callable, Optional, Type

import numpy as np
from deprecation import deprecated
from numpy.typing import NDArray
from scipy.stats import norm

from pydvl.utils import Status
from pydvl.value import ValuationResult

__all__ = [
    "make_criterion",
    "AbsoluteStandardError",
    "StoppingCriterion",
    "StandardError",
    "MaxChecks",
    "MaxUpdates",
    "MinUpdates",
    "MaxTime",
    "HistoryDeviation",
]

logger = logging.getLogger(__name__)

StoppingCriterionCallable = Callable[[ValuationResult], Status]


class StoppingCriterion(abc.ABC):
    """A composable callable object to determine whether a computation
    must stop.

    A ``StoppingCriterion`` takes a :class:`~pydvl.value.result.ValuationResult`
    and returns a :class:`~pydvl.value.result.Status~. Objects of this type
    can be composed with the binary operators ``&`` (*and*), and ``|`` (*or*),
    following the truth tables of :class:`~pydvl.utils.status.Status`. The
    unary operator ``~`` (*not*) is also supported.

    :param modify_result: If ``True`` the status of the input
        :class:`~pydvl.value.result.ValuationResult` is modified in place after
        the call.
    """

    # A boolean array indicating whether the corresponding element has converged
    _converged: NDArray[np.bool_]

    def __init__(self, modify_result: bool = True):
        self.modify_result = modify_result
        self._converged = np.full(0, False)

    @abc.abstractmethod
    def _check(self, result: ValuationResult) -> Status:
        """Check whether the computation should stop."""
        ...

    @abc.abstractmethod
    def completion(self) -> float:
        """Returns a value between 0 and 1 indicating the completion of the
        computation.
        """
        ...

    def converged(self) -> NDArray[np.bool_]:
        """Returns a boolean array indicating whether the values have converged
        for each data point.

        Inheriting classes must set the ``_converged`` attribute in their
        :meth:`_check`.
        """
        return self._converged

    @property
    def name(self):
        return type(self).__name__

    def __call__(self, result: ValuationResult) -> Status:
        if len(result) == 0:
            logger.warning(
                "At least one iteration finished but no results where generated. "
                "Please check that your scorer and utility return valid numbers."
            )
        status = self._check(result)
        if self.modify_result:  # FIXME: this is not nice
            result._status = status
        return status

    def __and__(self, other: "StoppingCriterion") -> "StoppingCriterion":
        return make_criterion(
            fun=lambda result: self._check(result) & other._check(result),
            completion=lambda: min(self.completion(), other.completion()),
            name=f"Composite StoppingCriterion: {self.name} AND {other.name}",
        )(modify_result=self.modify_result or other.modify_result)

    def __or__(self, other: "StoppingCriterion") -> "StoppingCriterion":
        return make_criterion(
            fun=lambda result: self._check(result) | other._check(result),
            completion=lambda: max(self.completion(), other.completion()),
            name=f"Composite StoppingCriterion: {self.name} OR {other.name}",
        )(modify_result=self.modify_result or other.modify_result)

    def __invert__(self) -> "StoppingCriterion":
        return make_criterion(
            fun=lambda result: ~self._check(result),
            completion=lambda: 1 - self.completion(),
            name=f"Composite StoppingCriterion: NOT {self.name}",
        )(modify_result=self.modify_result)


def make_criterion(
    fun: StoppingCriterionCallable,
    completion: Callable[[], float] = None,
    name: str = None,
) -> Type[StoppingCriterion]:
    """Create a new :class:`StoppingCriterion` from a function.
    Use this to enable simpler functions to be composed with bitwise operators

    :param fun: The callable to wrap.
    :param completion: A callable that returns a value between 0 and 1.
    :param name: The name of the new criterion. If ``None``, the ``__name__`` of
        the function is used.
    :return: A new subclass of :class:`StoppingCriterion`.
    """

    class WrappedCriterion(StoppingCriterion):
        def __init__(self, modify_result: bool = True):
            super().__init__(modify_result=modify_result)
            self._name = name or fun.__name__

        def _check(self, result: ValuationResult) -> Status:
            return fun(result)

        def completion(self) -> float:
            return completion() if completion is not None else 0.0

        @property
        def name(self):
            return self._name

        def converged(self) -> NDArray[np.bool_]:
            raise NotImplementedError(
                "Cannot determine individual sample convergence from a function"
            )

    return WrappedCriterion


class AbsoluteStandardError(StoppingCriterion):
    r"""Determine convergence based on the standard error of the values.

    If $s_i$ is the standard error for datum $i$ and $v_i$ its value, then this
    criterion returns :attr:`~pydvl.utils.status.Status.Converged` if
    $s_i < \epsilon$ for all $i$ and a threshold value $\epsilon \gt 0$.

    :param threshold: A value is considered to have converged if the standard
        error is below this value. A way of choosing it is to pick some
        percentage of the range of the values. For Shapley values this is the
        difference between the maximum and minimum of the utility function (to
        see this substitute the maximum and minimum values of the utility into
        the marginal contribution formula).
    :param fraction: The fraction of values that must have converged for the
        criterion to return :attr:`~pydvl.utils.status.Status.Converged`.
    """

    def __init__(
        self, threshold: float, fraction: float = 1.0, modify_result: bool = True
    ):
        super().__init__(modify_result=modify_result)
        self.threshold = threshold
        self.fraction = fraction

    def _check(self, result: ValuationResult) -> Status:
        self._converged = result.stderr < self.threshold
        if np.mean(self._converged) >= self.fraction:
            return Status.Converged
        return Status.Pending

    def completion(self) -> float:
        if self._converged.size == 0:
            return 0.0
        return np.mean(self._converged).item()


@deprecated(
    deprecated_in="0.6.0",
    removed_in="0.7.0",
    details="This stopping criterion has been deprecated. "
    "Use AbsoluteStandardError instead",
)
class StandardError(AbsoluteStandardError):
    pass


class ConfidenceIntervalSeparation(StoppingCriterion):
    r"""Terminates if normal confidence intervals around maximally separated
    values do not overlap.

    .. note::
       This is a very ad-hoc way of picking a constant threshold for the
       standard errors of values, and as such, YMMV. For a threshold relative to
       the magnitude of the values, use :class:`RelativeStandardError`.

    Imagine that the $n$ values are distributed uniformly across the range $r$.
    The maximal separation between two values is $r / (n - 1)$. Place normal
    confidence intervals of level $\tilde{\alpha}$ around a value $v_{i}$:

    $$C_{i} := (v_{i} - z_{\tilde{\alpha} / 2}  \hat{s}_{i}, v_{i} + z_{\tilde{\alpha} / 2}  \hat{s}_{i}),$$

    where $\hat{s}_{i}$ is the estimate of the standard error for value
    $v_{i}$ and $z_{\tilde{\alpha} / 2}$ is the $1 - \tilde{\alpha} / 2$
    quantile of the standard normal distribution (i.e. $\approx 1.96$ for level
    0.95). For a fixed level $\tilde{\alpha}$, these intervals do not overlap
    iff $\hat{s}_{i} < \frac{r}{2 (n - 1) z_{\alpha / 2}}$.

    Now, because there are $n$ (independent) confidence intervals, we apply a
    simple Bonferroni-type correction: the probability that _all_ $n$ contain
    their respective values simultaneously is $\mathbb{P} (v_{i} \in C_{i},
    \forall i) = (1 - \tilde{\alpha})^n$, and we want this to be equal to $1 -
    \alpha$ for a given $\alpha$. Therefore we must pick $\alpha = 1-(1 -
    \tilde{\alpha})^{1 / n}$.

    The criterion returns :attr:`~pydvl.utils.status.Status.Converged` if $s_{i}
    < \frac{r}{2 (n - 1) z_{\alpha / 2}}$ for all $i$, where $\alpha = 1 -
    (1 - \tilde{\alpha})^{1 / \lceil \rho n \rceil}$, and $\rho \in (0, 1]$ is
    the fraction of values that must fulfill the criterion.

    :param alpha: The overall level of confidence desired.
    :param values_range: The maximum possible difference between two values.
        Because this is unknown, a good rule of thumb is twice the total utility.
    :param fraction: The fraction of values that must have converged for the
        criterion to return :attr:`~pydvl.utils.status.Status.Converged`.
    """

    def __init__(
        self,
        alpha: float,
        values_range: float,
        fraction: float = 1.0,
        modify_result: bool = True,
    ):
        super().__init__(modify_result=modify_result)
        self.level = lambda n: 1 - (1 - alpha) ** (1 / n)
        self.range = values_range
        self.fraction = fraction

    def _check(self, result: ValuationResult) -> Status:
        n = np.ceil(self.fraction * result.values.size)
        bound = self.range / (2 * (n - 1) * norm.ppf(1 - self.level(n) / 2))
        self._converged = np.abs(result.stderr) < bound
        if np.mean(self._converged) >= self.fraction:
            return Status.Converged
        return Status.Pending

    def completion(self) -> float:
        if self._converged.size == 0:
            return 0.0
        return np.mean(self._converged).item()


class MaxChecks(StoppingCriterion):
    """Terminate as soon as the number of checks exceeds the threshold.

    A "check" is one call to the criterion.

    :param n_checks: Threshold: if ``None``, no _check is performed,
        effectively creating a (never) stopping criterion that always returns
        ``Pending``.
    """

    def __init__(self, n_checks: Optional[int], modify_result: bool = True):
        super().__init__(modify_result=modify_result)
        if n_checks is not None and n_checks < 1:
            raise ValueError("n_iterations must be at least 1 or None")
        self.n_checks = n_checks
        self._count = 0

    def _check(self, result: ValuationResult) -> Status:
        if self.n_checks:
            self._count += 1
            if self._count > self.n_checks:
                return Status.Converged
        return Status.Pending

    def completion(self) -> float:
        if self.n_checks:
            return min(1.0, self._count / self.n_checks)
        return 0.0


class MaxUpdates(StoppingCriterion):
    """Terminate if any number of value updates exceeds or equals the given
    threshold.

    This checks the ``counts`` field of a
    :class:`~pydvl.value.result.ValuationResult`, i.e. the number of times that
    each index has been updated. For powerset samplers, the maximum of this
    number coincides with the maximum number of subsets sampled. For permutation
    samplers, it coincides with the number of permutations sampled.

    :param n_updates: Threshold: if ``None``, no _check is performed,
        effectively creating a (never) stopping criterion that always returns
        ``Pending``.
    """

    def __init__(self, n_updates: Optional[int], modify_result: bool = True):
        super().__init__(modify_result=modify_result)
        if n_updates is not None and n_updates < 1:
            raise ValueError("n_updates must be at least 1 or None")
        self.n_updates = n_updates
        self.last_max = 0

    def _check(self, result: ValuationResult) -> Status:
        if self.n_updates:
            self._converged = result.counts >= self.n_updates
            try:
                self.last_max = int(np.max(result.counts))
                if self.last_max >= self.n_updates:
                    return Status.Converged
            except ValueError:  # empty counts array. This should not happen
                pass
        return Status.Pending

    def completion(self) -> float:
        if self.n_updates:
            return self.last_max / self.n_updates
        return 0.0


class MinUpdates(StoppingCriterion):
    """Terminate as soon as all value updates exceed or equal the given threshold.

    This checks the ``counts`` field of a
    :class:`~pydvl.value.result.ValuationResult`, i.e. the number of times that
    each index has been updated. For powerset samplers, the minimum of this
    number is a lower bound for the number of subsets sampled. For
    permutation samplers, it lower-bounds the amount of permutations sampled.

    :param n_updates: Threshold: if ``None``, no _check is performed,
        effectively creating a (never) stopping criterion that always returns
        ``Pending``.
    """

    def __init__(self, n_updates: Optional[int], modify_result: bool = True):
        super().__init__(modify_result=modify_result)
        self.n_updates = n_updates
        self.last_min = 0

    def _check(self, result: ValuationResult) -> Status:
        if self.n_updates is not None:
            self._converged = result.counts >= self.n_updates
            try:
                self.last_min = int(np.min(result.counts))
                if self.last_min >= self.n_updates:
                    return Status.Converged
            except ValueError:  # empty counts array. This should not happen
                pass
        return Status.Pending

    def completion(self) -> float:
        if self.n_updates:
            return self.last_min / self.n_updates
        return 0.0


class MaxTime(StoppingCriterion):
    """Terminate if the computation time exceeds the given number of seconds.

    Checks the elapsed time since construction

    :param seconds: Threshold: The computation is terminated if the elapsed time
        between object construction and a _check exceeds this value. If ``None``,
        no _check is performed, effectively creating a (never) stopping criterion
        that always returns ``Pending``.
    """

    def __init__(self, seconds: Optional[float], modify_result: bool = True):
        super().__init__(modify_result=modify_result)
        self.max_seconds = seconds or np.inf
        if self.max_seconds <= 0:
            raise ValueError("Number of seconds for MaxTime must be positive or None")
        self.start = time()

    def _check(self, result: ValuationResult) -> Status:
        if self._converged is None:
            self._converged = np.full(result.values.shape, False)
        if time() > self.start + self.max_seconds:
            self._converged.fill(True)
            return Status.Converged
        return Status.Pending

    def completion(self) -> float:
        if self.max_seconds is None:
            return 0.0
        return (time() - self.start) / self.max_seconds


class HistoryDeviation(StoppingCriterion):
    r"""A simple check for relative distance to a previous step in the
    computation.

    The method used by :footcite:t:`ghorbani_data_2019` computes the relative
    distances between the current values $v_i^t$ and the values at the previous
    checkpoint $v_i^{t-\tau}$. If the sum is below a given threshold, the
    computation is terminated.

    $$\sum_{i=1}^n \frac{\left| v_i^t - v_i^{t-\tau} \right|}{v_i^t} <
    \epsilon.$$

    When the denominator is zero, the summand is set to the value of $v_i^{
    t-\tau}$.

    This implementation is slightly generalised to allow for different number of
    updates to individual indices, as happens with powerset samplers instead of
    permutations. Every subset of indices that is found to converge can be
    pinned to that state. Once all indices have converged the method has
    converged.

    .. warning::
       This criterion is meant for the reproduction of the results in the paper,
       but we do not recommend using it in practice.

    :param n_steps: Checkpoint values every so many updates and use these saved
        values to compare.
    :param rtol: Relative tolerance for convergence ($\epsilon$ in the formula).
    :param pin_converged: If ``True``, once an index has converged, it is pinned
    """

    _memory: NDArray[np.float_]

    def __init__(
        self,
        n_steps: int,
        rtol: float,
        pin_converged: bool = True,
        modify_result: bool = True,
    ):
        super().__init__(modify_result=modify_result)
        if n_steps < 1:
            raise ValueError("n_steps must be at least 1")
        if rtol <= 0 or rtol >= 1:
            raise ValueError("rtol must be in (0, 1)")

        self.n_steps = n_steps
        self.rtol = rtol
        self.update_op = np.logical_or if pin_converged else np.logical_and
        self._memory = None  # type: ignore

    def _check(self, r: ValuationResult) -> Status:
        if self._memory is None:
            self._memory = np.full((len(r.values), self.n_steps + 1), np.inf)
            self._converged = np.full(len(r), False)
            return Status.Pending

        # shift left: last column is the last set of values
        self._memory = np.concatenate(
            [self._memory[:, 1:], r.values.reshape(-1, 1)], axis=1
        )

        # Look at indices that have been updated more than n_steps times
        ii = np.where(r.counts > self.n_steps)
        if len(ii) > 0:
            curr = self._memory[:, -1]
            saved = self._memory[:, 0]
            diffs = np.abs(curr[ii] - saved[ii])
            quots = np.divide(diffs, curr[ii], out=diffs, where=curr[ii] != 0)
            # quots holds the quotients when the denominator is non-zero, and
            # the absolute difference, which is just the memory, otherwise.
            if np.mean(quots) < self.rtol:
                self._converged = self.update_op(
                    self._converged, r.counts > self.n_steps
                )  # type: ignore
                if np.all(self._converged):
                    return Status.Converged
        return Status.Pending

    def completion(self) -> float:
        return np.mean(self._converged or [0]).item()
