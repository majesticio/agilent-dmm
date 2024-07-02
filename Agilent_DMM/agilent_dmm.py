import yaml
import argparse
import logging
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
    def __init__(self, config):
        """
        Initialize the AgilentDMM class with the given configuration.
        
        Parameters:
            config (dict): Configuration dictionary.
        """
        self.visa_addr = config['visa_addr']
        self.dmm = None
        self.data = pd.DataFrame(columns=['timestamp', 'voltage'])
        self.csv_filename = ""
        self.log_file = config.get('log_file', 'dmm_test.log')
        
        # Set up logging
        logging.basicConfig(filename=self.log_file, level=logging.INFO, 
                            format='%(asctime)s - %(levelname)s - %(message)s')

    @staticmethod
    def load_config(config_file):
        """Load configuration from a YAML file."""
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        return config

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
            logging.info("Instrument setup successfully.")
        except Exception as e:
            logging.error(f"Error initializing the instrument: {e}")
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
                logging.error(f"Error during measurement: {e}")

            next_time += expected_interval
            sleep_time = next_time - time.perf_counter()
            if sleep_time > 0:
                time.sleep(sleep_time)

        return readings

    def live_plot_voltages(self, measurement_frequency, max_points=100):
        """
        Live plot voltages using the DMM at the specified frequency.
        
        Parameters:
            measurement_frequency (int or float): The measurement frequency in Hertz.
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

        try:
            # Main loop for continuous data acquisition
            start_time = time.time()
            while True:
                # Query the instrument for DC voltage measurement
                volts = float(self.dmm.volt())

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

        except Exception as e:
            logging.error(f"An error occurred during live plotting: {e}")

        finally:
            # Close the connection to the instrument
            self.close()
            logging.info("Connection to DMM closed.")

    def save_data(self, filename):
        """Save data to a CSV file."""
        self.data.to_csv(filename, index=False)
        logging.info(f"Data saved to {filename}")

    def handle_exit(self, signum, frame):
        """Handle exit signal to save data and close connection."""
        self.save_data(self.csv_filename)
        self.close()
        logging.info("Process interrupted, exiting gracefully.")
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

                # Append the current measurement and time to deques and data DataFrame
                voltages.append(volts)
                times.append(current_time - start_time)  # Relative time
                self.data = self.data.append({'timestamp': datetime.fromtimestamp(current_time).strftime("%Y-%m-%d %H:%M:%S.%f"), 'voltage': volts}, ignore_index=True)

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
            logging.error(f"An error occurred during the test: {e}")

        finally:
            self.save_data(self.csv_filename)
            self.close()

    def close(self):
        """
        Close the connection to the DMM.
        """
        if self.dmm is not None:
            self.dmm.close()
            logging.info("Connection to DMM closed.")
        else:
            logging.warning("Instrument already closed or not initialized.")

def main():
    parser = argparse.ArgumentParser(description="Run voltage measurement test with Agilent DMM.")
    parser.add_argument('--config', type=str, default='config.yaml', help="Path to the configuration file.")
    args = parser.parse_args()

    config = AgilentDMM.load_config(args.config)

    dmm = AgilentDMM(config)

    try:
        dmm.setup_instrument()
        measurement_frequency = config.get('measurement_frequency', 10)  # Default to 10 Hz
        test_time = config.get('test_time', 9800)  # Default to 9800 seconds
        max_points = config.get('max_points', 100)  # Default to 100 points

        # Run the test with live plotting
        dmm.run_test(measurement_frequency, test_time, max_points)

    except Exception as e:
        logging.error(f"Failed to perform measurements: {e}")

    finally:
        dmm.close()

if __name__ == "__main__":
    main()
