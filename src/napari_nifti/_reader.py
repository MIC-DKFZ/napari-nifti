import SimpleITK as sitk
import numpy as np

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
    if not (path.endswith(".nii") or path.endswith(".nii.gz")):
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
    # load all files
    image_data_list = [load_nifti(_path) for _path in paths]
    # Convert to LayerData tuples
    layer_data = [(image_data["image"], {"affine": image_data["affine"], "metadata": image_data["metadata"]}, "image") for image_data in image_data_list]
    return layer_data


def load_nifti(filename):
    image_data = sitk.ReadImage(filename)
    image = sitk.GetArrayFromImage(image_data)
    spacing = image_data.GetSpacing()
    scale = list(spacing)[::-1]
    keys = image_data.GetMetaDataKeys()
    metadata = {key: image_data.GetMetaData(key) for key in keys}
    origin = image_data.GetOrigin()
    direction = image_data.GetDirection()
    # affine = np.zeros((4, 4))
    # affine[:3, :3] = np.asarray(direction).reshape(3, 3)
    # affine[3, 3] = 1
    affine = np.eye(4)
    affine[0, 0] = scale[0]
    affine[1, 1] = scale[1]
    affine[2, 2] = scale[2]
    return {"image": image, "affine": affine, "scale": scale, "metadata": {"metadata": metadata, "origin": origin, "direction": direction, "spacing": spacing}}
