import numpy as np
from medvol import MedVol

def napari_get_reader(path):
    """A basic implementation of a Reader contribution.

    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    function or None
        If the path is a recognized format, return a function that accepts the
        same path or list of paths, and returns a list of layer data tuples.
    """
    if isinstance(path, list):
        # reader plugins may be handed single path, or a list of paths.
        # if it is a list, it is assumed to be an image stack...
        # so we are only going to look at the first file.
        path = path[0]

    # if we know we cannot read the file, we immediately return None.
    if not (path.endswith(".nii") or path.endswith(".nii.gz") or path.endswith(".nrrd")):
        return None

    # otherwise we return the *function* that can read ``path``.
    return reader_function


def reader_function(path):
    """Take a path or list of paths and return a list of LayerData tuples.

    Readers are expected to return data as a list of tuples, where each tuple
    is (data, [add_kwargs, [layer_type]]), "add_kwargs" and "layer_type" are
    both optional.

    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    layer_data : list of tuples
        A list of LayerData tuples where each tuple in the list contains
        (data, metadata, layer_type), where data is a numpy array, metadata is
        a dict of keyword arguments for the corresponding viewer.add_* method
        in napari, and layer_type is a lower-case string naming the type of layer.
        Both "meta", and "layer_type" are optional. napari will default to
        layer_type=="image" if not provided
    """
    # handle both a string and a list of strings
    paths = [path] if isinstance(path, str) else path
    layer_data = []
    for _path in paths:
        # canonicalize=True (default): reorder axes to XYZ, fix flipped axes.
        # Keep remove_obliqueness=False so the true oblique affine is preserved for
        # round-trip saving. The deobliqued affine is computed separately for display.
        image = MedVol(_path, remove_obliqueness=False)

        # MedVol canonical array axis order is XYZ (axis 0 = X, 1 = Y, 2 = Z).
        # Napari uses ZYX convention (axis 0 is the primary slider = Z for 3-D volumes).
        # Permute (X,Y,Z) → (Z,Y,X) so the slice slider scrolls through axial planes.
        array_zyx = np.transpose(image.array, (2, 1, 0))

        # Build a deobliqued affine for display only: diagonal from spacing + origin.
        # remove_obliqueness does not change spacing or origin, only the direction, so
        # this is equivalent to loading with remove_obliqueness=True without a second IO.
        spacing = np.array(image.spacing)   # XYZ order
        origin  = np.array(image.origin)
        deobliqued_xyz = np.diag([spacing[0], spacing[1], spacing[2], 1.0])
        deobliqued_xyz[:3, 3] = origin
        # Permute columns to match ZYX axis order for napari.
        # Column i of A' = world direction of new array axis i.
        affine_zyx = deobliqued_xyz[:, [2, 1, 0, 3]]

        metadata = {
            "affine": image.affine,             # true oblique XYZ affine — used for saving
            "spacing": image.spacing,           # XYZ order
            "origin": image.origin,
            "direction": image.direction,
            "header": image.header,
            "coordinate_system": image.coordinate_system,
        }
        layer_data.append((array_zyx, {"affine": affine_zyx, "metadata": metadata}, "image"))
    return layer_data
