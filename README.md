# Agilent 34461a
----------
## Setup (windows)
`python -m pipenv shell`

## Plot live voltage
`python visvis.py`

## Usage
```
from beta import setup_instrument. measure_voltages

visa_addr = "USB0::0x0957::0x1A07::MY53206340::INSTR"

# Initialize the instrument
dmm = setup_instrument(visa_addr)

```

use `setup_instrument(visa_addr)` to initialize the DMM object and `measure_voltages(dmm, measurement_frequency, duration)` to do a session.
## Take a measurement
`dmm.volt()`


----------