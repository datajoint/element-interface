from suite2p import default_ops

# Note that the flags will be updated in the ops dictionary according to the
# step you choose to run / function you select

ops = dict(default_ops(), nonrigid=True, two_step_registration=False)

db = {
      'h5py': [], # a single h5 file path
      'h5py_key': 'data',
      'look_one_level_down': False, # whether to look in ALL subfolders when 
                                    # searching for tiffs
      'data_path': ['/Users/geetikasingh/Desktop/Projects-DJ/element-data-loader/element_data_loader/test_data'], # a list of folders with tiffs 
                                  # (or folder of folders with tiffs if 
                                  # look_one_level_down is True, or subfolders 
                                  # is not empty)                                    
      'subfolders': [], # choose subfolders of 'data_path' to look in (optional)
      'fast-disk': '/Users/geetikasingh/Desktop/Projects-DJ/element-data-loader/element_data_loader/test_data' # string which specifies where the binary file 
                               # will be stored (should be an SSD)
    }