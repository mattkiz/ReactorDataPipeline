from ReactorDataPipeline import *
import re
import pandas as pd
import io

file_strs = read_standards("testing_data/Standards")
parsed_data = get_all_raw_hplc_data(file_strs)
total_standards = process_multiple_samples(parsed_data)
cpd_dict = {"Nitrate": (2.42, .05), "Acetate": (3.90, 0.15)}
like_peaks_210 = find_like_peaks([std for std in total_standards if std.wavelength == 210], 0.05)
like_peaks_214 = find_like_peaks([std for std in total_standards if std.wavelength == 214], 0.05)

cal_curves_210 = make_standards(like_peaks_210, {"Group3": [25.0, 12.5, 6.25, 3.125],
                                                 "Group4": [25.0, 12.5, 6.25, 3.125],
                                                 "Group5": [400, 200, 100, 50]}, cmpd_dict=cpd_dict)
cal_curves_214 = make_standards(like_peaks_214, {"Group3": [25.0, 12.5, 6.25, 3.125],
                                                 "Group4": [25.0, 12.5, 6.25, 3.125],
                                                 "Group5": [400, 200, 100, 50]})
print(cal_curves_210)
print(HPLCCalibrationCurve.__subclasses__())
