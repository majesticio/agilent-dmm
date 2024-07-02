
"""
This test will run until the user presses ENTER
or the max duration (test_time) is reached. 

Will write CSV file with 'timestamp' and 'voltage' values
"""

import pyvisa as visa
import time
import matplotlib.pyplot as plt
import pandas as pd
from collections import deque
from datetime import datetime
import signal
import threading

# Import setup_instrument from your module
from beta import setup_instrument
# Max Duration of the test
# test_time = 3600  # 1 hour
test_time = 9800  # 3 hour
# test_time = 7200  # 2 hour

print(f"running test for {test_time} seconds...")
# test_time = 60  # 1 minute for testing

# Measurement frequency in Hertz
measurement_frequency = 10  # Hz
sleep_interval = 1 / measurement_frequency  # Calculate the sleep interval

# Initialize the instrument
visa_addr = "USB0::0x0957::0x1A07::MY53206340::INSTR"
dmm = setup_instrument(visa_addr)

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

def save_data():
    """Function to save data to CSV."""
    df = pd.DataFrame(data)
    df.to_csv(csv_filename, index=False)
    print(f"Data saved to {csv_filename}")

def handle_exit(signum, frame):
    """Handle exit signal to save data and close connection."""
    save_data()
    if 'dmm' in locals():
        dmm.close()
        print("Connection to DMM closed.")
    print("Process interrupted, exiting gracefully.")
    exit(0)

# Register signal handler for graceful exit
signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

# Flag to stop the main loop
stop_flag = threading.Event()

def wait_for_user_input():
    """Wait for user input to stop the test."""
    input("Press Enter to stop the test...\n")
    stop_flag.set()

# Start the thread to wait for user input
input_thread = threading.Thread(target=wait_for_user_input)
input_thread.start()

try:
    # Main loop for continuous data acquisition
    while not stop_flag.is_set() and time.time() - start_time < test_time:
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

except visa.VisaIOError as e:
    print(f"VISA error: {e}")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    save_data()
    # Close the connection to the instrument, if open
    if 'dmm' in locals():
        dmm.close()
        print("Connection to DMM closed.")
