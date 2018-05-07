import re
from .hplc_data_types import PeakTableData
from .calibration_curve_types import HPLCCalibrationCurve, CalibrationCurve
import io
import pandas as pd
import typing
import datetime
import inspect


def get_all_raw_hplc_data(data_list):
    parsed_list = []
    for data in data_list:
        parsed_list.append(get_raw_hplc_data(data))
    return parsed_list


def get_raw_hplc_data(data, peak_re=re.compile("\[(.+)\((.+)\)\]\n#.+(\d)\n((?:.+\n)*)")):
    raw_data = re.findall(peak_re, data)
    return raw_data


def process_raw_data(raw_data_list: list, standards=False):
    detector_dict = {}
    for data in raw_data_list:
        if data[-1] is "":
            continue
        elif data[0] == "Peak Table":
            peak_data_str = io.StringIO(initial_value=data[-1])
            peak_table = PeakTableData(detector_name=data[1].split("-")[-1], peak_data=pd.read_table(peak_data_str))
            detector_dict[peak_table.detector_name] = peak_table
            if standards:
                peak_table.is_standard = True
        elif data[0] == "PDA Multi Chromatogram":
            wavelength = int(re.search("Wavelength\(nm\)\t(.+)\n", data[-1]).group(1))
            peak_table = detector_dict[data[1]]
            peak_table.wavelength = wavelength
        else:
            print("Weird Behavior!")
    return list(detector_dict.values())


def process_multiple_samples(parsed_data_list: typing.List[typing.List], are_standards=False):
    final_list = []
    for parsed in parsed_data_list:
        final_list.extend(process_raw_data(parsed))
    return final_list


def find_like_peaks(peak_table_list: typing.List[PeakTableData], error: float):
    full_df = pd.DataFrame()
    for peak_table in peak_table_list:
        peak_table.peak_data = peak_table.peak_data.join(pd.Series([str(id(peak_table)) for x in range(
            peak_table.peak_data.shape[1])], name="obs_id"))
        full_df = pd.concat([full_df, peak_table.peak_data])
    upper = None
    lower = None
    c = 0
    group_dict = {}
    full_df.sort_values(by="R.Time", axis=0, inplace=True)
    full_df.reset_index(inplace=True, drop=True)

    def group_within_error(dataframe: pd.DataFrame, index, col):
        nonlocal upper, lower, error, c, group_dict
        if upper is None or lower is None:
            upper = dataframe.iloc[index, col] + 2 * error
            lower = dataframe.iloc[index, col]
            c = c + 1
            group_dict[lower] = c
        if dataframe.iloc[index, col] <= upper and dataframe.iloc[index, col] >= lower:
            return "Group" + str(group_dict[lower])
        else:
            upper = dataframe.iloc[index, col] + 2 * error
            lower = dataframe.iloc[index, col]
            c = c + 1
            group_dict[lower] = c
            return "Group" + str(group_dict[lower])

    grouped_by = full_df.groupby(lambda x: group_within_error(full_df, x, 1))
    return grouped_by


def __predict_peak_from_compound_dict(value, cmpd_dict, depth=1):
    for k, v in cmpd_dict.items():
        if value.between(v[0] - v[1] * depth, v[0] + v[1] * depth).all():
            return k


def __assign_hplccalibratiion_curve_class(guess_dict, name):
    if guess_dict.get(name) is not None:
        for cls in HPLCCalibrationCurve.__subclasses__():
            if guess_dict.get(name) in str(cls):
                return cls()
        return HPLCCalibrationCurve()
    else:
        return HPLCCalibrationCurve()


def make_standards(grouped_by, knowns: typing.Dict[str, typing.List[float]], cmpd_dict: dict = None):
    standards = []
    cpd_guess = pd.Series()
    if cmpd_dict is not None:
        cpd_guess = grouped_by["R.Time"].aggregate(lambda x: __predict_peak_from_compound_dict(x, cmpd_dict=cmpd_dict))
        print(cpd_guess)
    for x, y in grouped_by:
        if knowns.get(x) is not None:
            std_df = y[["Height", "Area"]].sort_values(by="Area", ascending=False).reset_index(drop=True)
            std_df.rename(columns={"Height": "height", "Area": "area"}, inplace=True)
            std_df["known_concentration"] = pd.Series(knowns.get(x))
            cal_curve = __assign_hplccalibratiion_curve_class(cpd_guess, x)
            cal_curve.df = std_df
            cal_curve.processed_time = datetime.datetime.now()
            cal_curve.fit_linear_regression()
            cal_curve.set_standard_dev()
            cal_curve.stdev_rtimes = y["R.Time"].std()
            cal_curve.mean_rtimes = y["R.Time"].mean()
            standards.append(cal_curve)
    return standards
