import cv2
import os
import pathlib
import shutil

try:
    cv2.setNumThreads(0)
except:  # noqa E722
    pass  # TODO: remove bare except

import caiman as cm
from caiman.source_extraction.cnmf import params as params
from caiman.source_extraction.cnmf.cnmf import CNMF

from .caiman_loader import _save_mc


def run_caiman(
    file_paths: list,
    parameters: dict,
    sampling_rate: float,
    output_dir: str,
    is3D: bool,
):
    """
    Runs the standard caiman analysis pipeline (CNMF.fit_file method).

    Args:
        file_paths (list): Image (full) paths
        parameters (dict): Caiman parameters
        sampling_rate (float): Image sampling rate (Hz)
        output_dir (str): Output directory
        is3D (bool):  the data is 3D
    """
    parameters["is3D"] = is3D
    parameters["fnames"] = file_paths
    parameters["fr"] = sampling_rate

    if "indices" in parameters:
        indices = parameters.pop(
            "indices"
        )  # Indices that restrict FOV for motion correction.
        indices = slice(*indices[0]), slice(*indices[1])
        parameters["motion"] = {**parameters.get("motion", {}), "indices": indices}

    opts = params.CNMFParams(params_dict=parameters)

    c, dview, n_processes = cm.cluster.setup_cluster(
        backend="multiprocessing", n_processes=None
    )

    try:
        cnm = CNMF(n_processes, params=opts, dview=dview)
        cnmf_output, mc_output = cnm.fit_file(
            motion_correct=True,
            indices=None,  # Indices defined here restrict FOV for segmentation. `None` uses the full image for segmentation.
            include_eval=True,
            output_dir=output_dir,
            return_mc=True,
        )
    except Exception as e:
        dview.terminate()
        raise e
    else:
        cm.stop_server(dview=dview)

    cnmf_output_file = pathlib.Path(cnmf_output.mmap_file[:-4] + "hdf5")
    assert cnmf_output_file.exists()
    output_files = os.listdir(cnmf_output_file.parent)
    for output_file in output_files:
        try:
            shutil.move(output_file, output_dir)
        except FileExistsError:
            print(f"File {output_file.name} already exists in {output_dir}. Skipping.")

    _save_mc(mc_output, cnmf_output_file.as_posix(), parameters["is3D"])
