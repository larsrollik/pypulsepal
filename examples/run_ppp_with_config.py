from pathlib import Path

from pypulsepal import PulsePal


def run_example():
    config_path = "pypulsepal.config.test"
    serial_port = "/dev/ttyACM0"

    p = PulsePal(serial_port=serial_port)
    p.load_from_config(config_path=config_path)

    print(p)


if __name__ == "__main__":
    run_example()
