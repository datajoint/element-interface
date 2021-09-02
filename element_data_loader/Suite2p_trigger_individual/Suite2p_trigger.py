from suite2p import run_s2p
from suite2p.extraction import dcnv
import numpy as np
import os
import warnings


def motion_correction_suite2p(ops, db):
    """Performs registration using Suite2p package, 
    Make sure the 'do_registration' key is set to 1 to perform registration

    Args:
        ops (dict): ops dictionary can be obtained by using default_ops() function. 
                    It contains all options and default values used to perform 
                    preprocessing.
        db (dict): dictionary that includes paths pointing towards the input data,
                   and where to store the data

    Returns:
        dict: Returns a dictionary with x and y shifts
        data.bin: Creates and saves a binary file on your local path. If 
                  delete_bin is set to True, the binary file is deleted after
                  processing.
        ops.npy: Creates and saves the options dictionary in a numpy array file 
                 in the specified path. The ops file gets updated during the 
                 cell detection and the deconvultion steps.
    """

    # Nonrigid motion correction

    if ops['nonrigid']:

        print("==========RUNNING NON-RIGID REGISTRATION==========")
        warnings.warn('You are running registration/ motion correction using \
                      Suite2p module, this requires do_registration=1,\
                      roidetect=False, spikedetect=False. If the ops dictionary\
                      has values differing from these, the flags will \
                      automatically be se set to it.')

        ops.update(do_registration = 1, 
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
        
    else:
    
    # Rigid motion correction

        print("==========RUNNING RIGID REGISTRATION==========")
        warnings.warn('You are running registration/ motion correction using \
                      Suite2p module, this requires do_registration=1,\
                      roidetect=False, spikedetect=False. If the ops dictionary\
                      has values differing from these, the flags will \
                      automatically be se set to it.')

        ops.update(do_registration = 1, 
                    roi_detect = False,
                    spikedetect = False,
                    delete_bin = True)

        reg_ops = run_s2p(ops,db)
        desired_keys = ['xoff', 'yoff', 'do_registration', 'two_step_registration',
                        'roidetect', 'spikedetect', 'delete_bin']
        reg_ops = {key: reg_ops[key] for key in desired_keys}

    return reg_ops


def segmentation_suite2p(reg_ops, db):
    """Performs cell detection using Suite2p package, 
    Make sure the 'roidetect' key is set to True to perform cell/ roi detection

    Args:
        reg_ops (dict): reg_ops dictionary can be obtained from registration 
                        step (CaImAn or Suite2p) Must contain x and y shifts 
                        along with 'do_registration'=0,
                        'two_step_registration'=False,
                        'roidetect'=True and 'spikedetect'= False
        db (dict): dictionary that includes paths pointing towards the input data,
                   and where to store the data

    Returns: 
        reg_ops (dict): The ops dictionary is updated with additional keys that
                        are added 
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

    warnings.warn('You are running cell detection/ segmentation using \
                    Suite2p module, this requires do_registration=0,\
                    roidetect=True, spikedetect=False. If the ops dictionary\
                    has values differing from these, the flags will \
                    automatically be se set to it.')
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
    """Performs cell detection using Suite2p package, 
    Make sure the 'roidetect' key is set to True to perform cell/ roi detection.
    The code to run deconvolution separately can be found here
    </https://suite2p.readthedocs.io/en/latest/deconvolution.html>.

    Args:
        roi_ops (dict): roi_ops dictionary can be obtained from registration
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
        roi_ops (dict): Returns a dictionary generated during the cell detection
                        step
        spks.npy: Updates the file with an array of deconvolved traces
    """

    warnings.warn('You are running cell detection/ segmentation using \
                      Suite2p module, this requires do_registration=0,\
                      roidetect=True, spikedetect=False. If the ops dictionary\
                      has values differing from these, the flags will \
                      automatically be se set to it.')

    F = np.load(db['fast-disk'] + '/suite2p/plane0/F.npy', allow_pickle = True)
    Fneu= np.load(db['fast-disk'] + '/suite2p/plane0/Fneu.npy',
                  allow_pickle = True)
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