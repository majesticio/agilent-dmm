import keysight_kt34400 as m
import time
import datetime

def initialize_driver(resource_name, idQuery=True, reset=True, options="QueryInstrStatus=False, Simulate=True, Trace=False"):
    """
    Initialize the Keysight driver with the given resource name and options.
    """
    try:
        driver = m.Kt34400(resource_name, idQuery, reset, options)
        print("Driver Initialized")
        print('Identifier: ', driver.identity.identifier)
        print('Revision:   ', driver.identity.revision)
        print('Vendor:     ', driver.identity.vendor)
        print('Description:', driver.identity.description)
        print('Model:      ', driver.identity.instrument_model)
        print('Resource:   ', driver.driver_operation.io_resource_descriptor)
        print('Options:    ', driver.driver_operation.driver_setup)
        return driver
    except Exception as e:
        print("Error initializing driver:", e)
        return None

def configure_dc_voltage_measurement(driver, range_val=10, resolution=m.Resolution.MAX):
    """
    Configure the driver for DC voltage measurement.
    """
    driver.utility.reset()
    driver.trigger.source = m.TriggerSource.IMMEDIATE
    driver.dc_voltage.configure(range_val, resolution)

def measure_voltage(driver, num_measurements=10, interval=0.1):
    """
    Measure voltage at specified intervals and return the results.
    """
    measurements = []
    start_time = datetime.datetime.now()

    try:
        for _ in range(num_measurements):
            data = driver.measurement.read()
            elapsed_time = (datetime.datetime.now() - start_time).total_seconds()
            measurements.append((elapsed_time, data))
            print(f"Time: {elapsed_time:.2f} s, Voltage: {data:.6f} V")
            time.sleep(interval)
    except Exception as e:
        print("Error during measurement:", e)

    return measurements

def main():
    resource_name = "MyVisaAlias"
    driver = initialize_driver(resource_name)

    if driver:
        configure_dc_voltage_measurement(driver)

        measurements = measure_voltage(driver)

        print("\nAll measurements completed:")
        for timestamp, voltage in measurements:
            print(f"Time: {timestamp:.2f} s, Voltage: {voltage:.6f} V")

        try:
            while True:
                error_code, error_message = driver.utility.error_query()
                print(f"Error query: code: {error_code}, message: {error_message}")
                if error_code == 0:
                    break
        except Exception as e:
            print("Error querying instrument errors:", e)
        finally:
            driver.close()
            print("Driver closed")

if __name__ == "__main__":
    main()
