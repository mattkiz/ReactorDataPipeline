import datetime
import pandas as pd
import statsmodels.api as sm
from .calibration_curve_types import *


class Sample:
    def __init__(self, collection_time: datetime.datetime = None, processed_time: datetime.datetime = None,
                 user: str = "", reactor: str = ""):
        self.collection_time = collection_time
        self.processed_time = processed_time
        self.user = user
        self.reactor = reactor


class MetaboliteSample(Sample):
    formula = None
    molar_mass = None
    charge = None
    name = None

    def __init__(self, calibration_id: str = "", raw_data_point: int = None, concentration_mgl: int = None,
                 concentration_mmol: int = None, normalized_concentration: int = None, biomass_collected: bool = None):
        Sample.__init__(self)
        self.calibration_id = calibration_id
        self.raw_data_point = raw_data_point
        self.concentration_mgL = concentration_mgl
        self.concentration_mmol = concentration_mmol
        self.normalized_concentration = normalized_concentration
        self.biomass_collected = biomass_collected

    def compute_mgl_to_mmol(self):
        if self.concentration_mgL is not None and self.molar_mass is not None:
            self.concentration_mmol = self.concentration_mgL / self.molar_mass

    def compute_conc_from_curve(self, curve: CalibrationCurve, param_name=None):
        if param_name is None:
            self.concentration_mgL = curve.params[self.name] * self.raw_data_point + curve.params["const"]
        else:
            self.concentration_mgL = curve.params[param_name] * self.raw_data_point + curve.params["const"]
        self.compute_mgl_to_mmol()


class PhosphateSample(MetaboliteSample):
    formula = {"P": 1, "O": 4}
    molar_mass = 94.9714
    charge = -3
    name = "phosphate"

    def __init__(self, dilution: int = 1):
        MetaboliteSample.__init__(self)
        self.dilution = dilution


class AcetateSample(MetaboliteSample):
    formula = {"C": 2, "H": 3, "O": 2}
    molar_mass = 59.04
    charge = -1
    name = "acetate"

    def __init__(self):
        MetaboliteSample.__init__(self)

    def compute_conc_from_curve(self, curve: AcetateCalibrationCurve, param_name=None):
        MetaboliteSample.compute_conc_from_curve(self, curve, param_name=curve.fitted_to)
