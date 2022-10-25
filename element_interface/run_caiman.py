import cv2
import pathlib

try:
    cv2.setNumThreads(0)
except:
    pass

import caiman as cm
from caiman.source_extraction.cnmf.cnmf import *
from caiman.source_extraction.cnmf import params as params

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

    opts = params.CNMFParams(params_dict=parameters)

    c, dview, n_processes = cm.cluster.setup_cluster(
        backend="local", n_processes=None, single_thread=False
    )

    cnm = CNMF(n_processes, params=opts, dview=dview)
    cnmf_output, mc_output = cnm.fit_file(
        motion_correct=True, include_eval=True, output_dir=output_dir, return_mc=True
    )

    cm.stop_server(dview=dview)

    cnmf_output_file = pathlib.Path(cnmf_output.mmap_file[:-4] + "hdf5")
    assert cnmf_output_file.exists()
    assert cnmf_output_file.parent == pathlib.Path(output_dir)

    _save_mc(mc_output, cnmf_output_file.as_posix(), parameters["is3D"])
