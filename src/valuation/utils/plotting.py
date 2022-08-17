from typing import TYPE_CHECKING, Dict, Optional, Tuple

import matplotlib as mpl
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

if TYPE_CHECKING:
    try:
        from numpy.typing import NDArray
    except ImportError:
        from numpy import ndarray as NDArray


def plot_shapley(
    dval_df: pd.DataFrame,
    figsize: Tuple[int, int] = None,
    title: str = None,
    xlabel: str = None,
    ylabel: str = None,
):
    """Plots the shapley values, as returned from shapley.get_shapley_values.

    :param dval_df: dataframe with the shapley values
    :param figsize: tuple with figure size
    :param title: string, title of the plot
    :param xlabel: string, x label of the plot
    :param ylabel: string, y label of the plot
    """
    fig = plt.figure(figsize=figsize)
    plt.errorbar(
        x=dval_df["data_key"],
        y=dval_df["shapley_dval"],
        yerr=dval_df["dval_std"],
        fmt="o",
    )
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.xticks(rotation=45)
    return fig


def plot_datasets(
    datasets: Dict[str, Tuple["NDArray", "NDArray"]],
    x_min: Optional["NDArray"] = None,
    x_max: Optional["NDArray"] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    vline: Optional[float] = None,
    cmap_name: Optional[str] = None,
    line: Optional["NDArray"] = None,
    suptitle: Optional[str] = None,
    s: Optional[float] = None,
):
    """
    Plots a dictionary of 2-dimensional datasets to either a continuous regression value or a discrete class label.
    In the former case the plasma color map is selected and in the later the tab10 color map is chosen.
    :param datasets: A dictionary mapping dataset names to a tuple of (features, target_variable). Note that the
    features have size [Nx2] and the target_variable [N].
    :param x_min: Set to define the minimum boundaries of the plot.
    :param x_max: Set to define the maximum boundaries of the plot.
    :param line: Optional, line of shape [Mx2], where each row is a point of the 2-dimensional line.
    :param s: The thickness of the points to plot.
    """

    num_datasets = len(datasets)
    fig = plt.figure(figsize=(6 * num_datasets, 4), constrained_layout=True)
    spec = fig.add_gridspec(20, num_datasets)
    ax = [fig.add_subplot(spec[:-1, i]) for i in range(num_datasets)]
    ax.append(fig.add_subplot(spec[-1, :]))

    discrete_keys = [
        key for key, dataset in datasets.items() if dataset[1].dtype == int
    ]
    if 0 < len(discrete_keys) < len(datasets):
        "You can only plot either discrete or only continuous plots."

    is_discrete = len(discrete_keys) == len(datasets)
    continuous_keys = [key for key in datasets.keys() if key not in discrete_keys]

    v_min = (
        None if is_discrete else min([np.min(datasets[k][1]) for k in continuous_keys])
    )
    v_max = (
        None if is_discrete else max([np.max(datasets[k][1]) for k in continuous_keys])
    )

    num_classes = None
    if is_discrete:
        if cmap_name is None:
            cmap_name = "Set1"
        cmap = plt.get_cmap(cmap_name)
        all_y = np.concatenate(tuple([v[1] for _, v in datasets.items()]), axis=0)
        unique_y = np.sort(np.unique(all_y))
        num_classes = len(unique_y)
        handles = [
            mpatches.Patch(color=cmap(i), label=y) for i, y in enumerate(unique_y)
        ]
    else:
        if cmap_name is None:
            cmap_name = "plasma"
        cmap = plt.get_cmap(cmap_name)

    for i, dataset_name in enumerate(datasets.keys()):
        x, y = datasets[dataset_name]
        if x.shape[1] != 2:
            raise AttributeError("The maximum number of allowede features is 2.")

        ax[i].set_title(dataset_name)
        if x_min is not None:
            ax[i].set_xlim(x_min[0], x_max[0])  # type: ignore
        if x_max is not None:
            ax[i].set_ylim(x_min[1], x_max[1])  # type: ignore

        if line is not None:
            ax[i].plot(line[:, 0], line[:, 1], color="black")

        ax[i].scatter(x[:, 0], x[:, 1], c=cmap(y), s=s, edgecolors="black")

        if xlabel is not None:
            ax[i].set_xlabel(xlabel)
        if ylabel is not None:
            ax[i].set_ylabel(ylabel)

        if vline is not None:
            ax[i].axvline(vline, color="black", linestyle="--")

    if is_discrete:
        ax[-1].legend(handles=handles, loc="center", ncol=num_classes)
        ax[-1].axis("off")
    else:
        norm = mpl.colors.Normalize(vmin=v_min, vmax=v_max)
        cb1 = mpl.colorbar.ColorbarBase(
            ax[-1], cmap=cmap, norm=norm, orientation="horizontal"
        )
        cb1.set_label("Influence values")

    if suptitle is not None:
        plt.suptitle(suptitle)

    plt.show()