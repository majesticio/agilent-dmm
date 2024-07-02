import time
import qcodes as qc
from qcodes.instrument_drivers.Keysight import Keysight34461A

class AgilentDMM:
    def __init__(self, visa_addr):
        """
        Initialize the AgilentDMM class with the given VISA address.
        
        Parameters:
            visa_addr (str): The VISA address of the instrument.
        """
        self.visa_addr = visa_addr
        self.dmm = None

    def setup_instrument(self):
        """
        Setup the Keysight34461A instrument.
        """
        try:
            self.dmm = Keysight34461A('dmm', self.visa_addr)
            self.dmm.autorange_once()
            self.dmm.trigger.source('IMM')
            self.dmm.trigger.delay(0.0)
            self.dmm.display.enabled(False)
            self.dmm.range.set(10)  # 10 volts range
            self.dmm.NPLC.set(0.02)  # Minimum integration time for faster measurements
            self.dmm.autozero.set('OFF')
            self.dmm.resolution.set(0.0001)
        except Exception as e:
            print(f"Error initializing the instrument: {e}")
            raise

    def measure_voltages(self, measurement_frequency, duration):
        """
        Measure voltages using the DMM at the specified frequency and duration.
        
        Parameters:
            measurement_frequency (int or float): The measurement frequency in Hertz.
            duration (int or float): The duration of the measurement in seconds.
        
        Returns:
            list of tuple: A list of timestamped voltage readings (timestamp, voltage).
        """
        if self.dmm is None:
            raise ValueError("Instrument not initialized. Call setup_instrument() first.")
        
        expected_interval = 1 / measurement_frequency
        end_time = time.perf_counter() + duration
        readings = []

        next_time = time.perf_counter()
        while time.perf_counter() < end_time:
            try:
                voltage = self.dmm.volt()
                timestamp = time.time()
                readings.append((timestamp, voltage))
            except Exception as e:
                print(f"Error during measurement: {e}")

            next_time += expected_interval
            sleep_time = next_time - time.perf_counter()
            if sleep_time > 0:
                time.sleep(sleep_time)

        return readings

    def close(self):
        """
        Close the connection to the DMM.
        """
        if self.dmm is not None:
            self.dmm.close()
        else:
            print("Instrument already closed or not initialized.")

# Example usage
if __name__ == "__main__":
    visa_addr = "USB0::0x0957::0x1A07::MY53206340::INSTR"
    dmm = AgilentDMM(visa_addr)

    try:
        dmm.setup_instrument()
        measurement_frequency = 10  # Hz
        duration = 1  # second

        readings = dmm.measure_voltages(measurement_frequency, duration)

        for reading in readings:
            print(reading)

    except Exception as e:
        print(f"Failed to perform measurements: {e}")

    finally:
        dmm.close()