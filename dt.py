import time
import sched
import qcodes as qc
from qcodes.instrument_drivers.Keysight import Keysight34461A

# Initialize the instrument
visa_addr = "USB0::0x0957::0x1A07::MY53206340::INSTR"
dmm = Keysight34461A('dmm', visa_addr)
dmm.display.enabled(False)

# Configure measurement settings if needed
# dmm.range.set(10)  # 10 volts range
# dmm.resolution.set(0.0001)  # 100 µV resolution
# dmm.NPLC.set(0.02)  # Minimum integration time within allowed range
# dmm.autozero.set('OFF')

# Measurement frequency and interval
measurement_frequency = 20  # Hz
expected_interval = 1 / measurement_frequency

# Initialize scheduler
scheduler = sched.scheduler(time.time, time.sleep)

# Start measurements
num_measurements = 300
voltages = []
start_time = time.time()

def take_measurement(sc, counter):
    try:
        voltage = dmm.volt.get()
        voltages.append(voltage)
    except Exception as e:
        pass  # Handle error if necessary

    if counter < num_measurements:
        sc.enter(expected_interval, 1, take_measurement, (sc, counter + 1))

# Schedule the first measurement
scheduler.enter(0, 1, take_measurement, (scheduler, 1))
scheduler.run()

end_time = time.time()
elapsed_time = end_time - start_time

# Calculate actual Hertz
actual_hertz = num_measurements / elapsed_time

# Output results
print(f"Total time for {num_measurements} measurements: {elapsed_time:.4f} seconds")
print(f"Expected Hertz: {measurement_frequency} Hz")
print(f"Actual Hertz: {actual_hertz:.2f} Hz")
print(f"Average time per measurement: {elapsed_time / num_measurements:.4f} seconds")

# Close the connection to the instrument
dmm.close()
