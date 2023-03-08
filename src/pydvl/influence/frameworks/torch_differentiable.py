"""
Contains all parts of pyTorch based machine learning model.
"""
import logging
from typing import Any, Callable, List, Sequence, Tuple

import numpy as np
import torch
import torch.nn as nn
from torch import autograd
from torch.autograd import Variable

from ...utils import maybe_progress
from .twice_differentiable import TwiceDifferentiable

__all__ = [
    "TorchTwiceDifferentiable",
]
logger = logging.getLogger(__name__)


def flatten_gradient(grad):
    """
    Simple function to flatten a pyTorch gradient for use in subsequent calculation
    """
    return torch.cat([el.reshape(-1) for el in grad])


def solve_linear(matrix: torch.Tensor, b: torch.Tensor):
    """Computes the solution of a square system of linear equations"""
    return torch.linalg.solve(matrix, b)


def as_tensor(a: Any, ensure=True, **kwargs):
    """Converts an array into a torch tensor"""
    if ensure and not isinstance(a, torch.Tensor):
        logger.warning("Converting tensor to type torch.Tensor.")
    return torch.as_tensor(a, **kwargs)


def stack_tensors(a: Sequence[torch.Tensor], **kwargs):
    """Stacks a sequence of tensors into a single torch tensor"""
    return torch.stack(a, **kwargs)


def einsum(equation, *operands):
    """Sums the product of the elements of the input :attr:`operands` along dimensions specified using a notation
    based on the Einstein summation convention.
    """
    return torch.einsum(equation, *operands)


def identity_tensor(dim: int):
    return torch.eye(dim, dim)


def mvp(
    grad_xy: torch.Tensor,
    v: torch.Tensor,
    backprop_on: torch.Tensor,
    progress: bool = False,
) -> torch.Tensor:
    """
    Calculates second order derivative of the model along directions v.
    This second order derivative can be selected through the backprop_on argument.

    :param grad_xy: an array [P] holding the gradients of the model
        parameters wrt input $x$ and labels $y$, where P is the number of
        parameters of the model. It is typically obtained through
        self.grad.
    :param v: An array ([DxP] or even one dimensional [D]) which
        multiplies the matrix, where D is the number of directions.
    :param progress: True, iff progress shall be printed.
    :param backprop_on: tensor used in the second backpropagation (the first
        one is along $x$ and $y$ as defined via grad_xy).
    :returns: A matrix representing the implicit matrix vector product
        of the model along the given directions. Output shape is [DxP] if
        backprop_on is None, otherwise [DxM], with M the number of elements
        of backprop_on.
    """
    v = as_tensor(v, ensure=False)
    if v.ndim == 1:
        v = v.unsqueeze(0)

    z = (grad_xy * Variable(v)).sum(dim=1)

    mvp = []
    for i in maybe_progress(range(len(z)), progress, desc="MVP"):
        mvp.append(
            flatten_gradient(autograd.grad(z[i], backprop_on, retain_graph=True))
        )
    mvp = torch.stack([grad.contiguous().view(-1) for grad in mvp])
    return mvp.detach()  # type: ignore


class TorchTwiceDifferentiable(TwiceDifferentiable[torch.Tensor, nn.Module]):
    """
    Calculates second-derivative of a model wrt. a given loss
    """

    def __init__(
        self,
        model: nn.Module,
        loss: Callable[[torch.Tensor, torch.Tensor], torch.Tensor],
    ):
        """
        :param model: A (differentiable) function.
        :param loss: Loss function $L(f(x), y)$ maps a prediction and a target to a single value.
        """
        if model.training:
            logger.warning(
                "Passed model not in evaluation mode. This can create several issues in influence "
                "computation, e.g. due to batch normalization. Please call model.eval() before "
                "computing influences."
            )
        self.model = model
        self.loss = loss

    def parameters(self) -> List[torch.Tensor]:
        """Returns all the model parameters that require differentiating"""
        return [
            param for param in self.model.parameters() if param.requires_grad == True
        ]

    def num_params(self) -> int:
        """
        Get number of parameters of model f.
        :returns: Number of parameters as integer.
        """
        return sum([np.prod(p.size()) for p in self.parameters()])

    def split_grad(
        self,
        x: torch.Tensor,
        y: torch.Tensor,
        progress: bool = False,
    ) -> torch.Tensor:
        """
        Calculates gradient of model parameters wrt each $x[i]$ and $y[i]$ and then
        returns a array of size [N, P] with N number of points (length of x and y) and P
        number of parameters of the model.
        :param x: An array [NxD] representing the features $x_i$.
        :param y: An array [NxK] representing the predicted target values $y_i$.
        :param progress: True, iff progress shall be printed.
        :returns: An array [NxP] representing the gradients with respect to
        all parameters of the model.
        """
        x = as_tensor(x).unsqueeze(1)
        y = as_tensor(y)

        params = [
            param for param in self.model.parameters() if param.requires_grad == True
        ]

        grads = []
        for i in maybe_progress(range(len(x)), progress, desc="Split Gradient"):
            grads.append(
                flatten_gradient(
                    autograd.grad(
                        self.loss(
                            torch.squeeze(self.model(x[i])),
                            torch.squeeze(y[i]),
                        ),
                        params,
                    )
                ).detach()
            )

        return torch.stack(grads, axis=0)

    def grad(
        self,
        x: torch.Tensor,
        y: torch.Tensor,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Calculates gradient of model parameters wrt $x$ and $y$.
        :param x: A matrix [NxD] representing the features $x_i$.
        :param y: A matrix [NxK] representing the target values $y_i$.
        :returns: A tuple where: \
            - first element is an array [P] with the gradients of the model. \
            - second element is the input to the model as a grad parameters. \
                This can be used for further differentiation. 
        """
        x = as_tensor(x).requires_grad_(True)
        y = as_tensor(y)

        params = [
            param for param in self.model.parameters() if param.requires_grad == True
        ]

        loss_value = self.loss(torch.squeeze(self.model(x)), torch.squeeze(y))
        grad_f = torch.autograd.grad(loss_value, params, create_graph=True)
        return flatten_gradient(grad_f), x

    def hessian(
        self,
        x: torch.Tensor,
        y: torch.Tensor,
        progress: bool = False,
    ) -> torch.Tensor:
        """Calculates the explicit hessian of model parameters given data ($x$ and $y$).
        :param x: A matrix [NxD] representing the features $x_i$.
        :param y: A matrix [NxK] representing the target values $y_i$.
        :returns: A tuple where: \
            - first element is an array [P] with the gradients of the model. \
            - second element is the input to the model as a grad parameters. \
                This can be used for further differentiation. 
        """
        grad_xy, _ = self.grad(x, y)
        backprop_on = [
            param for param in self.model.parameters() if param.requires_grad == True
        ]
        return mvp(
            grad_xy,
            torch.eye(self.num_params(), self.num_params()),
            backprop_on,
            progress,
        )
