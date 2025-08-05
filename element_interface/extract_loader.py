import os
import h5py
from datetime import datetime
from pathlib import Path

import numpy as np
from scipy.io import loadmat


class EXTRACT_loader:
    def __init__(self, extract_file_path: str):
        """Initialize EXTRACT loader class

        Args:
            extract_file_path (str): string, absolute file path to EXTRACT output file.
        """

        self.creation_time = datetime.fromtimestamp(os.stat(extract_file_path).st_ctime)
        try:
            results = loadmat(extract_file_path)

            self.S = results["output"][0]["spatial_weights"][
                0
            ]  # (Height, Width, MaskId)
            self.spatial_weights = self.S.transpose([2, 0, 1])  # MaskId, Height, Width
            self.T = results["output"][0]["temporal_weights"][0]  # (Time, MaskId)

        except NotImplementedError:

            results = h5py.File(extract_file_path, "r")
            self.spatial_weights = results["output"]["spatial_weights"][
                :
            ]  # (MaskId, Height, Width)
            self.T = results["output"]["temporal_weights"][:]  # (MaskId, Time)

    def load_results(self):
        """Load the EXTRACT results

        Returns:
            masks (dict): Details of the masks identified with the EXTRACT segmentation package.
        """
        from scipy.sparse import find

        masks = []

        for mask_id, s in enumerate(self.spatial_weights):
            ypixels, xpixels, weights = find(s)
            masks.append(
                dict(
                    mask_id=mask_id,
                    mask_npix=len(weights),
                    mask_weights=weights,
                    mask_center_x=int(np.average(xpixels, weights=weights) + 0.5),
                    mask_center_y=int(np.average(ypixels, weights=weights) + 0.5),
                    mask_center_z=None,
                    mask_xpix=xpixels,
                    mask_ypix=ypixels,
                    mask_zpix=None,
                )
            )
        return masks
