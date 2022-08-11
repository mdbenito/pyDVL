# mypy: ignore-errors
import pickle
from functools import partial

import click

from valuation.reporting.plots import shapley_results
from valuation.reporting.scores import compute_fb_scores
from valuation.shapley.montecarlo import truncated_montecarlo_shapley
from valuation.utils import Dataset
from valuation.utils.logging import logger


def maybe_init_task(task_name: str, clearml_config: dict, task_params: dict):
    """FIXME: will task.connect() work with copies of the params?"""
    global task
    if task is not None:
        task = Task.init(
            project_name=clearml_config["project_name"],
            task_name=task_name,
            output_uri=clearml_config["output_uri"],
        )
        from io import TextIOWrapper

        from click.utils import LazyFile

        # def convert(value) -> str:
        #     if isinstance(value, TextIOWrapper):
        #         return value.name
        #     if isinstance(value, LazyFile):
        #         return value.name
        #     return value
        cli_params = click.get_current_context().params
        # cli_params = {k: convert(v) for k, v in cli_params.items()}
        task.connect(cli_params, name="CLI parameters")
        for k, v in task_params.items():
            task.connect(v, name=k)


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option(
    "-v",
    "--verbosity",
    count=True,
    default=0,
    show_default=True,
    help="Verbosity level (0: ERROR, 1: WARNING, 2: INFO, 3: DEBUG)"
    ". Has no effect when using joblib.Parallel"
    " (e.g. in 'shapley'), use logging_config.ini instead.",
)
@click.option(
    "-x",
    "--track-experiment",
    is_flag=True,
    default=False,
    show_default=True,
    help="Whether to track the experiment using clearml",
)
def run(verbosity, track_experiment: bool):
    if track_experiment:
        global task
        task = True
    from logging import DEBUG, ERROR, INFO, WARNING

    levels = {0: ERROR, 1: WARNING, 2: INFO, 3: DEBUG}
    logger.setLevel(levels[verbosity])


@run.command(help="Compute DataShapley values")
# @click.option('-r', '--training-data',
#               type=click.Path(readable=True, dir_okay=False, exists=True),
#               required=True,
#               help="File with training data")
# @click.option('-t', '--test-data',
#               type=click.Path(readable=True, dir_okay=False, exists=True),
#               required=True,
#               help="File with test data")
# @click.option('-m', '--model',
#               type=click.Path(readable=True, dir_okay=False, exists=True),
#               required=True,
#               help='(Serialized) model to fit')
# @click.option('-c', '--config-file',
#               type=click.File('rt'),
#               required=False,
#               help='YAML file with configuration parameters')
@click.option(
    "-j",
    "--num-jobs",
    type=click.IntRange(1, None),
    default=160,
    show_default=True,
    help="Maximum number of parallel jobs to run",
)
@click.option(
    "-b",
    "--bootstrap-iterations",
    type=click.IntRange(1, None),
    default=200,
    show_default=True,
    help="Number of times to bootstrap computation of value for the " "full dataset",
)
@click.option(
    "-r",
    "--permutations-ratio",
    type=click.FloatRange(0.01, None),
    default=0.5,
    show_default=True,
    help="Number of MonteCarlo samples (factor of training set size)",
)
@click.option(
    "-w",
    "--value-tolerance",
    type=click.FloatRange(1e-12, None),
    default=1e-3,
    show_default=True,
    help="Tolerance for the convergence criterion of Shapley values",
)
@click.option(
    "-e",
    "--score-tolerance",
    type=click.FloatRange(1e-12, None),
    default=0.1,
    show_default=True,
    help="Tolerance for early stopping of single training runs. Stop "
    "after the score for subsets does not increase beyond this "
    "number times the stddev of global scores, estimated via "
    "bootstrapping",
)
@click.option(
    "-s",
    "--min-samples",
    type=click.IntRange(2, None),
    default=10,
    show_default=True,
    help="Use so many of the last samples for a permutation in order "
    "to compute the moving average of scores",
)
@click.option(
    "-p",
    "--min-values",
    type=click.IntRange(2, None),
    default=10,
    show_default=True,
    help="Complete at least these many value computations for every "
    "index. Also use as many of the last values for each sample "
    "index in order to compute the moving averages of values",
)
@click.option(
    "-n",
    "--num-runs",
    type=click.IntRange(1, None),
    default=10,
    show_default=True,
    help="Number of complete runs to perform for averaging of " "results",
)
def shapley(
    # training_data: click.Path,
    # test_data: click.Path,
    # model: click.Path,
    # config_file: click.File,
    num_jobs: int,
    permutations_ratio: float,
    bootstrap_iterations: int,
    value_tolerance: float,
    min_values: int,
    score_tolerance: float,
    min_scores: int,
    num_runs: int,
):
    # config = yaml.safe_load(config_file)

    from sklearn import datasets
    from sklearn.ensemble import GradientBoostingRegressor

    data = Dataset.from_sklearn(datasets.load_boston())
    # NOTE: should max_iterations be a fraction of the number of permutations?
    max_iterations = int(permutations_ratio * len(data))

    model = GradientBoostingRegressor()
    fun = partial(
        truncated_montecarlo_shapley,
        model=model,
        data=data,
        bootstrap_iterations=bootstrap_iterations,
        min_scores=min_scores,
        score_tolerance=score_tolerance,
        min_values=min_values,
        value_tolerance=value_tolerance,
        max_iterations=max_iterations,
        num_workers=num_jobs,
        worker_progress=True,
    )
    values, history = run_and_gather(fun, num_runs=num_runs, progress=False)
    scores = compute_fb_scores(model, data, values)
    print("Saving results...")
    filename = (
        f"save_{max_iterations}_iterations_{num_runs}_runs_"
        f"{score_tolerance}_score_{value_tolerance}_value"
    )
    # if task is not None:
    #     task.upload_artifact(name=filename, artifact_object=results)
    with open(f"{filename}.pkl", "wb") as fd:
        pickle.dump({"values": values, "history": history}, fd)
    scores.update({"max_iterations": max_iterations, "score_name": "$R^2$"})
    shapley_results(scores, filename=f"{filename}.png")


if __name__ == "__main__":
    run()
