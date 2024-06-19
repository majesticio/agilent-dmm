import time
import qcodes as qc
from qcodes.instrument_drivers.Keysight import Keysight34461A

def setup_instrument(visa_addr):
    """
    Setup the Keysight34461A instrument.
    
    Parameters:
        visa_addr (str): The VISA address of the instrument.
    
    Returns:
        Keysight34461A: The initialized instrument object.
    """
    try:
        dmm = Keysight34461A('dmm', visa_addr)
        dmm.autorange_once()
        dmm.trigger.source('IMM')
        dmm.trigger.delay(0.0)
        dmm.display.enabled(False)
        dmm.range.set(10)  # 10 volts range
        dmm.NPLC.set(0.02)  # Minimum integration time for faster measurements
        dmm.autozero.set('OFF')
        return dmm
    except Exception as e:
        print(f"Error initializing the instrument: {e}")
        raise

def measure_voltages(dmm, measurement_frequency, duration):
    """
    Measure voltages using the given DMM at the specified frequency and duration.
    
    Parameters:
        dmm (Keysight34461A): The instantiated DMM instrument object.
        measurement_frequency (int or float): The measurement frequency in Hertz.
        duration (int or float): The duration of the measurement in seconds.
    
    Returns:
        list of dict: A list of timestamped voltage readings {'timestamp': timestamp, 'voltage': voltage}.
    """
    expected_interval = 1 / measurement_frequency
    end_time = time.perf_counter() + duration
    readings = []

    next_time = time.perf_counter()
    while time.perf_counter() < end_time:
        try:
            voltage = dmm.volt()
            timestamp = time.time()
            readings.append({'timestamp': timestamp, 'voltage': voltage})
        except Exception as e:
            print(f"Error during measurement: {e}")

        next_time += expected_interval
        sleep_time = next_time - time.perf_counter()
        if sleep_time > 0:
            time.sleep(sleep_time)

    return readings

if __name__ == "__main__":
    visa_addr = "USB0::0x0957::0x1A07::MY53206340::INSTR"
    try:
        dmm = setup_instrument(visa_addr)

        measurement_frequency = 25  # Hz
        duration = 1  # second

        readings = measure_voltages(dmm, measurement_frequency, duration)
        
        for reading in readings:
            print(reading)

        dmm.close()
    except Exception as e:
        print(f"Failed to perform measurements: {e}")
