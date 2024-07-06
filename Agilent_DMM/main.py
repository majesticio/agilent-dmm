from agilent_dmm import AgilentDMM
import argparse

parser = argparse.ArgumentParser(description="Run voltage measurement test with Agilent DMM.")
parser.add_argument('--config', type=str, default='config.yaml', help="Path to the configuration file.")
args = parser.parse_args()

config = AgilentDMM.load_config(args.config)

dmm = AgilentDMM(config)

dmm.setup_instrument()
measurement_frequency = config.get('measurement_frequency', 10)  # Default to 10 Hz
test_time = config.get('test_time', 9800)  # Default to 9800 seconds
max_points = config.get('max_points', 100)  # Default to 100 points

# Run the test with live plotting
# dmm.run_test(measurement_frequency, test_time, max_points) # <- NEEDS WORK
# print(dmm.measure_voltages(10, 10)) # (f, D) seems to work 
dmm.live_plot_voltages(10) # seems to work, RENAME?

