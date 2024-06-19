import time
import qcodes as qc
from qcodes.instrument_drivers.Keysight import Keysight34461A

# Define the VISA address of the instrument
visa_addr = "USB0::0x0957::0x1A07::MY53206340::INSTR"

# Initialize the instrument
dmm = Keysight34461A('dmm', visa_addr)
dmm.device_clear()
dmm.autorange_once()
dmm.trigger.source('IMM')
# dmm.trigger.count(1)
dmm.trigger.delay(0.0)

dmm.display.enabled(False)

# Configure the range and resolution if needed
dmm.range.set(10)  # 10 volts range
# Disable autozero for faster measurements
dmm.autozero.set('OFF')

# Variable for measurement frequency (Hertz)
measurement_frequency = 100  # 25 Hz
expected_interval = 1 / measurement_frequency

voltages = []

# Measure voltage 25 times per second for a given duration (e.g., 1 second)
duration = 1  # seconds
start_time = time.time()
end_time = start_time + duration

while time.time() < end_time:
    voltage = dmm.volt()
    voltages.append(voltage)
    time.sleep(expected_interval)

# Close the connection to the instrument
dmm.close()

print(len(voltages), "voltages")
# print (start_time, end_time)
# print(dir(dmm))
# help(dmm)