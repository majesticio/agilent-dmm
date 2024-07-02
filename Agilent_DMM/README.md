# Agilent DMM Voltage Measurement

## Overview

This library provides a Python class `AgilentDMM` to interface with an Agilent Digital Multimeter (DMM) for voltage measurements. It includes functionalities for setting up the instrument, measuring voltages at a specified frequency, live plotting of voltage measurements, and saving the data to a CSV file. The project also handles graceful termination of the measurement process with signal handling and user input.

## Features

- **Setup and configure** the Agilent DMM (Keysight34461A)
- **Measure voltages** at a specified frequency and duration
- **Live plot** the voltage measurements
- **Save measurement data** to a CSV file
- **Handle exit signals** to gracefully stop the measurements and save data

## Requirements

- Python 3.x
- qcodes
- PyYAML
- matplotlib
- pandas

## Usage

### Configuration

Create or update a `config.yaml` file with the following structure:

```yaml
visa_addr: 'USB0::0x0957::0x1A07::MY53206340::INSTR'  # VISA address
log_file: 'dmm_test.log'
measurement_frequency: 10  # Measurement frequency in Hz
test_time: 9800  # Test duration in seconds
max_points: 100  # Maximum points to display on the plot
```

### Running the Script

You can run the script from the command line with the following command:

```bash
python agilent_dmm.py --config config.yaml
```

### Example Code

Here's an example of how to import and use the `AgilentDMM` class in your own script:

```python
import yaml
from agilent_dmm import AgilentDMM

# Load configuration from YAML file
config_file = 'config.yaml'
with open(config_file, 'r') as f:
    config = yaml.safe_load(f)

# Initialize the DMM with the configuration
dmm = AgilentDMM(config)

try:
    # Setup the instrument
    dmm.setup_instrument()
    
    # Set measurement parameters
    measurement_frequency = config.get('measurement_frequency', 10)
    test_time = config.get('test_time', 9800)
    max_points = config.get('max_points', 100)
    
    # Run the test with live plotting
    dmm.run_test(measurement_frequency, test_time, max_points)

except Exception as e:
    print(f"Error: {e}")

finally:
    # Ensure the instrument is properly closed
    dmm.close()
```

### Methods Overview

- **`__init__(self, config)`**: Initializes the AgilentDMM class with the given configuration.
- **`load_config(config_file)`**: Loads configuration from a YAML file.
- **`setup_instrument(self)`**: Sets up the Keysight34461A instrument.
- **`measure_voltages(self, measurement_frequency, duration)`**: Measures voltages at the specified frequency and duration.
- **`live_plot_voltages(self, measurement_frequency, max_points=100)`**: Live plots voltages using the DMM at the specified frequency.
- **`save_data(self, filename)`**: Saves data to a CSV file.
- **`handle_exit(self, signum, frame)`**: Handles exit signal to save data and close connection.
- **`wait_for_user_input(self)`**: Waits for user input to stop the test.
- **`run_test(self, measurement_frequency, test_time, max_points=100)`**: Runs the test to measure and plot voltages live until user interruption or max duration.
- **`close(self)`**: Closes the connection to the DMM.

## Logging

The script uses Python's `logging` module to log messages to a file specified in the configuration file (`log_file`). The log includes timestamps, log levels, and messages to help with debugging and tracking the measurement process.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

This project uses the following open-source libraries:
- [qcodes](https://github.com/QCoDeS/Qcodes)
- [PyYAML](https://github.com/yaml/pyyaml)
- [matplotlib](https://matplotlib.org/)
- [pandas](https://pandas.pydata.org/)

---

Feel free to customize this README to better fit your project's specifics. This template provides a clear and structured overview of your project's purpose, usage, and setup instructions.