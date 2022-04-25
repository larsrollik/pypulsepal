import logging

from pybpodapi.com.arcom import ArCOM
from tqdm import tqdm

from pypulsepal.definitions import CHANNEL_PARAM_DEFAULTS
from pypulsepal.definitions import CUSTOM_PULSE_TRAIN_OPCODES
from pypulsepal.definitions import PARAM_DTYPE_MODEL_1
from pypulsepal.definitions import PARAM_DTYPE_MODEL_2
from pypulsepal.definitions import PARAM_SCALING
from pypulsepal.definitions import PULSEPAL_CYCLE_FREQUENCY
from pypulsepal.definitions import ReceiveMessageHeader
from pypulsepal.definitions import resolve_param_name_code_pair
from pypulsepal.definitions import resolve_trigger_name_code_pair
from pypulsepal.definitions import SendMessageHeader
from pypulsepal.definitions import TRIGGER_PARAM_DEFAULTS
from pypulsepal.utils import encode_message
from pypulsepal.utils import volts_to_bytes


class PulsePal:
    """PulsePal API object"""

    # communication
    _arcom = None
    serial_port = None
    baudrate = 115200

    # hardware attributes
    firmware_version = None
    hardware_model = None
    hardware_dac_bit_max = None
    hardware_cycle_frequency = 20000
    firmware_opcode = None
    nr_output_channels = 4
    nr_trigger_channels = 2
    param_dtype_lookup = None

    _config = None  # todo

    def __init__(
        self,
        serial_port=None,
        baudrate=115200,
        cycle_frequency=20000,
        nr_output_channels=4,
        nr_trigger_channels=2,
        firmware_opcode=213,
        **kwargs,
    ):
        """

        :param serial_port:
        :param baudrate:
        :param cycle_frequency:
        :param nr_output_channels:
        :param nr_trigger_channels:
        :param kwargs:
        """
        super(PulsePal, self).__init__()

        # Generate class attributes according to default channel parameters
        for param, default_value in CHANNEL_PARAM_DEFAULTS.items():
            setattr(self, param, [default_value] * self.nr_output_channels)

        for param, default_value in TRIGGER_PARAM_DEFAULTS.items():
            setattr(self, param, [default_value] * self.nr_trigger_channels)

        # Args
        self.serial_port = serial_port
        self.baudrate = baudrate
        self.hardware_cycle_frequency = (
            cycle_frequency or self.hardware_cycle_frequency
        )
        self.nr_output_channels = nr_output_channels
        self.nr_trigger_channels = nr_trigger_channels
        self.firmware_opcode = firmware_opcode or self.firmware_opcode

        # Convenience updates for debug inputs
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)

        self.connect(serial_port=serial_port, baudrate=baudrate)

    @property
    def encoded_opcode(self):
        return encode_message(self.firmware_opcode, encoding="uint8")

    @encoded_opcode.setter
    def encoded_opcode(self, value=None):
        self.firmware_opcode = value

    def _clear_read_queue(self):
        """Clears leftover items from serial read queue"""
        return self._arcom.serial_object.read(
            self._arcom.serial_object.inWaiting()
        )

    def _read_confirmation(self):
        """Returns True for successful receipt of previous message"""
        return self._arcom.read_uint8() == 1

    def _pulsepal_handshake(self):
        """Confirm connectivity with hardware.

        :return: handshake success bool
        """
        self._arcom.serial_object.write(
            self.encoded_opcode + str.encode(SendMessageHeader.HANDSHAKE)
        )
        handshake, firmware_version = (
            self._arcom.read_char(),
            self._arcom.read_uint8(),
        )
        self._clear_read_queue()

        handshake_ok = handshake == ReceiveMessageHeader.HANDSHAKE_OK
        if handshake_ok:
            self.firmware_version = firmware_version
            if firmware_version < 20:
                self.hardware_model = 1
                self.hardware_dac_bit_max = 255
                self.param_dtype_lookup = PARAM_DTYPE_MODEL_1
            else:
                self.hardware_model = 2
                self.hardware_dac_bit_max = 65535
                self.param_dtype_lookup = PARAM_DTYPE_MODEL_2

        return True if handshake_ok else False

    def connect(self, serial_port, baudrate=115200, timeout=1):
        """Connect (& handshake) with hardware

        :param serial_port:
        :param baudrate:
        :param timeout:
        :return:
        """
        self._arcom = ArCOM().open(
            serial_port=serial_port, baudrate=baudrate, timeout=timeout
        )
        handshake_ok = self._pulsepal_handshake()
        if not handshake_ok:
            raise ConnectionError(
                f"Could not connect PulsePal at '{serial_port}' with baudrate {baudrate}"
            )
        return self

    def _pulsepal_set_display(self, message="> Py API"):
        """"""
        message_ascii = [ord(s) for s in message]
        self._arcom.write_array(
            *[
                self.encoded_opcode,
                encode_message(SendMessageHeader.DISPLAY, encoding="uint8"),
                *message_ascii,
            ]
        )

    def _update_param(self, channel, param_name, param_value):
        attr = getattr(self, param_name)
        attr[channel] = param_value
        setattr(self, param_name, attr)

    def program_one_param(
        self, channel=None, param_name=None, param_value=None
    ):
        """Program one channel parameter (one parameter on one channel)."""
        param_name, param_code = resolve_param_name_code_pair(
            param_name_or_code=param_name
        )
        param_dtype, param_scaling = self.param_dtype_lookup.get(
            param_name
        ), PARAM_SCALING.get(param_name)

        logging.debug(
            f"Param value before voltage-to-bit correction: {param_value}"
        )
        if "volt" in param_name.lower():
            param_value = volts_to_bytes(
                volt=param_value, dac_bitMax=self.hardware_dac_bit_max
            )

        logging.debug(
            f"Param value before time scaling correction: {param_value}"
        )
        param_value = param_value * param_scaling

        # Send
        message = [
            self.encoded_opcode,
            encode_message(SendMessageHeader.PROGRAM_ONE, encoding="uint8"),
            encode_message(param_code, encoding="uint8"),
            encode_message(channel + 1, encoding="uint8"),
            encode_message(param_value, encoding=param_dtype),
        ]
        self._arcom.write_array(b"".join(message))

        write_ok = self._read_confirmation()
        if write_ok:
            self._update_param(
                channel=channel, param_name=param_name, param_value=param_value
            )

        return write_ok

    def program_trigger_channel(self, trigger_channel=None, trigger_mode=None):
        """"""
        _, trigger_mode_value = resolve_trigger_name_code_pair(
            trigger_name_or_code=trigger_mode
        )
        write_ok = self.program_one_param(
            channel=trigger_channel,
            param_name="triggerMode",
            param_value=trigger_mode_value,
        )
        return write_ok

    def upload_all(self):
        """Set each channel and trigger param on each output channel and trigger channel, respectively."""
        # Channel parameters
        for param_name in tqdm(CHANNEL_PARAM_DEFAULTS):
            for channel in range(self.nr_output_channels):

                param_value = getattr(self, param_name)[channel]
                success = self.program_one_param(
                    channel=channel,
                    param_name=param_name,
                    param_value=param_value,
                )
                logging.debug(
                    param_name, channel, param_value, f"ok: {success}"
                )
                if not success:
                    raise ValueError

        # Trigger modes
        param_name = "triggerMode"
        for trigger_channel in tqdm(range(self.nr_trigger_channels)):
            param_value = getattr(self, param_name)[trigger_channel]
            success = self.program_one_param(
                channel=trigger_channel,
                param_name=param_name,
                param_value=param_value,
            )
            logging.debug(
                param_name, trigger_channel, param_value, f"ok: {success}"
            )
            if not success:
                raise ValueError

    def set_resting_voltage(self, channel=None, voltage=None):
        """Convenience function to set restingVoltage parameter on one channel.

        :param channel:
        :param voltage:
        :return:
        """
        write_ok = self.program_one_param(
            channel=channel,
            param_name="restingVoltage",
            param_value=voltage,
        )
        return write_ok

    def upload_custom_pulse_train(
        self, pulse_train_id=None, pulse_times=None, pulse_voltages=None
    ):
        """"""
        assert pulse_train_id in [0, 1]
        assert len(pulse_times) == len(pulse_voltages)

        scaled_pulse_times = []
        scaled_pulse_voltages = []
        for pulse_time, pulse_voltage in zip(pulse_times, pulse_voltages):
            scaled_pulse_times.append(
                pulse_time * self.hardware_cycle_frequency
            )
            scaled_pulse_voltages.append(
                volts_to_bytes(
                    volt=pulse_voltage, dac_bitMax=self.hardware_dac_bit_max
                )
            )

        message = [
            self.encoded_opcode,
            encode_message(
                CUSTOM_PULSE_TRAIN_OPCODES.get(pulse_train_id),
                encoding="uint8",
            ),
            # if model=1, additional 0 int here,
            encode_message(len(scaled_pulse_times), encoding="uint32"),
            encode_message(scaled_pulse_times, encoding="uint32"),
            encode_message(
                scaled_pulse_voltages,
                encoding=self.param_dtype_lookup.get("phase1Voltage"),
            ),
        ]
        self._arcom.write_array(b"".join(message))
        return self._read_confirmation()

    def upload_custom_waveform(
        self, pulse_train_id=None, pulse_width=None, pulse_voltages=None
    ):
        """"""
        assert pulse_train_id in [0, 1]

        scaled_pulse_times = []
        scaled_pulse_voltages = []
        for pulse_index, pulse_voltage in enumerate(pulse_voltages):
            pulse_time = (
                pulse_index * pulse_width * self.hardware_cycle_frequency
            )
            scaled_pulse_times.append(pulse_time)
            scaled_pulse_voltages.append(
                volts_to_bytes(
                    volt=pulse_voltage, dac_bitMax=self.hardware_dac_bit_max
                )
            )

        message = [
            self.encoded_opcode,
            encode_message(
                CUSTOM_PULSE_TRAIN_OPCODES.get(pulse_train_id),
                encoding="uint8",
            ),
            # if model=1, additional 0 int here,
            encode_message(len(scaled_pulse_times), encoding="uint32"),
            encode_message(scaled_pulse_times, encoding="uint32"),
            encode_message(
                scaled_pulse_voltages,
                encoding=self.param_dtype_lookup.get("phase1Voltage"),
            ),
        ]
        self._arcom.write_array(b"".join(message))
        return self._read_confirmation()

    def set_continuous(self, channel=None, state=None):
        """"""
        message = [
            self.encoded_opcode,
            encode_message(SendMessageHeader.CONTINUOUS, encoding="uint8"),
            encode_message(channel, encoding="uint8"),
            encode_message(state, encoding="uint8"),
        ]
        self._arcom.write_array(b"".join(message))
        return self._read_confirmation()

    def trigger_selected_channels(
        self,
        channel_1=False,  # fixme: this indexing is inconsistent with the expected config indices range 0-3
        channel_2=False,
        channel_3=False,
        channel_4=False,
    ):
        """Trigger specific channels

        :param channel_1:
        :param channel_2:
        :param channel_3:
        :param channel_4:
        :return:
        """
        combination_byte = (
            (1 * channel_1)
            + (2 * channel_2)
            + (4 * channel_3)
            + (8 * channel_4)
        )
        message = [
            self.encoded_opcode,
            encode_message(SendMessageHeader.SOFT_TRIGGER, encoding="uint8"),
            encode_message(combination_byte, encoding="uint8"),
        ]
        self._arcom.write_array(b"".join(message))
        return self._read_confirmation()

    def trigger_all_channels(self):
        return self.trigger_selected_channels(
            channel_1=True, channel_2=True, channel_3=True, channel_4=True
        )

    def stop_all_outputs(self):
        """"""
        message = [
            self.encoded_opcode,
            encode_message(SendMessageHeader.ABORT_ALL, encoding="uint8"),
        ]
        self._arcom.write_array(b"".join(message))
        return self._read_confirmation()

    def save_settings(
        self,
    ):  # fixme: rename, so it's clear this is persisting the settings on the device
        """"""
        message = [
            self.encoded_opcode,
            encode_message(SendMessageHeader.DISCONNECT, encoding="uint8"),
        ]
        self._arcom.write_array(b"".join(message))
        return self._read_confirmation()  # fixme: returns False

    def load_from_config(self, config_path=None):
        from pathlib import Path
        from configobj import ConfigObj
        from validate import Validator
        from pypulsepal import config as ppp_config

        config_spec_path = (
            Path(ppp_config.__path__[0]) / "pypulsepal.config.spec"
        )
        assert Path(config_path).exists() and config_spec_path.exists()

        config = ConfigObj(
            infile=str(config_path),
            configspec=str(config_spec_path),
            unrepr=True,
            list_values=True,
        )
        v = Validator()
        validation_success = config.validate(v, copy=True)
        if isinstance(validation_success, bool) and validation_success is True:
            self.config = config.dict()

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, new_config: dict = None):
        # update params from config
        for k, v in new_config.items():
            if hasattr(self, k):
                setattr(self, k, v)
            else:
                print(
                    f"Config contains property '{k}', but not a property of 'self'!"
                )

        for channel_name, channel_params in new_config.get(
            "channels", {}
        ).items():
            for prop_name, prop_value in channel_params.items():
                before = getattr(self, prop_name)[int(channel_name)]
                getattr(self, prop_name)[int(channel_name)] = prop_value
                print(
                    channel_name,
                    prop_name,
                    " : ",
                    before,
                    "-->>",
                    getattr(self, prop_name)[int(channel_name)],
                )

        for channel_name, channel_params in new_config.get(
            "triggers", {}
        ).items():
            for prop_name, prop_value in channel_params.items():
                before = getattr(self, prop_name)[int(channel_name)]
                getattr(self, prop_name)[int(channel_name)] = prop_value
                print(
                    channel_name,
                    prop_name,
                    " : ",
                    before,
                    "-->>",
                    getattr(self, prop_name)[int(channel_name)],
                )

        self._config = new_config

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.save_settings()
        self._arcom.close()

    def __del__(self):
        self.save_settings()
        self._arcom.close()
