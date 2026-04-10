from __future__ import annotations
from typing import TYPE_CHECKING, Any, Sequence, Tuple, Union
import numpy as np
from medvol import MedVol

if TYPE_CHECKING:
    DataType = Union[Any, Sequence[Any]]
    FullLayerData = Tuple[DataType, dict, str]


def write_single_image(path: str, data: Any, meta: dict):
    """Writes a single image layer"""
    meta = meta["metadata"]
    # The layer is stored in SAR+ order (dim 0 = S, dim 1 = A, dim 2 = R).
    # Permute back to RAS+ (XYZ) so MedVol saves with the canonical affine.
    array_ras = np.transpose(data, (2, 1, 0))
    MedVol(
        array_ras,
        affine=meta.get("affine"),             # true oblique RAS+ affine from load
        header=meta.get("header"),
        coordinate_system=meta.get("coordinate_system"),
    ).save(path)
    return [path]
