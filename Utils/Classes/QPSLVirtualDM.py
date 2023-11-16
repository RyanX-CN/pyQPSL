from QPSLClass.Base import *


class QPSLVirtualDM:

    def __init__(self) -> None:
        super(QPSLVirtualDM, self).__init__()
        self.m_state = False
        self.m_map_loaded = False
        self.m_error_strings = [
            "No error.", "Uknown error.", "No hardware found.",
            "Error initializing connection to hardware.",
            "An invalid serial number was entered.",
            "Error allocating memory.", "Invalid driver type.",
            "Invalid number of actuators.", "Invalid mapping lookup table.",
            "Invalid actuator ID.", "Error opening file.",
            "Function not available in this configuration.",
            "Operation timed out.", "Error poking actuator.",
            "Error reading value from system registry.",
            "Error writing PCIe board register.",
            "Error reading PCIe board register.", "Error writing burst array.",
            "Function Only available on 64-bit OS.",
            "Sync pulse out of range.", "Invalid sequence array received.",
            "Invalid sequence rate received.", "Invalid dither waveform.",
            "Invalid dither gains.", "Invalid dither rate.", "Bad argument.",
            "Invalid segment ID.", "Calibration not loaded or invalid.",
            "Value not found in lookup table.",
            "Driver not initialized; must open driver first.",
            "Driver already open; must close driver first.",
            "Error reading or writing file due to OS permissions.",
            "Error reading file; it was formatted incorrectly.",
            "Error reading from USB.", "Error writing to USB.",
            "Unknown USB error."
        ]

    def get_state(self):
        return self.m_state

    def BMCOpen(self, serial_number: str):
        assert not self.m_state
        self.m_state = True
        self.m_map_loaded = False

    def BMCClose(self):
        assert self.m_state
        self.m_state = False

    def is_opened(self):
        return self.m_state

    def BMCLoadMap(self):
        assert self.m_state
        self.m_map_loaded = True

    def is_map_loaded(self):
        assert self.m_state
        return self.m_map_loaded

    def BMCSetArray(self, double_arr: List[float]):
        assert self.m_state
        assert self.m_map_loaded
        pass

    def translate_error_code(self, error_code: int):
        return self.m_error_strings[error_code]
