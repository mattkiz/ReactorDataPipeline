import pandas as pd
from .sample_types import CalibrationCurve
import datetime
import os


def read_data_file(filename):
    try:
        file = open(filename)
        file_string = file.read()
        return file_string
    except FileNotFoundError:
        print(filename + " not found.")
        return None


def read_standards(directory):
    file_str_list = []
    for filename in os.listdir(directory):
        file_str_list.append(read_data_file(directory + "/" + filename))
    return file_str_list
