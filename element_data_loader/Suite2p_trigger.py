from suite2p import run_s2p, default_ops
from suite2p.extraction import dcnv
import numpy as np
import matplotlib.pyplot as plt
import os
# from variables import db, ops


def motion_correction_suite2p(ops, db):
    """Performs registration using Suite2p package, 
    Make sure the 'do_registration' key is set to 1 to perform registration

    Args:
        ops (dict): ops dictionary can be obtained by using default_ops() function. 
                    It contains all options and default values used to perform 
                    preprocessing.

    Returns:
        dict : Returns a dictionary with x and y shifts
    """
    # Rigid motion correction
    if ops['nonrigid'] == False:
        # The flags are hard coded and set to run each step of Suite2p (as this
        # is meant to be fixed. If this is updated by the user, we can generate 
        # an error warning to mention that this function is only meant to be
        # used for registration.

        ops['do_registration'] = 1
        ops['roidetect'] = False
        ops['spikedetect'] = False
        ops['delete_bin'] = True

        reg_ops = run_s2p(ops,db)
        desired_keys = ['xoff', 'yoff', 'do_registration', 'two_step_registration',
                        'roidetect', 'spikedetect', 'delete_bin']
        reg_ops = {key: reg_ops[key] for key in desired_keys}

        return reg_ops

    else:

        ops['nonrigid'] = True
        ops['do_registration'] = 1
        ops['roidetect'] = False
        ops['spikedetect'] = False
        ops['delete_bin'] = True

        reg_ops = run_s2p(ops,db)
        desired_keys = ['xoff', 'yoff', 'xoff1', 'yoff1',
                        'do_registration',
                        'two_step_registration',
                        'roidetect',
                        'spikedetect', 'delete_bin',
                        'xblock', 'yblock', 'xrange', 'yrange', 'nblocks',
                        'nframes']
        reg_ops = {key: reg_ops[key] for key in desired_keys}

        return reg_ops


def segmentation_suite2p(reg_ops, db):
    """Performs cell detection using Suite2p package, 
    Make sure the 'roidetect' key is set to True to perform cell/ roi detection

    Args:
        reg_ops (dict): reg_ops dictionary can be obtained from registration step (CaImAn or Suite2p)
                        Must contain x and y shifts along with 'do_registration'=0, 'two_step_registration'=False,
                        'roidetect'=True and 'spikedetect'= False

    Returns:
        dict : Returns a dictionary with x and y shifts
    """

    if reg_ops['nonrigid'] == False:

        # Set flags
        reg_ops['do_registration'] = 0
        reg_ops['roidetect'] = True
        reg_ops['spikedetect'] = False

        roi_ops = run_s2p(reg_ops,db)
        desired_keys = ['baseline', 'win_baseline', 'sig_baseline',
                        'fs', 'prctile_baseline', 'batch_size',
                        'tau','save_path']

        roi_ops = {key: roi_ops[key] for key in desired_keys}

        return roi_ops

    else:

        # Set flags
        reg_ops['nonrigid'] = True
        reg_ops['do_registration'] = 0
        reg_ops['roidetect'] = True
        reg_ops['spikedetect'] = False

        roi_ops = run_s2p(reg_ops,db)
        desired_keys = ['baseline', 'win_baseline', 'sig_baseline',
                        'fs', 'prctile_baseline', 'batch_size',
                        'tau','save_path']

        roi_ops = {key: roi_ops[key] for key in desired_keys}

        return roi_ops


def deconvolution_suite2p(roi_ops, db):

    # Rigid motion correction
    F = np.load("element_data_loader/test_data/suite2p/plane0/F.npy", allow_pickle = True)
    Fneu = np.load("element_data_loader/test_data/suite2p/plane0/Fneu.npy", allow_pickle = True)
    Fc = F - roi_ops['neucoeff'] * Fneu

    Fc = dcnv.preprocess(
         F=Fc,
         baseline=roi_ops['baseline'],
         win_baseline=roi_ops['win_baseline'],
         sig_baseline=roi_ops['sig_baseline'],
         fs=roi_ops['fs'],
         prctile_baseline=roi_ops['prctile_baseline']
     )

    if roi_ops['nonrigid'] == False:

        roi_ops['do_registration'] = 0
        roi_ops['roidetect'] = False
        roi_ops['spikedetect'] = True

        spikes = dcnv.oasis(F=Fc, batch_size=roi_ops['batch_size'], 
                           tau=roi_ops['tau'], fs=roi_ops['fs'])
        np.save(os.path.join(roi_ops['save_path'], 'spks.npy'), spikes)

        return roi_ops, spikes

    else:

        roi_ops['nonrigid'] = True
        roi_ops['do_registration'] = 0
        roi_ops['roidetect'] = False
        roi_ops['spikedetect'] = True

        spikes = dcnv.oasis(F=Fc, batch_size=roi_ops['batch_size'], 
                            tau=roi_ops['tau'], fs=roi_ops['fs'])
        np.save(os.path.join(roi_ops['save_path'], 'spks.npy'), spikes)

        return roi_ops, spikes