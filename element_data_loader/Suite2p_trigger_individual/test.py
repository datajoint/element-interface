from Suite2p_trigger import motion_correction_suite2p, segmentation_suite2p
from variables import ops, db
import matplotlib.pyplot as plt
import numpy as np

reg_ops = ops
# reg_ops = motion_correction_suite2p(ops, db)
roi_ops = segmentation_suite2p(reg_ops, db)
# roi_ops, spikes = deconvultion_suite2p(roi_ops, db)
# spks = np.load("suite2p/plane0/spks.npy", allow_pickle= True)
# plt.plot(spks)
# plt.show()