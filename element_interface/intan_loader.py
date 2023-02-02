import numpy as np
import os, sys, struct
from pathlib import Path
import matplotlib.pyplot as plt


def read_qstring(fid):
    """Read Qt style QString.

    The first 32-bit unsigned number indicates the length of the string (in bytes).
    If this number equals 0xFFFFFFFF, the string is null.

    Strings are stored as unicode.
    """

    (length,) = struct.unpack("<I", fid.read(4))
    if length == int("ffffffff", 16):
        return ""

    if length > (os.fstat(fid.fileno()).st_size - fid.tell() + 1):
        print(length)
        raise Exception("Length too long.")

    # convert length from bytes to 16-bit Unicode words
    length = int(length / 2)

    data = []
    for i in range(0, length):
        (c,) = struct.unpack("<H", fid.read(2))
        data.append(c)

    if sys.version_info >= (3, 0):
        a = "".join([chr(c) for c in data])
    else:
        a = "".join([unichr(c) for c in data])

    return a


def read_header(fid):
    """Reads the Intan File Format header from the given file."""

    # Check 'magic number' at beginning of file to make sure this is an Intan
    # Technologies RHD2000 data file.
    (magic_number,) = struct.unpack("<I", fid.read(4))

    if magic_number != int("0xD69127AC", 16):
        raise Exception("Unrecognized file type.")

    header = {}
    # Read version number.
    version = {}
    (version["major"], version["minor"]) = struct.unpack("<hh", fid.read(4))
    header["version"] = version

    print("")
    print(
        "Reading Intan Technologies RHS2000 Data File, Version {}.{}".format(
            version["major"], version["minor"]
        )
    )
    print("")

    # Read information of sampling rate and amplifier frequency settings.
    (header["sample_rate"],) = struct.unpack("<f", fid.read(4))
    (
        header["dsp_enabled"],
        header["actual_dsp_cutoff_frequency"],
        header["actual_lower_bandwidth"],
        header["actual_lower_settle_bandwidth"],
        header["actual_upper_bandwidth"],
        header["desired_dsp_cutoff_frequency"],
        header["desired_lower_bandwidth"],
        header["desired_lower_settle_bandwidth"],
        header["desired_upper_bandwidth"],
    ) = struct.unpack("<hffffffff", fid.read(34))

    # This tells us if a software 50/60 Hz notch filter was enabled during
    # the data acquisition.
    (notch_filter_mode,) = struct.unpack("<h", fid.read(2))
    header["notch_filter_frequency"] = 0
    if notch_filter_mode == 1:
        header["notch_filter_frequency"] = 50
    elif notch_filter_mode == 2:
        header["notch_filter_frequency"] = 60

    (
        header["desired_impedance_test_frequency"],
        header["actual_impedance_test_frequency"],
    ) = struct.unpack("<ff", fid.read(8))
    (header["amp_settle_mode"], header["charge_recovery_mode"]) = struct.unpack(
        "<hh", fid.read(4)
    )

    frequency_parameters = {}
    frequency_parameters["amplifier_sample_rate"] = header["sample_rate"]
    frequency_parameters["board_adc_sample_rate"] = header["sample_rate"]
    frequency_parameters["board_dig_in_sample_rate"] = header["sample_rate"]
    frequency_parameters["desired_dsp_cutoff_frequency"] = header[
        "desired_dsp_cutoff_frequency"
    ]
    frequency_parameters["actual_dsp_cutoff_frequency"] = header[
        "actual_dsp_cutoff_frequency"
    ]
    frequency_parameters["dsp_enabled"] = header["dsp_enabled"]
    frequency_parameters["desired_lower_bandwidth"] = header["desired_lower_bandwidth"]
    frequency_parameters["desired_lower_settle_bandwidth"] = header[
        "desired_lower_settle_bandwidth"
    ]
    frequency_parameters["actual_lower_bandwidth"] = header["actual_lower_bandwidth"]
    frequency_parameters["actual_lower_settle_bandwidth"] = header[
        "actual_lower_settle_bandwidth"
    ]
    frequency_parameters["desired_upper_bandwidth"] = header["desired_upper_bandwidth"]
    frequency_parameters["actual_upper_bandwidth"] = header["actual_upper_bandwidth"]
    frequency_parameters["notch_filter_frequency"] = header["notch_filter_frequency"]
    frequency_parameters["desired_impedance_test_frequency"] = header[
        "desired_impedance_test_frequency"
    ]
    frequency_parameters["actual_impedance_test_frequency"] = header[
        "actual_impedance_test_frequency"
    ]

    header["frequency_parameters"] = frequency_parameters

    (
        header["stim_step_size"],
        header["recovery_current_limit"],
        header["recovery_target_voltage"],
    ) = struct.unpack("fff", fid.read(12))

    note1 = read_qstring(fid)
    note2 = read_qstring(fid)
    note3 = read_qstring(fid)
    header["notes"] = {"note1": note1, "note2": note2, "note3": note3}

    (header["dc_amplifier_data_saved"], header["eval_board_mode"]) = struct.unpack(
        "<hh", fid.read(4)
    )

    header["ref_channel_name"] = read_qstring(fid)

    # Create structure arrays for each type of data channel.
    header["spike_triggers"] = []
    header["amplifier_channels"] = []
    header["board_adc_channels"] = []
    header["board_dac_channels"] = []
    header["board_dig_in_channels"] = []
    header["board_dig_out_channels"] = []

    # Read signal summary from data file header.
    (number_of_signal_groups,) = struct.unpack("<h", fid.read(2))
    print("n signal groups {}".format(number_of_signal_groups))

    for signal_group in range(1, number_of_signal_groups + 1):
        signal_group_name = read_qstring(fid)
        signal_group_prefix = read_qstring(fid)
        (
            signal_group_enabled,
            signal_group_num_channels,
            signal_group_num_amp_channels,
        ) = struct.unpack("<hhh", fid.read(6))

        if (signal_group_num_channels > 0) and (signal_group_enabled > 0):
            for signal_channel in range(0, signal_group_num_channels):
                new_channel = {
                    "port_name": signal_group_name,
                    "port_prefix": signal_group_prefix,
                    "port_number": signal_group,
                }
                new_channel["native_channel_name"] = read_qstring(fid)
                new_channel["custom_channel_name"] = read_qstring(fid)
                (
                    new_channel["native_order"],
                    new_channel["custom_order"],
                    signal_type,
                    channel_enabled,
                    new_channel["chip_channel"],
                    command_stream,
                    new_channel["board_stream"],
                ) = struct.unpack(
                    "<hhhhhhh", fid.read(14)
                )  # ignore command_stream
                new_trigger_channel = {}
                (
                    new_trigger_channel["voltage_trigger_mode"],
                    new_trigger_channel["voltage_threshold"],
                    new_trigger_channel["digital_trigger_channel"],
                    new_trigger_channel["digital_edge_polarity"],
                ) = struct.unpack("<hhhh", fid.read(8))
                (
                    new_channel["electrode_impedance_magnitude"],
                    new_channel["electrode_impedance_phase"],
                ) = struct.unpack("<ff", fid.read(8))

                if channel_enabled:
                    if signal_type == 0:
                        header["amplifier_channels"].append(new_channel)
                        header["spike_triggers"].append(new_trigger_channel)
                    elif signal_type == 1:
                        raise Exception("Wrong signal type for the rhs format")
                        # header['aux_input_channels'].append(new_channel)
                    elif signal_type == 2:
                        raise Exception("Wrong signal type for the rhs format")
                        # header['supply_voltage_channels'].append(new_channel)
                    elif signal_type == 3:
                        header["board_adc_channels"].append(new_channel)
                    elif signal_type == 4:
                        header["board_dac_channels"].append(new_channel)
                    elif signal_type == 5:
                        header["board_dig_in_channels"].append(new_channel)
                    elif signal_type == 6:
                        header["board_dig_out_channels"].append(new_channel)
                    else:
                        raise Exception("Unknown channel type.")

    # Summarize contents of data file.
    header["num_amplifier_channels"] = len(header["amplifier_channels"])
    header["num_board_adc_channels"] = len(header["board_adc_channels"])
    header["num_board_dac_channels"] = len(header["board_dac_channels"])
    header["num_board_dig_in_channels"] = len(header["board_dig_in_channels"])
    header["num_board_dig_out_channels"] = len(header["board_dig_out_channels"])

    return header


