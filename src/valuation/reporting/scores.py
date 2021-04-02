import pandas as pd
import numpy as np
from functools import partial
from itertools import chain
from joblib import Parallel, delayed

from typing import List
from tqdm import tqdm, trange
from valuation import Regressor


def backward_elimination(model: Regressor,
                         x_train: pd.DataFrame,
                         y_train: pd.DataFrame,
                         x_test: pd.DataFrame,
                         y_test: pd.DataFrame,
                         indices: List[int],
                         job_id: int = 0) -> List[float]:
    """ Computes model score (on a test set) after incrementally removing
    points from the training data.

    :param model: duh
    :param x_train:
    :param y_train:
    :param x_test:
    :param y_test:
    :param indices: data points to remove in sequence. Retraining happens
                    after each removal.
    :param job_id: for progress bar positioning in parallel execution
    :return: List of scores
    """
    scores = []
    x, y = x_train, y_train
    for i in tqdm(indices[:-1], position=job_id,
                  desc=f"Backward elimination. Job {job_id}"):
        x = x[x.index != i]
        y = y[y.index != i]
        try:
            model.fit(x, y.values.ravel())
            scores.append(model.score(x_test, y_test.values.ravel()))
        except:
            scores.append(np.nan)
    return scores


def forward_selection(model: Regressor,
                      x_train: pd.DataFrame,
                      y_train: pd.DataFrame,
                      x_test: pd.DataFrame,
                      y_test: pd.DataFrame,
                      indices: List[int],
                      job_id: int = 0) -> List[float]:
    """ Computes model score (on a test set) incrementally adding
    points from training data.

    :param model: duh
    :param x_train:
    :param y_train:
    :param x_test:
    :param y_test:
    :param indices: data points to add in sequence. Retraining happens
                    after each addition
    :param job_id: for progress bar positioning in parallel execution
    :return: List of scores
    """
    scores = []
    for i in trange(len(indices), position=job_id,
                    desc=f"Forward selection. Job {job_id}"):
        # FIXME don't do a full index search on each iteration
        x = x_train[x_train.index.isin(indices[:i + 1])]
        y = y_train[y_train.index.isin(indices[:i + 1])]
        try:
            model.fit(x, y.values.ravel())
            scores.append(model.score(x_test, y_test.values.ravel()))
        except:
            scores.append(np.nan)
    return scores


def compute_fb_scores(values,
                      model: Regressor,
                      x_train: pd.DataFrame,
                      y_train: pd.DataFrame,
                      x_test: pd.DataFrame,
                      y_test: pd.DataFrame) -> dict:
    """ Compute scores during forward selection and backward elimination of
     points, in parallel.
    """
    num_runs = len(values)
    # TODO: report number of early stoppings
    bfun = partial(backward_elimination, model,
                   x_train, y_train, x_test, y_test)
    backward_scores_delayed = chain(
            (delayed(bfun)(indices=list(v.keys()), job_id=i)
             for i, v in enumerate(values)),
            (delayed(bfun)(indices=list(reversed(v.keys())), job_id=i)
             for i, v in enumerate(values, start=num_runs)),
            (delayed(bfun)(
                    indices=np.random.permutation(
                            list(values[i % num_runs].keys())),
                    job_id=i)
                    for i, _ in enumerate(values, start=2 * num_runs)))

    ffun = partial(forward_selection, model,
                   x_train, y_train, x_test, y_test)
    forward_scores_delayed = chain(
            (delayed(ffun)(indices=list(v.keys()), job_id=i)
             for i, v in enumerate(values, start=3 * num_runs)),
            (delayed(ffun)(indices=list(reversed(v.keys())), job_id=i)
             for i, v in enumerate(values, start=4 * num_runs)),
            (delayed(ffun)(
                    indices=np.random.permutation(
                            list(values[i % num_runs].keys())),
                    job_id=i)
                    for i, _ in enumerate(values, start=5 * num_runs)))

    all_scores = Parallel(n_jobs=6 * num_runs)(
            chain(backward_scores_delayed, forward_scores_delayed))

    results = {'all_values': values,
               # 'all_histories': all_histories,
               'backward_scores': all_scores[:num_runs],
               'backward_scores_reversed': all_scores[num_runs:2 * num_runs],
               'backward_random_scores': all_scores[2 * num_runs:3 * num_runs],
               'forward_scores': all_scores[3 * num_runs:4 * num_runs],
               'forward_scores_reversed': all_scores[4 * num_runs:5 * num_runs],
               'forward_random_scores': all_scores[5 * num_runs:6 * num_runs],
               'num_points': len(x_train)}

    return results
