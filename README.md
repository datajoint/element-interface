# DataJoint Elements Interface for external analysis packages

+ This repository serves a few purposes:
     + Load neurophysiological data into the
 [DataJoint Elements](https://github.com/datajoint/datajoint-elements).
     + Trigger packages used for neurophysiological data processing.
     + Functions common to the DataJoint Elements (e.g. search directory tree for data files).

+ See [DataJoint Elements](https://github.com/datajoint/datajoint-elements) for descriptions
 of the `elements` and `workflows` developed as part of this initiative.

# Architecture

+ The functions for each acquisition and analysis package are stored within a separate module.

+ Acquisition packages
     + `scanimage_utils.py`

+ Analysis packages
     + `suite2p_loader.py`
     + `caiman_loader.py`
     + `run_caiman.py`

# Installation

+ Install `element-interface`:
     ```
     pip install element-interface
     ```

+ This package is to be used in combination with the other DataJoint Elements (e.g. `element-calcium-imaging`).  The installation of packages used for data processing (e.g. `Suite2p`) will be included within the respective DataJoint Element (e.g. `element-calcium-imaging`).

# Usage

+ See the [workflow-calcium-imaging](https://github.com/datajoint/workflow-calcium-imaging) 
and [element-calcium-imaging](https://github.com/datajoint/element-calcium-imaging) 
repositories for example usage of `element-interface`.

+ ScanImage
     ```python
     import scanreader
     from element_interface import scanimage_utils

     # ScanImage file path
     scan_filepath = '<imaging_root_data_dir>/subject1/session0/<scan_filename>.tif'

     loaded_scan = scanreader.read_scan(scan_filepath)

     recording_time = scanimage_utils.get_scanimage_acq_time(loaded_scan)
     header = scanimage_utils.parse_scanimage_header(loaded_scan)
     ```

+ Suite2p
     ```python
     from element_interface import suite2p_loader

     # Directory containing Suite2p output
     output_dir = '<imaging_root_data_dir>/subject1/session0/suite2p'

     loaded_dataset = suite2p_loader.Suite2p(output_dir)
     ```

+ Suite2p wrapper functions for triggering analysis

  + Functions to independently run Suite2p's registration, segmentation, and deconvolution steps. These functions currently work for single plane tiff files.  If running all Suite2p pre-processing steps concurrently, these functions are not required and one can run `suite2p.run_s2p()`.

  + These wrapper functions were developed primarily because `run_s2p` cannot individually run deconvolution using the `spikedetect` flag ([Suite2p Issue #718](https://github.com/MouseLand/suite2p/issues/718)).

  + Requirements
    + [ops dictionary](https://suite2p.readthedocs.io/en/latest/settings.html)
    + [db dictionary](https://github.com/MouseLand/suite2p/blob/4b6c3a95b53e5581dbab1feb26d67878db866068/jupyter/run_pipeline_tiffs_or_batch.ipynb)

  + Note that the ops dictionary returned from the `motion_correction_suite2p` and `segmentation_suite2p` functions is only a subset of the keys generated with the `suite2p.default_ops()` function.

     ```python
     import element_interface
     import suite2p

     ops = dict(suite2p.default_ops(), nonrigid=False, two_step_registration=False)

     db = {
          'h5py': [], # single h5 file path
          'h5py_key': 'data',
          'look_one_level_down': False, # search for TIFFs in all subfolders 
          'data_path': ['/test_data'], # list of folders with tiffs                                    
          'subfolders': [], # choose subfolders of 'data_path'
          'fast-disk': '/test_data' # string path for storing binary file 
          }

     ops.update(do_registration=1, roidetect=False, spikedetect=False)
     motion_correction_ops = element_interface.suite2p_trigger.motion_correction_suite2p(ops, db)

     motion_correction_ops.update(do_registration=0, roidetect=True, spikedetect=False)
     segmentation_ops = element_interface.suite2p_trigger.segmentation_suite2p(motion_correction_ops, db)

     segmentation_ops.update(do_registration=0, roidetect=False, spikedetect=True)
     spikes = element_interface.suite2p_trigger.deconvolution_suite2p(segmentation_ops, db)
     ```


+ CaImAn
     ```python
     from element_interface import caiman_loader

     # Directory containing CaImAn output
     output_dir = '<imaging_root_data_dir>/subject1/session0/caiman'

     loaded_dataset = caiman_loader.CaImAn(output_dir)
     ```