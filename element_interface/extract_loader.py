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

        output_file = list(Path(extract_dir).glob("*_extract_output.mat"))

        if not output_file:
            raise FileNotFoundError(
                "EXTRACT output result files not found at {}".format(extract_dir)
            )

        results = loadmat(output_file[0])

        self.creation_time = datetime.utcnow()
        self.S = results["output"][0]["spatial_weights"][0]  # (Height, Width, Time)
        self.T = results["output"][0]["temporal_weights"][0]  # (Time, MaskId)

    def load_results(self):
        """Load the EXTRACT results"""
        from scipy.sparse import find

        S_tr = self.S.transpose([2, 0, 1])  # Mask_no, Height, Width

        masks = []

        for mask_id, s in enumerate(S_tr):
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
