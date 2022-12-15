import os
import numpy as np
from pathlib import Path
from datetime import datetime


class EXTRACT_loader:
    def __init__(self, extract_dir: str):
        """Initialize EXTRACT loader class

        Args:
            extract_dir (str): string, absolute file path to EXTRACT directory

        Raises:
            FileNotFoundError: Could not find EXTRACT results
        """
        from scipy.io import loadmat

        try:
            extract_file = next(Path(extract_dir).glob("*_extract_output.mat"))
        except StopInteration:
            raise FileNotFoundError(
                f"EXTRACT output result file is not found at {extract_dir}."
            )

        results = loadmat(extract_file)

        self.creation_time = datetime.fromtimestamp(os.stat(extract_file).st_ctime)
        self.S = results["output"][0]["spatial_weights"][0]  # (Height, Width, MaskId)
        self.T = results["output"][0]["temporal_weights"][0]  # (Time, MaskId)

    def load_results(self):
        """Load the EXTRACT results
        
        Returns:
            masks (dict): Details of the masks identified with the EXTRACT segmentation package.
        """
        from scipy.sparse import find

        S_transposed = self.S.transpose([2, 0, 1])  # MaskId, Height, Width

        masks = []

        for mask_id, s in enumerate(S_transposed):
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
