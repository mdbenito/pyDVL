# FIXME the following code was part of an attempt to accommodate different
# frameworks. In its current form it is ugly and thus it will likely be changed
# in the future.

from .twice_differentiable import TwiceDifferentiable

__all__ = ["TwiceDifferentiable"]

try:
    import torch

    from .torch_differentiable import TorchTwiceDifferentiable

    __all__.append("TorchTwiceDifferentiable")

    from .torch_differentiable import (
        as_tensor,
        einsum,
        identity_tensor,
        mvp,
        solve_linear,
        stack_tensors,
    )

    TensorType = torch.Tensor
    ModelType = torch.nn.Module

except ImportError:
    pass

__all__.extend(
    [
        "TensorType",
        "ModelType",
        "solve_linear",
        "as_tensor",
        "stack_tensors",
        "einsum",
        "identity_tensor",
        "mvp",
    ]
)
