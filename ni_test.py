import nidaqmx
import numpy as np
import time

def generate_sine_wave(sample_rate, frequency, duration, amplitude=5.0):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    return amplitude * np.sin(2 * np.pi * frequency * t)

def analog_output(task_name, channel, data, sample_rate):
    with nidaqmx.Task(task_name) as task:
        task.ao_channels.add_ao_voltage_chan(channel, min_val=-10.0, max_val=10.0)
        task.timing.cfg_samp_clk_timing(rate=sample_rate, sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)
        task.write(data, auto_start=False)
        task.start()
        time.sleep(len(data) / sample_rate)
        task.stop()

def analog_input(task_name, channel, sample_rate, duration):
    num_samples = int(sample_rate * duration)
    with nidaqmx.Task(task_name) as task:
        task.ai_channels.add_ai_voltage_chan(channel, min_val=-10.0, max_val=10.0)
        task.timing.cfg_samp_clk_timing(rate=sample_rate, sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)
        data = task.read(number_of_samples_per_channel=num_samples)
        return np.array(data)

def main():
    sample_rate = 1000.0  # Samples per second
    frequency = 1.0       # Frequency of the sine wave
    duration = 5.0        # Duration in seconds

    # Generate waveform data
    output_data = generate_sine_wave(sample_rate, frequency, duration)

    # Perform Analog Output
    ao_channel = "cDAQ1Mod1/ao0"
    print("Starting Analog Output...")
    analog_output("AnalogOutputTask", ao_channel, output_data, sample_rate)
    print("Analog Output Completed")

    # Perform Analog Input
    ai_channel = "cDAQ1Mod1/ai0"
    print("Starting Analog Input...")
    input_data = analog_input("AnalogInputTask", ai_channel, sample_rate, duration)
    print("Analog Input Completed")
    
    # Display Input Data
    print("Input Data:")
    print(input_data)

if __name__ == "__main__":
    main()
