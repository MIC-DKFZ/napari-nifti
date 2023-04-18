from __future__ import annotations
from typing import TYPE_CHECKING, Any, Sequence, Tuple, Union
import SimpleITK as sitk
import numpy as np

if TYPE_CHECKING:
    DataType = Union[Any, Sequence[Any]]
    FullLayerData = Tuple[DataType, dict, str]

dtype_mapping = {"int8": np.int8, "int16": np.int16, "int32": np.int32, "int64": np.int64}


def write_single_image(path: str, data: Any, meta: dict):
    """Writes a single image layer"""
    spacing, affine, header = None, None, None
    if "spacing" in meta["metadata"]:
        spacing = meta["metadata"]["affine"]
    if "affine" in meta["metadata"]:
        affine = meta["metadata"]["affine"]
    if "header" in meta["metadata"]:
        header = meta["metadata"]["header"]
    save_nifti(path, data, spacing=spacing, affine=affine, header=header)
    return [path]


def save_nifti(filename, image, spacing=None, affine=None, header=None):
    if str(image.dtype) in dtype_mapping:
        image = image.astype(dtype_mapping[str(image.dtype)])
    image = sitk.GetImageFromArray(image)

    if header is not None:
        [image.SetMetaData(key, header[key]) for key in header.keys()]

    if spacing is not None:
        image.SetSpacing(spacing)

    if affine is not None:
        pass  # How do I set the affine transform with SimpleITK? With NiBabel it is just nib.Nifti1Image(img, affine=affine, header=header)

    sitk.WriteImage(image, filename)
