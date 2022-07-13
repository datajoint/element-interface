from suite2p import run_s2p
from suite2p.extraction import dcnv
import numpy as np
import os
import warnings


def motion_correction_suite2p(ops, db):
    """Performs registration using Suite2p package

    Args:
        ops (dict): ops dictionary can be obtained by using default_ops()
                    function. It contains all options and default values used
                    to perform preprocessing. ops['do_registration'] should be
                    set to 1.
        db (dict): dictionary that includes paths pointing towards the input
                   data, and path to store outputs

    Returns:
        registration_ops (dict): Returns a dictionary that includes x and y shifts.
                                 This dictionary only consists of a subset of the
                                 output so that we only use the required values
                                 in the segmentation step.
        data.bin: Creates and saves a binary file on your local path. If
                  delete_bin is set to True (default: False), the binary file is
                  deleted after processing.
        ops.npy: Creates and saves the options dictionary in a numpy array file
                 in the specified path. The ops file gets updated during the
                 cell detection and the deconvolution steps.
    """

    if (not ops["do_registration"]) or ops["roidetect"] or ops["spikedetect"]:
        warnings.warn(
            "You are running motion correction with Suite2p."
            "Requirements include do_registration=1,"
            "roidetect=False, spikedetect=False.  The ops"
            "dictionary has differing values. The flags will"
            "be set to the required values."
        )

        ops.update(do_registration=1, roidetect=False, spikedetect=False)

    if ops["nonrigid"]:

        print("------------RUNNING NON-RIGID REGISTRATION------------")

        registration_ops = run_s2p(ops, db)
        subset_keys = [
            "xoff",
            "yoff",
            "xoff1",
            "yoff1",
            "do_registration",
            "two_step_registration",
            "roidetect",
            "spikedetect",
            "delete_bin",
            "xblock",
            "yblock",
            "xrange",
            "yrange",
            "nblocks",
            "nframes",
        ]

    else:

        print("------------RUNNING RIGID REGISTRATION------------")

        registration_ops = run_s2p(ops, db)
        subset_keys = [
            "xoff",
            "yoff",
            "do_registration",
            "two_step_registration",
            "roidetect",
            "spikedetect",
            "delete_bin",
        ]

    registration_ops = {key: registration_ops[key] for key in subset_keys}

    return registration_ops


def segmentation_suite2p(registration_ops, db):
    """Performs cell detection using Suite2p package,
    Make sure the 'roidetect' key is set to True to perform cell/ roi detection

    Args:
        registration_ops (dict): reg_ops dictionary can be obtained from
                                 registration step (CaImAn or Suite2p).
                                 Must contain x and y shifts along with
                                 'do_registration'=0,
                                 'two_step_registration'=False,
                                 'roidetect'=True and 'spikedetect'= False
        db (dict): dictionary that includes paths pointing towards the input
                   data, and path to store outputs

    Returns:
        segmentation_ops (dict): The ops dictionary is updated with additional
                                 keys that are added. This dictionary only
                                 consists of a subset of the
                                 output so that we only use the required values
                                 in the deconvolution step.
        data.bin: Creates and saves a binary file on your local path, if the one
                  created during registration is deleted. If delete_bin is set
                  to True, the binary file is deleted after processing.
        ops.npy: Updates the options dictionary in a file created during the
                 registration step and saves as a numpy array file on the
                 specified path.
        F.npy: Stores an array of fluorescence traces
        Fneu.npy: Returns an array of neuropil fluorescence traces
        iscell.npy: Specifies whether an ROI is a cell
        stat.npy: Returns a list of statistics computed for each cell
        spks.npy: Returns an empty file, it is updated during the deconvolution
                  step with deconvolved traces
    """

    if (
        registration_ops["do_registration"]
        or not (registration_ops["roidetect"])
        or registration_ops["spikedetect"]
    ):
        warnings.warn(
            "You are running segmentation with Suite2p. Requirements"
            "include do_registration=0, roidetect=True,"
            "spikedetect=False. The ops dictionary has differing"
            "values. The flags will be set to the required values."
        )
        registration_ops.update(do_registration=0, roidetect=True, spikedetect=False)

    segmentation_ops = run_s2p(registration_ops, db)
    subset_keys = [
        "baseline",
        "win_baseline",
        "sig_baseline",
        "fs",
        "prctile_baseline",
        "batch_size",
        "tau",
        "save_path",
        "do_registration",
        "roidetect",
        "spikedetect",
        "neucoeff",
    ]

    segmentation_ops = {key: segmentation_ops[key] for key in subset_keys}

    return segmentation_ops


def deconvolution_suite2p(segmentation_ops, db):
    """Performs cell detection using Suite2p package,
    Make sure the 'roidetect' key is set to True to perform cell/ roi detection.
    The code to run deconvolution separately can be found here
    </https://suite2p.readthedocs.io/en/latest/deconvolution.html>.

    Args:
        segmentation_ops (dict): roi_ops dictionary can be obtained from registration
                        step (CaImAn or Suite2p). Must contain baseline,
                        win_baseline (window in seconds for max filter),
                        sig_baseline (width of Gaussian filter in seconds),
                        fs (sampling rate per plane),
                        prctile_baseline (percentile of trace to use as baseline
                        is using constant_prctile for baseline)
                        along with 'do_registration'=0,
                        'two_step_registration'=False,'roidetect'=False and
                        'spikedetect'= True

    Returns:
        spks.npy: Updates the file with an array of deconvolved traces
    """
    if (
        segmentation_ops["do_registration"]
        or segmentation_ops["roidetect"]
        or (not segmentation_ops["spikedetect"])
    ):
        warnings.warn(
            "You are running deconvolution using Suite2p module."
            "Requirements include do_registration=0, roidetect=False,"
            "spikedetect=True. The ops dictionary has differing values,"
            "the flags will be se set to the required values."
        )
        segmentation_ops.update(do_registration=0, roidetect=False, spikedetect=True)

    F = np.load(db["fast-disk"] + "/suite2p/" + "plane0" + "/F.npy", allow_pickle=True)
    Fneu = np.load(
        db["fast-disk"] + "/suite2p/" + "plane0" + "/Fneu.npy", allow_pickle=True
    )
    Fc = F - segmentation_ops["neucoeff"] * Fneu

    Fc = dcnv.preprocess(
        F=Fc,
        baseline=segmentation_ops["baseline"],
        win_baseline=segmentation_ops["win_baseline"],
        sig_baseline=segmentation_ops["sig_baseline"],
        fs=segmentation_ops["fs"],
        prctile_baseline=segmentation_ops["prctile_baseline"],
    )

    spikes = dcnv.oasis(
        F=Fc,
        batch_size=segmentation_ops["batch_size"],
        tau=segmentation_ops["tau"],
        fs=segmentation_ops["fs"],
    )
    np.save(os.path.join(segmentation_ops["save_path"], "spks.npy"), spikes)

    return spikes
