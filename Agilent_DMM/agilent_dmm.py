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
        self.visa_addr = config['visa_addr']
        self.dmm = None
        self.data = {'timestamp': [], 'voltage': []}
        self.csv_filename = ""
        self.log_file = config.get('log_file', 'dmm_test.log')
        
        logging.basicConfig(filename=self.log_file, level=logging.INFO, 
                            format='%(asctime)s - %(levelname)s - %(message)s')

    @staticmethod
    def load_config(config_file):
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        return config

    def setup_instrument(self):
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

    def save_data(self):
        """Function to save data to CSV."""
        df = pd.DataFrame(self.data)
        df.to_csv(self.csv_filename, index=False)
        logging.info(f"Data saved to {self.csv_filename}")

    def handle_exit(self, signum=None, frame=None):
        """Handle exit signal to save data and close connection."""
        logging.info("Process interrupted, saving data and closing connections...")
        self.save_data()
        if self.dmm is not None:
            self.dmm.close()
            logging.info("Connection to DMM closed.")
        self.stop_flag.set()  # Ensure the thread stops
        plt.close('all')  # Close the plot
        logging.info("Exiting gracefully.")
        exit(0)

    def wait_for_user_input(self):
        """Wait for user input to stop the test."""
        input("Press Enter to stop the test...\n")
        self.stop_flag.set()

    def run_test(self, measurement_frequency, test_time, max_points=100):
        if self.dmm is None:
            raise ValueError("Instrument not initialized. Call setup_instrument() first.")
        
        sleep_interval = 1 / measurement_frequency

        plt.ion()  # Turn on interactive mode
        fig, ax = plt.subplots()
        line, = ax.plot([], [], 'b-', label='Voltage (V)')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Voltage (V)')
        ax.set_title('Live Voltage Measurement')
        ax.grid(True)
        ax.legend()

        times = deque(maxlen=max_points)
        voltages = deque(maxlen=max_points)

        start_time = time.time()
        start_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.csv_filename = f"PDMS_Test_{start_datetime}.csv"
        
        signal.signal(signal.SIGINT, self.handle_exit)
        signal.signal(signal.SIGTERM, self.handle_exit)

        self.stop_flag = threading.Event()
        input_thread = threading.Thread(target=self.wait_for_user_input)
        input_thread.start()

        try:
            while not self.stop_flag.is_set() and time.time() - start_time < test_time:
                volts = float(self.dmm.volt())
                current_time = time.time()

                voltages.append(volts)
                times.append(current_time - start_time)  # Relative time
                self.data['timestamp'].append(datetime.fromtimestamp(current_time).strftime("%Y-%m-%d %H:%M:%S.%f"))
                self.data['voltage'].append(volts)
                
                line.set_data(times, voltages)
                ax.relim()
                ax.autoscale_view()
                fig.canvas.draw()
                fig.canvas.flush_events()
                time.sleep(sleep_interval)

        except Exception as e:
            logging.error(f"An error occurred during the test: {e}")

        finally:
            self.handle_exit()

    def close(self):
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

        dmm.run_test(measurement_frequency, test_time, max_points)

    except Exception as e:
        logging.error(f"Failed to perform measurements: {e}")

    finally:
        dmm.close()

if __name__ == "__main__":
    main()
