import numpy as np
from pathlib import Path
from intanrhsreader import read_header


def load_rhs(folder: str, file_expr: str = "*"):
    """Load rhs data

    Data type and coversions are based on https://intantech.com/files/Intan_RHS2000_data_file_formats.pdf.

    Example:
        # Read data
        >>> rhs_data = load_rhs("/home/inbox/organoids21/032520_US_885kHz_sham", file_expr="amp*dat")

        # Plot data
        >>> import matplotlib.pyplot as plt
        >>> plt.plot(rhs_data["time"], rhs_data["recordings"]["amp-B-000.dat"])
        >>> plt.xlabel("Time (s)")
        >>> plt.ylabel("Reading")
        >>> plt.show()

    Args:
        folder (str): Folder that contains info.rhs, time.dat, and *.dat files
        file_expr (str): pattern matching of file names to be read. Defaults to "*" (read all files).

    Returns:
        rhs_data (dict): RHS data.
            rhs_data["header"] (dict): Header.
            rhs_data["recordings"] (dict): Readings from various files
            rhs_data["timestamps"] (np.array_like): Relative timestamps in seconds.
    """

    rhs_data = {}

    # Get header
    header_filepath = next(Path(folder).glob("info.rhs"))
    with open(header_filepath, "rb") as fid:
        rhs_data["header"] = read_header(fid)

    # Get timestamps
    time_file = next(Path(folder).glob("time.dat"))

    rhs_data["timestamps"] = (
        np.memmap(time_file, dtype=np.int32)
        / rhs_data["header"]["frequency_parameters"]["amplifier_sample_rate"]
    )

    # Get data files
    file_paths = Path(folder).glob(file_expr)

    exclude_list = ["time", "info", "Zone.Identifier"]

    file_paths = [
        file
        for file in file_paths
        if not any(string in file.as_posix() for string in exclude_list)
    ]

    # Get recording data
    rhs_data["recordings"] = {}

    for file_path in sorted(file_paths):
        signal_type = file_path.stem.split("-")[0]

        if signal_type == "amp":
            signal = np.memmap(file_path, dtype=np.int16)
            signal = signal * 0.195  # Convert to microvolts

        elif signal_type == "board":
            signal = np.memmap(file_path, dtype=np.uint16)
            signal = (signal - 32768) * 0.0003125  # Convert to volts

        elif signal_type == "dc":
            signal = np.memmap(file_path, dtype=np.uint16)
            signal = (signal - 512) * 19.23  # Convert to milivolts

        elif signal_type == "stim":
            signal = np.memmap(file_path, dtype=np.uint16)
            # convert the signal from 9-bit one's complement to standard encoding
            current = np.bitwise_and(signal, 255) * rhs_data["header"]["stim_step_size"]
            sign = 1 - np.bitwise_and(signal, 256) // 128
            signal = current * sign

        rhs_data["recordings"][file_path.stem] = signal
    return rhs_data
