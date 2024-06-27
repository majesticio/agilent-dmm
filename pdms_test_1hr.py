import pyvisa as visa
import time
import matplotlib.pyplot as plt
import pandas as pd
from collections import deque
from datetime import datetime

# Import setup_instrument from your module
from beta import setup_instrument

# test_time = 3600 # 1 hr test
test_time = 60     # 1 min test run

# Measurement frequency in Hertz
measurement_frequency = 10  # Hz, change this to your desired frequency

# Initialize the instrument as 'dmm'
visa_addr = "USB0::0x0957::0x1A07::MY53206340::INSTR"
dmm = setup_instrument(visa_addr)

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

# Prepare for data storage
data = {'timestamp': [], 'voltage': []}

start_time = time.time()
start_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

csv_filename = f"PDMS_Test_{start_datetime}.csv"

try:
    # Main loop for continuous data acquisition
    while time.time() - start_time < test_time:  # Run for one hour
        # Query the instrument for DC voltage measurement
        volts = float(dmm.volt())

        # Get the current timestamp
        current_time = time.time()

        # Append the current measurement and time to deques and data dictionary
        voltages.append(volts)
        times.append(current_time - start_time)  # Relative time
        data['timestamp'].append(datetime.fromtimestamp(current_time).strftime("%Y-%m-%d %H:%M:%S.%f"))
        data['voltage'].append(volts)

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

    # Convert the data dictionary to a DataFrame
    df = pd.DataFrame(data)

    # Save the DataFrame to a CSV file
    df.to_csv(csv_filename, index=False)
    print(f"Data saved to {csv_filename}")

except visa.VisaIOError as e:
    print(f"VISA error: {e}")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Close the connection to the instrument, if open
    if 'dmm' in locals():
        dmm.close()
        print("Connection to DMM closed.")
