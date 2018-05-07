import datetime
import pandas as pd
import statsmodels.api as sm
import abc


class CalibrationCurve:
    name = None

    def __init__(self, calibration_id: str = None, collection_time: datetime.datetime = None,
                 processed_time: datetime.datetime = None,
                 user: str = "", df: pd.DataFrame = None, stdev: float = None
                 ):
        self.calibration_id = calibration_id
        self.collection_time = collection_time
        self.processed_time = processed_time
        self.user = user
        self.df = df
        self.stdev = stdev
        self.r_squared = None
        self.params = None
        self.regression = None

    @abc.abstractmethod
    def fit_linear_regression(self, x_raw=None, y_raw=None, set_fields=True):
        if x_raw is None:
            x = sm.add_constant(self.df[self.name])
        else:
            x = sm.add_constant(x_raw)
        if y_raw is None:
            y = self.df["known_concentration"]
        else:
            y = y_raw
        model = sm.OLS(y, x)
        result = model.fit()
        if set_fields:
            self.regression = result
            self.r_squared = result.rsquared
            self.params = result.params
        else:
            return result

    @abc.abstractmethod
    def load_curve_csv(self, filename: str):
        pass

    @abc.abstractmethod
    def set_standard_dev(self):
        pass


class UVSpecCalibration(CalibrationCurve):
    name = None

    def __init__(self):
        CalibrationCurve.__init__(self)

    def load_curve_csv(self, filename):
        raw_df = pd.read_csv(filename)
        raw_df.rename(columns={"measurement": self.name}, inplace=True)
        self.df = raw_df
        self.processed_time = datetime.datetime.now()
        return

    def fit_linear_regression(self, x_raw=None, y_raw=None, set_fields=True):
        CalibrationCurve.fit_linear_regression(self, set_fields=set_fields)

    def set_standard_dev(self):
        if self.df is not None and self.name is not None:
            self.stdev = self.df[self.name].std()
        else:
            self.stdev = None


class HPLCCalibrationCurve(CalibrationCurve):
    name = None

    def __init__(self):
        CalibrationCurve.__init__(self)
        self.fitted_to = ""
        self.stdev_rtimes = None
        self.mean_rtimes = None

    def load_curve_csv(self, filename):
        raw_df = pd.read_csv(filename)
        self.df = raw_df
        self.processed_time = datetime.datetime.now()
        return

    def fit_linear_regression(self, x_raw=None, y_raw=None, set_fields=True):
        height_result = CalibrationCurve.fit_linear_regression(self, x_raw=self.df["height"], set_fields=False)
        area_result = CalibrationCurve.fit_linear_regression(self, x_raw=self.df["area"], set_fields=False)
        if height_result.rsquared >= area_result.rsquared:
            print("Height has a better curve. R^2: ", height_result.rsquared)
            self.r_squared = height_result.rsquared
            self.regression = height_result
            self.params = height_result.params
            self.fitted_to = "height"

        else:
            print("Area has a better curve. R^2: ", area_result.rsquared)
            self.r_squared = area_result.rsquared
            self.regression = area_result
            self.params = area_result.params
            self.fitted_to = "area"

    def set_standard_dev(self):
        if self.fitted_to is "":
            print("Error")
            return
        self.stdev = self.df[self.fitted_to].std()


class AcetateCalibrationCurve(HPLCCalibrationCurve):
    name = "acetate"

    def __init__(self):
        HPLCCalibrationCurve.__init__(self)


class NitrateCalibrationCurve(HPLCCalibrationCurve):
    name = "nitrate"

    def __init__(self):
        HPLCCalibrationCurve.__init__(self)


class NitriteCalibrationCurve(HPLCCalibrationCurve):
    name = "nitrite"

    def __init__(self):
        HPLCCalibrationCurve.__init__(self)


class PhosphateCalibrationCurve(UVSpecCalibration):
    name = "phosphate"

    def __init__(self):
        UVSpecCalibration.__init__(self)
