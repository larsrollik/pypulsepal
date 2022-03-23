[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.6360738.svg)](https://doi.org/10.5281/zenodo.6360738)
[![Website](https://img.shields.io/website?up_message=online&url=https%3A%2F%2Fgithub.com/larsrollik/pypulsepal)](https://github.com/larsrollik/pypulsepal)
[![PyPI](https://img.shields.io/pypi/v/pypulsepal.svg)](https://pypi.org/project/pypulsepal)
[![Wheel](https://img.shields.io/pypi/wheel/pypulsepal.svg)](https://pypi.org/project/pypulsepal)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)


# PyPulsePal
Python API for the PulsePal open-source pulse train generator
---
This package provides an API to the [PulsePal] hardware.
This API is a re-implementation of the original [PulsePal Python 3 API] that draws from the `pybpod-api` communication protoool.

## Example usage

#### script/function
```python
from pypulsepal import PulsePal

serial_port = "/dev/ttyACM0"  # for unix or "COM"-style port names for Windows

# Create PulsePal object
pp = PulsePal(serial_port=serial_port)

# Set parameters

## Manually
pp.program_one_param(channel=2, param_name="phase1Duration", param_value=.002)

## Via convencience functions
pp.set_resting_voltage(channel=2, voltage=4.2)

# Upload parameters
pp.upload_all()

# Trigger channels
pp.trigger_selected_channels(channel_2=True, channel_4=True)
pp.trigger_all_channels()

# Stop outputs
pp.stop_all_outputs()

# Save settings (also done automatically on disconnect)
pp.save_settings()


```

#### as context manager
```python
import time
from pypulsepal import PulsePal

with PulsePal(serial_port="/dev/ttyACM0") as pp:
    # set params
    pp.upload_all()

    # do something
    time.sleep(2)

```

#### Write `default` params to all channels

```python
from pypulsepal.write_tests import write_default_settings

write_default_settings(serial_port="/dev/ttyACM0")

```

#### Write (funky) `test` params to all channels

```python
from pypulsepal.write_tests import write_test_settings_for_manual_check

write_test_settings_for_manual_check(serial_port="/dev/ttyACM0")

```


## Installation
#### pip
```shell
pip install pypulsepal
```
#### git
```shell
git clone https://github.com/larsrollik/pypulsepal.git
cd pypulsepal/
pip install -e .
```
#### pip + git
```shell
pip install git+https://github.com/larsrollik/pypulsepal.git
```

## Problems & issues
Please open [issues](https://github.com/larsrollik/pypulsepal/issues) or [pull-requests](https://github.com/larsrollik/pypulsepal/pulls) in this repository.

## Citation
Please cite the original [PulsePal] and [PyBpod] code and publications that this package is based on.

To cite `PyPulsePal` with a reference to the current version (as publicly documented on Zenodo), please use:
> Rollik, Lars B. (2021). PyPulsePal: Python API for the PulsePal open-source pulse train generator. doi: [--doi--](https://doi.org/--doi--).

**BibTeX**
```BibTeX
@misc{rollik2022pypulsepal,
    author       = {Lars B. Rollik},
    title        = {{PyPulsePal: Python API for the PulsePal open-source pulse train generator}},
    year         = {2022},
    month        = mar,
    publisher    = {Zenodo},
    url          = {https://doi.org/--doi--},
    doi          = {--doi--},
  }
```

## License & sources
This software is released under the **[GNU GPL v3.0](https://github.com/larsrollik/pypulsepal/blob/main/LICENSE)**.

This work is derived from the [Sanworks PulsePal Python API](https://github.com/sanworks/PulsePal/tree/develop) ([commit: 5bb189f](https://github.com/sanworks/PulsePal/commit/5bb189fec8d7435433b8c23f7bae520f92e271af)).

The architecture of the API is imported and inspired by the `pybpodapi.com.arcom` module from the [pybpod-api](https://github.com/pybpod/pybpod-api).

For changes from the original implementation, see the git history since [commit 972bc1e](https://github.com/larsrollik/pypulsepal/commit/972bc1ed3d07b6809e6cbcd05373be3b76ae5b5b).

## Useful code references
- [PyBpod com ArCOM]
- [PyBpod com protocol]
- [PyBpod message headers]
- [PulsePal Python 3 API]
- [PulsePal .ino file]
- [PulsePal param definitions]


## TODO
- [ ] Simplify parameter dicts in `definitions`: into nested dict with first level for name, then standard sub-dict (default value, dtype, dtype legacy(model 1), scaling, )
- [ ] Complete API functions with all PulsePal opcodes, e.g. for Arduino logic levels (see [PulsePal USB v2 opcode list])
- [ ] Move PulsePal hardware settings to init and remove defaults for easier upgrade in future
- [ ] API function to accept list of dicts (from json settings file)
  - to make overwrites on channels to get from value-based logic to channel parameter sets
  - add write function to save all settings to json for documentation

[//]: # (links)
[Pulsepal]: https://github.com/sanworks/PulsePal
[PyBpod]: https://github.com/pybpod/pybpod
[PyBpod com ArCOM]: https://github.com/pybpod/pybpod-api/blob/master/pybpodapi/com/arcom.py
[PyBpod com protocol]: https://github.com/pybpod/pybpod-api/blob/master/pybpodapi/bpod/bpod_com_protocol.py
[PyBpod message headers]: https://github.com/pybpod/pybpod-api/blob/master/pybpodapi/com/protocol/send_msg_headers.py
[PulsePal Python 3 API]: https://github.com/sanworks/PulsePal/blob/develop/Python/Python3/PulsePal.py
[PulsePal .ino file]: https://github.com/sanworks/PulsePal/blob/develop/Firmware/PulsePal_2_0_1/PulsePal_2_0_1.ino
[PulsePal param definitions]: https://sites.google.com/site/pulsepalwiki/matlab-gnu-octave/functions/programpulsepalparam
[PulsePal USB v2 opcode list]: https://sites.google.com/site/pulsepalwiki/usb-serial-interface/usb-interface-v2-x
