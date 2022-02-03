import nd2
import tifffile
import pathlib


def nd2_to_tif(nd2_file):
    """
    Convert Nikon .nd2 file to .tif file.
    
    Inputs
    ------
    nd2_file: str
        Path to the .nd2 file.
    """
    f = nd2.ND2File(nd2_file)
    tif_file = pathlib.Path(nd2_file).with_suffix('.nd2')
    tifffile.imwrite(tif_file, f.asarray(), imagej=True)
