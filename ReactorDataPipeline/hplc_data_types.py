import pandas as pd


class PeakTableData:
    """
    This class repersents HPLC data as a single peak table for a given detector.
    """

    def __init__(self, detector_name: str, peak_data: pd.DataFrame = None):
        """
        HPLCData constructor
        """
        self.detector_name = detector_name  # name of the detector used
        self.peak_data = peak_data  # List of PeakData objects that are initialized by processed_raw_peak_data
        self.wavelength = None
        if self.peak_data is not None:
            self.number_of_peaks = peak_data.shape[0]  # Number of peaks detected
        else:
            self.number_of_peaks = None

    def __str__(self):
        return str(self.peak_data)
