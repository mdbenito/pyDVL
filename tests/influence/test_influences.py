import itertools
from collections import OrderedDict
from typing import List, Tuple

import numpy as np
import pytest
import torch.nn.functional as F

from valuation.influence.naive import InfluenceTypes, influences
from valuation.models.linear_regression_torch_model import LRTorchModel
from valuation.models.pytorch_model import PyTorchOptimizer, PyTorchSupervisedModel
from valuation.utils import (
    Dataset,
    linear_regression_analytical_derivative_d2_theta,
    linear_regression_analytical_derivative_d_theta,
    linear_regression_analytical_derivative_d_x_d_theta,
    upweighting_influences_linear_regression_analytical,
)

test_cases = OrderedDict()
test_cases["lr_test_single_thread"] = (LRTorchModel, 1)
test_cases["lr_test_multi_thread"] = (LRTorchModel, 2)


@pytest.mark.parametrize(
    "torch_model_factory,n_jobs", test_cases.values(), ids=test_cases.keys()
)
def test_upweighting_influences_valid_output(
    linear_dataset: Dataset, torch_model_factory, n_jobs: int
):
    n_in_features = linear_dataset.x_test.shape[1]
    model = PyTorchSupervisedModel(
        model=torch_model_factory((n_in_features, 1)),
        objective=F.mse_loss,
        num_epochs=10,
        batch_size=16,
        optimizer=PyTorchOptimizer.ADAM,
        optimizer_kwargs={"lr": 0.05},
    )
    model.fit(linear_dataset.x_train, linear_dataset.y_train)
    influence_values = influences(model, linear_dataset, progress=True, n_jobs=n_jobs)

    assert np.all(np.logical_not(np.isnan(influence_values)))
    assert influence_values.shape == (
        len(linear_dataset.x_test),
        len(linear_dataset.x_train),
    )


@pytest.mark.parametrize(
    "torch_model_factory,n_jobs", test_cases.values(), ids=test_cases.keys()
)
def test_perturbation_influences_valid_output(
    linear_dataset: Dataset, torch_model_factory, n_jobs: int
):
    n_in_features = linear_dataset.x_test.shape[1]
    model = PyTorchSupervisedModel(
        model=torch_model_factory((n_in_features, 1)),
        objective=F.mse_loss,
        num_epochs=10,
        batch_size=16,
        optimizer=PyTorchOptimizer.ADAM,
        optimizer_kwargs={"lr": 0.05},
    )
    model.fit(linear_dataset.x_train, linear_dataset.y_train)
    influence_values = influences(
        model,
        linear_dataset,
        progress=True,
        n_jobs=n_jobs,
        influence_type=InfluenceTypes.Perturbation,
    )

    assert np.all(np.logical_not(np.isnan(influence_values)))
    assert influence_values.shape == (
        len(linear_dataset.x_test),
        len(linear_dataset.x_train),
        n_in_features,
    )


class InfluenceTestSettings:
    DATA_OUTPUT_NOISE: float = 0.01
    ACCEPTABLE_ABS_TOL_INFLUENCE: float = 1e-5

    INFLUENCE_TEST_CONDITION_NUMBERS: List[int] = [5]
    INFLUENCE_TEST_SET_SIZE: List[int] = [10, 20]
    INFLUENCE_TRAINING_SET_SIZE: List[int] = [500, 1000]
    INFLUENCE_DIMENSIONS: List[Tuple[int, int]] = [
        (10, 10),
        (20, 10),
        (20, 20),
    ]


test_cases = list(
    itertools.product(
        InfluenceTestSettings.INFLUENCE_TRAINING_SET_SIZE,
        InfluenceTestSettings.INFLUENCE_TEST_SET_SIZE,
        InfluenceTestSettings.INFLUENCE_DIMENSIONS,
        InfluenceTestSettings.INFLUENCE_TEST_CONDITION_NUMBERS,
    )
)


def lmb_test_case_to_str(packed_i_test_case):
    i, test_case = packed_i_test_case
    return f"Problem #{i} of dimension {test_case[2]} with train size {test_case[0]}, test size {test_case[1]} and condition number {test_case[3]}"


test_case_ids = list(map(lmb_test_case_to_str, zip(range(len(test_cases)), test_cases)))


