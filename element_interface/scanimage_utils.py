import re
from datetime import datetime


def parse_scanimage_header(scan):
    """Parse ScanImage header

    Args:
        scan (scanimage object): ScanImage object including a header property

    Returns:
        header (dict): ScanImage header as key-value dictionary
    """
    header = {}
    for item in scan.header.split("\n"):
        try:
            key, value = item.split(" = ")
            key = re.sub("^scanimage_", "", key.replace(".", "_"))
            header[key] = value
        except:
            pass
    return header


def get_scanimage_acq_time(scan):
    """Return ScanImage acquisition time

    Args:
        scan (scanimage object): ScanImage object with header

    Returns:
        str: acquisition time in %Y %m %d %H %M %S format
    """
    header = parse_scanimage_header(scan)
    recording_time = datetime.strptime(
        (header["epoch"][1:-1]).replace(",", " "), "%Y %m %d %H %M %S.%f"
    )
    return recording_time
