from suite2p import run_s2p, default_ops
from suite2p.detection.anatomical import roi_detect
from suite2p.extraction import dcnv
import numpy as np
import os


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
    if not ops['nonrigid']:
        # The flags are hard coded and set to run each step of Suite2p (as this
        # is meant to be fixed. If this is updated by the user, we can generate 
        # an error warning to mention that this function is only meant to be
        # used for registration.

        ops.update(do_registration = 1, 
                    roi_detect = False,
                    spikedetect = False,
                    delete_bin = True)

        reg_ops = run_s2p(ops,db)
        desired_keys = ['xoff', 'yoff', 'do_registration', 'two_step_registration',
                        'roidetect', 'spikedetect', 'delete_bin']
        reg_ops = {key: reg_ops[key] for key in desired_keys}

        return reg_ops

    else:
        
        ops.update(nonrigid = True, 
                    do_registration = 1, 
                    roidetect = False,
                    spikedetect = False,
                    delete_bin = True)

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
    # Set flags
    reg_ops.update(do_registration = 0,
                    roidetect = True,
                    spikedetect = False)

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

    roi_ops.update(do_registration = 0,
                    roidetect = False,
                    spikedetect = True)
    
    spikes = dcnv.oasis(F=Fc, batch_size=roi_ops['batch_size'], 
                        tau=roi_ops['tau'], fs=roi_ops['fs'])
    np.save(os.path.join(roi_ops['save_path'], 'spks.npy'), spikes)

    return roi_ops, spikes