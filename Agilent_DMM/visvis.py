import pyvisa as visa
import time
import matplotlib.pyplot as plt
from collections import deque

# Import setup_instrument from your module
from beta import setup_instrument

# Initialize the instrument
visa_addr = "USB0::0x0957::0x1A07::MY53206340::INSTR"
dmm = setup_instrument(visa_addr)

# Measurement frequency in Hertz
measurement_frequency = 90  # Hz, change this to your desired frequency
sleep_interval = 1 / measurement_frequency  # Calculate the sleep interval

# Initialize plot
plt.ion()  # Turn on interactive mode
fig, ax = plt.subplots()
line, = ax.plot([], [], 'b-', label='Voltage (V)')
ax.set_xlabel('Time (s)')
ax.set_ylabel('Voltage (V)')
ax.set_title('Live Voltage Measurement')
ax.grid(True)
ax.legend()

# Initialize deque for storing data
max_points = 100  # Adjust based on how many points you want to display
times = deque(maxlen=max_points)
voltages = deque(maxlen=max_points)

try:
    # Main loop for continuous data acquisition
    start_time = time.time()
    while True:
        # Query the instrument for DC voltage measurement
        volts = float(dmm.volt())

        # Append the current measurement and time to deques
        voltages.append(volts)
        times.append(time.time() - start_time)  # Relative time

        # Update plot data
        line.set_data(times, voltages)

        # Adjust plot limits
        ax.relim()
        ax.autoscale_view()

        # Redraw the plot
        fig.canvas.draw()
        fig.canvas.flush_events()

        # Pause for the sleep interval to control measurement frequency
        time.sleep(sleep_interval)

except visa.VisaIOError as e:
    print(f"VISA error: {e}")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Close the connection to the instrument, if open
    if 'dmm' in locals():
        dmm.close()
        print("Connection to DMM closed.")
