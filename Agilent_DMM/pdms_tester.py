import time
import qcodes as qc
from qcodes.instrument_drivers.Keysight import Keysight34461A
import matplotlib.pyplot as plt
from collections import deque
import pandas as pd
from datetime import datetime
import signal
import threading

class AgilentDMM:
    def __init__(self, visa_addr):
        """
        Initialize the AgilentDMM class with the given VISA address.
        
        Parameters:
            visa_addr (str): The VISA address of the instrument.
        """
        self.visa_addr = visa_addr
        self.dmm = None
        self.data = {'timestamp': [], 'voltage': []}

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

    def save_data(self, filename):
        """Save data to a CSV file."""
        df = pd.DataFrame(self.data)
        df.to_csv(filename, index=False)
        print(f"Data saved to {filename}")

    def handle_exit(self, signum, frame):
        """Handle exit signal to save data and close connection."""
        self.save_data(self.csv_filename)
        self.close()
        print("Process interrupted, exiting gracefully.")
        exit(0)

    def wait_for_user_input(self):
        """Wait for user input to stop the test."""
        input("Press Enter to stop the test...\n")
        self.stop_flag.set()

    def run_test(self, measurement_frequency, test_time, max_points=100):
        """
        Run the test to measure and plot voltages live until user interruption or max duration.
        
        Parameters:
            measurement_frequency (int or float): The measurement frequency in Hertz.
            test_time (int or float): The maximum duration of the test in seconds.
            max_points (int): The maximum number of points to display on the plot.
        """
        if self.dmm is None:
            raise ValueError("Instrument not initialized. Call setup_instrument() first.")
        
        sleep_interval = 1 / measurement_frequency

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
        times = deque(maxlen=max_points)
        voltages = deque(maxlen=max_points)

        # Prepare for data storage
        start_time = time.time()
        start_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.csv_filename = f"PDMS_Test_{start_datetime}.csv"
        
        # Register signal handler for graceful exit
        signal.signal(signal.SIGINT, self.handle_exit)
        signal.signal(signal.SIGTERM, self.handle_exit)

        # Flag to stop the main loop
        self.stop_flag = threading.Event()

        # Start the thread to wait for user input
        input_thread = threading.Thread(target=self.wait_for_user_input)
        input_thread.start()

        try:
            # Main loop for continuous data acquisition
            while not self.stop_flag.is_set() and time.time() - start_time < test_time:
                # Query the instrument for DC voltage measurement
                volts = float(self.dmm.volt())

                # Get the current timestamp
                current_time = time.time()

                # Append the current measurement and time to deques and data dictionary
                voltages.append(volts)
                times.append(current_time - start_time)  # Relative time
                self.data['timestamp'].append(datetime.fromtimestamp(current_time).strftime("%Y-%m-%d %H:%M:%S.%f"))
                self.data['voltage'].append(volts)

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

        except Exception as e:
            print(f"An error occurred: {e}")

        finally:
            self.save_data(self.csv_filename)
            self.close()

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
        test_time = 9800  # seconds (e.g., 3 hours)

        # Run the test with live plotting
        dmm.run_test(measurement_frequency, test_time)

    except Exception as e:
        print(f"Failed to perform measurements: {e}")

    finally:
        dmm.close()