@pytest.mark.parametrize(
    "train_set_size,test_set_size,problem_dimension,condition_number",
    test_cases,
    ids=test_case_ids,
)
def test_upweighting_influences_lr_analytical(
    train_set_size: int,
    test_set_size: int,
    condition_number: float,
    linear_model: Tuple[np.ndarray, np.ndarray],
):

    # some settings
    A, b = linear_model
    o_d, i_d = tuple(A.shape)

    # generate datasets
    data_model = lambda x: np.random.normal(
        x @ A.T + b, InfluenceTestSettings.DATA_OUTPUT_NOISE
    )
    train_x = np.random.uniform(size=[train_set_size, i_d])
    train_y = data_model(train_x)
    test_x = np.random.uniform(size=[test_set_size, i_d])
    test_y = data_model(test_x)

    model = PyTorchSupervisedModel(
        model=LRTorchModel(dim=tuple(A.shape), init=linear_model),
        objective=F.mse_loss,
        num_epochs=1000,
        batch_size=32,
        optimizer=PyTorchOptimizer.ADAM_W,
        optimizer_kwargs={"lr": 0.02},
    )

    influence_values_analytical = (
        2
        * upweighting_influences_linear_regression_analytical(
            A, b, test_x, test_y, train_x, train_y
        )
    )

    class Object(object):
        pass

    dataset = Object()
    dataset.x_train = train_x
    dataset.y_train = train_y
    dataset.x_test = test_x
    dataset.y_test = test_y
    influence_values = influences(
        model, dataset, progress=True, n_jobs=1, influence_type=InfluenceTypes.Up
    )
    influences_max_abs_diff = np.max(
        np.abs(influence_values - influence_values_analytical)
    )
    assert (
        influences_max_abs_diff < InfluenceTestSettings.ACCEPTABLE_ABS_TOL_INFLUENCE
    ), "Upweighting influence values were wrong."


@pytest.mark.parametrize(
    "train_set_size,test_set_size,problem_dimension,condition_number",
    test_cases,
    ids=test_case_ids,
)
def test_perturbation_influences_lr_analytical(
    train_set_size: int,
    test_set_size: int,
    problem_dimension: int,
    condition_number: float,
    linear_model: Tuple[np.ndarray, np.ndarray],
):

    # some settings
    A, b = linear_model
    output_dimension, input_dimension = tuple(A.shape)

    # generate datasets
    data_model = lambda x: np.random.normal(
        x @ A.T + b, InfluenceTestSettings.DATA_OUTPUT_NOISE
    )
    train_x = np.random.uniform(size=[train_set_size, input_dimension])
    train_y = data_model(train_x)
    test_x = np.random.uniform(size=[test_set_size, input_dimension])
    test_y = data_model(test_x)

    model = PyTorchSupervisedModel(
        model=LRTorchModel(dim=(output_dimension, input_dimension), init=(A, b)),
        objective=F.mse_loss,
        num_epochs=1000,
        batch_size=32,
        optimizer=PyTorchOptimizer.ADAM_W,
        optimizer_kwargs={"lr": 0.02},
    )

    # check grads
    test_grads_analytical = linear_regression_analytical_derivative_d_theta(
        A, b, test_x, test_y
    )
    train_second_deriv_analytical = linear_regression_analytical_derivative_d_x_d_theta(
        A, b, train_x, train_y
    )

    hessian_analytical = linear_regression_analytical_derivative_d2_theta(
        A, b, train_x, train_y
    )
    s_test_analytical = np.linalg.solve(hessian_analytical, test_grads_analytical.T).T
    influence_values_analytical = -2 * np.einsum(
        "ia,jab->ijb", s_test_analytical, train_second_deriv_analytical
    )

    class Object(object):
        pass

    dataset = Object()
    dataset.x_train = train_x
    dataset.y_train = train_y
    dataset.x_test = test_x
    dataset.y_test = test_y
    influence_values = influences(
        model,
        dataset,
        progress=True,
        n_jobs=1,
        influence_type=InfluenceTypes.Perturbation,
    )
    influences_max_abs_diff = np.max(
        np.abs(influence_values - influence_values_analytical)
    )
    assert (
        influences_max_abs_diff < InfluenceTestSettings.ACCEPTABLE_ABS_TOL_INFLUENCE
    ), "Perturbation influence values were wrong."
