from pypulsepal import PulsePal
from pypulsepal.definitions import CHANNEL_PARAM_TEST
from pypulsepal.definitions import TRIGGER_PARAM_TEST


def write_test_settings_for_manual_check(serial_port=None):
    pulsepal_object = PulsePal(serial_port=serial_port)

    print("ENTER test write")
    for k, v in CHANNEL_PARAM_TEST.items():
        setattr(pulsepal_object, k, [v] * pulsepal_object.nr_output_channels)

    for k, v in TRIGGER_PARAM_TEST.items():
        setattr(pulsepal_object, k, [v] * pulsepal_object.nr_trigger_channels)

    pulsepal_object.upload_all()
    print("EXIT test write")


def write_default_settings(serial_port=None):
    print("ENTER default write")
    pulsepal_object = PulsePal(serial_port=serial_port)
    pulsepal_object.upload_all()
    print("EXIT default write")
