import nidaqmx
import time
import matplotlib.pyplot as plt
from collections import deque

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

# Initialize NI-DAQmx task
# ai_channel = "SimDev1/ai0"  # Replace with your actual AI channel
ai_channel = "SimDev1/ai2"  # Replace with your actual AI channel

task = nidaqmx.Task()

try:
    # Add an analog input voltage channel
    task.ai_channels.add_ai_voltage_chan(ai_channel, min_val=-10.0, max_val=10.0)
    
    # Main loop for continuous data acquisition
    start_time = time.time()
    while True:
        # Read voltage measurement from the AI channel
        volts = task.read()

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

except nidaqmx.errors.DaqError as e:
    print(f"NI-DAQmx error: {e}")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Close the NI-DAQmx task
    task.close()
    print("Connection to NI-DAQmx task closed.")
