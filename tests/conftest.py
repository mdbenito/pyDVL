import numpy as np
import pytest

from sklearn.linear_model import LinearRegression
from typing import OrderedDict, Type
from valuation.shapley import combinatorial_exact_shapley
from valuation.utils import Dataset, SupervisedModel
from valuation.utils.numeric import spearman, utility
from valuation.utils.types import Scorer


@pytest.fixture(scope="module")
def boston_dataset():
    from sklearn import datasets
    return Dataset.from_sklearn(datasets.load_boston())


@pytest.fixture(scope="module")
def linear_dataset():
    from sklearn.utils import Bunch
    a = 2
    b = 0
    x = np.arange(-1, 1, .15)
    y = np.random.normal(loc=a * x + b, scale=0.1)
    db = Bunch()
    db.data, db.target = x.reshape(-1, 1), y
    db.DESCR = f"y~N({a}*x + {b}, 1)"
    db.feature_names = ["x"]
    db.target_names = ["y"]
    return Dataset.from_sklearn(data=db, train_size=0.66)


@pytest.fixture()
def scoring():
    return 'r2'


@pytest.fixture()
def exact_shapley(linear_dataset, scoring):
    model = LinearRegression()
    values_c = combinatorial_exact_shapley(
            model, linear_dataset, scoring=scoring, progress=False)
    return model, linear_dataset, values_c, scoring


class TolerateErrors:
    def __init__(self, max_errors: int, exception_cls: Type[BaseException]):
        self.max_errors = max_errors
        self.Exception = exception_cls
        self.error_count = 0

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.error_count += 1
        if self.error_count > self.max_errors:
            raise self.Exception(
                f"Maximum number of {self.max_errors} error(s) reached")
        return True


def check_total_value(model: SupervisedModel,
                      data: Dataset,
                      values: OrderedDict,
                      scoring: Scorer = None,
                      rtol: float = 0.01):
    """ Checks absolute distance between total and added values.
     Shapley value is supposed to fulfill the total value axiom."""
    total_utility = utility(model, data, frozenset(data.indices), scoring)
    values = np.array(list(values.values()))
    # We use relative tolerances here because we don't have the range of the
    # scorer.
    assert np.isclose(values.sum(), total_utility, rtol=rtol)


def check_exact(values: OrderedDict, exact_values: OrderedDict, eps: float):
    """ Compares ranks and values. """

    k = list(values.keys())
    ek = list(exact_values.keys())

    assert np.all(k == ek)

    v = np.array(list(values.values()))
    ev = np.array(list(exact_values.values()))

    assert np.allclose(v, ev, atol=eps)


def check_rank_correlation(values: OrderedDict, exact_values: OrderedDict,
                           n: int = None, threshold: float = 0.9):
    # FIXME: estimate proper threshold for spearman
    if n is not None:
        raise NotImplementedError
    else:
        n = len(values)
    ranks = np.array(list(values.keys())[:n])
    ranks_exact = np.array(list(exact_values.keys())[:n])

    assert spearman(ranks, ranks_exact) >= threshold