INBOX = Path("/Users/tolgadincer/ClientData/Utah_Alex/2020Data/RawData/Organoid21")
header_filename = INBOX / "032520_US_885kHz_sham/info.rhs"
with open(header_filename, "rb") as fid:
    header = read_header(fid)


def read_time(file_paths, time_filename="time.dat", header_filename="info.rhs"):

    time = (
        np.memmap(time_filename, dtype=np.int32, offset=2_000_000, shape=10000)
        / header["frequency_parameters"]["amplifier_sample_rate"]
    )

    signals = np.empty([len(file_paths), len(time)])
    for i, file_path in enumerate(file_paths):
        signals[i, :] = np.memmap(
            file_path, dtype=np.int16, offset=2_000_000, shape=10000
        )
    signals = signals * 0.195  # Convert to microvolts

    return signals, time


INBOX = Path("/Users/tolgadincer/ClientData/Utah_Alex/2020Data/RawData/Organoid21")

time_filename = INBOX / "032520_US_885kHz_sham/time.dat"
header_filename = INBOX / "032520_US_885kHz_sham/info.rhs"

relative_paths = [
    "032520_US_885kHz_sham/amp-B-001.dat",
    "032520_US_885kHz_sham/amp-B-005.dat",
]
file_paths = [INBOX / x for x in relative_paths]

signals, time = read_time(file_paths, time_filename, header_filename)

for signal in signals:
    plt.plot(time, signal)
# plt.title("/".join(file_path.parts[-2:]))
plt.xlabel("Time (s)")
plt.ylabel("Signal (microvolts)")
plt.show()
