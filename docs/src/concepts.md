# Concepts

## Software interoperability

While software versioning helps researchers keep track of changes over time, it often
makes sense to separate the interface from the pipeline itself. By collecting utilities
here in Element Interface, maintainers can keep up to date with the latest developments
across other packages, without causing issues in the respective Element.

## Element Features

### General utilities

`utils.find_full_path` and `utils.find_root_directory` are used
across many Elements and Workflows to allow for the flexibility of providing
one or more root directories in the user's config, and extrapolating from a relative
path at runtime.

`utils.ingest_csv_to_table` is used across workflow examples to ingest from sample data
from local CSV files into sets of manual tables. While researchers may wish to manually
insert for day-to-day operations, it helps to have a more complete dataset when learning
how to use various Elements.

`utils.str_to_bool` converts a set of strings to boolean True or False. This is implemented
as the equivalent item in Python's `distutils` which will be removed in future versions.

`utils.memoized_result` is a decorator that caches the result of a function call based 
 on input parameters and the state of the output. If the function is called with the same
 parameters and the output files in the directory remain unchanged, it returns the 
 cached results; otherwise, it executes the function and caches the new results along 
 with metadata.

### Suite2p

This Element provides functions to independently run Suite2p's motion correction,
segmentation, and deconvolution steps. These functions currently work for single plane
tiff files. If one is running all Suite2p pre-processing steps concurrently, these
functions are not required and one can run `suite2p.run_s2p()`. The wrapper functions
here were developed primarily because `run_s2p` cannot individually run deconvolution
using the `spikedetect` flag ( 
[Suite2p Issue #718](https://github.com/MouseLand/suite2p/issues/718)).

Requirements:

- [ops dictionary](https://suite2p.readthedocs.io/en/latest/settings.html)
  
- [db dictionary](https://github.com/MouseLand/suite2p/blob/4b6c3a95b53e5581dbab1feb26d67878db866068/jupyter/run_pipeline_tiffs_or_batch.ipynb)

**Note:** The ops dictionary returned from the `motion_correction_suite2p` and
`segmentation_suite2p` functions is only a subset of the keys generated with the
`suite2p.default_ops()` function.

### PrairieView Reader

This Element provides a `PrairieViewMeta` class to handle different types of output from
 the PrairieView Scanner. The PrairieView software either generates one `.ome.tif` 
 imaging file per frame acquired or multi-page `.ome.tif` files. The metadata for all 
 frames is contained in one `.xml` file. This class contains methods that locate the 
 `.xml` file and generate a dictionary necessary to populate the DataJoint ScanInfo and
  Field tables. The class also contains methods to create a big tiff file from the 
  individual `.ome.tif` files. PrairieView works with resonance scanners with a single 
  field, does not support bidirectional x and y scanning, and the `.xml` file does not 
  contain ROI information.

## Element Architecture

The functions for each acquisition and analysis package are stored within a separate
module.

- Acquisition packages: [ScanImage](../api/element_interface/scanimage_utils)
- Analysis packages:
  
  - Suite2p [loader](../api/element_interface/suite2p_loader) and [trigger](../api/element_interface/suite2p_trigger)

  - CaImAn [loader](../api/element_interface/caiman_loader) and [trigger](../api/element_interface/run_caiman)

- Data upload: [DANDI](../api/element_interface/dandi/)

## Roadmap

Further development of this Element is community driven.  Upon user requests and based
on guidance from the Scientific Steering Group we will additional features to
this Element.
