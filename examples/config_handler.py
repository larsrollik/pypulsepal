from pathlib import Path

from configobj import ConfigObj
from validate import Validator


def run_example(
    config_path="pypulsepal.config.test",
    config_spec_path="pypulsepal.config.spec",
):
    config = ConfigObj(
        infile=str(config_path),
        configspec=str(config_spec_path),
        unrepr=True,
        list_values=True,
    )
    v = Validator()
    validation_success = config.validate(v, copy=True)
    print(config.dict(), validation_success)

    c2 = ConfigObj(configspec=config_spec_path)
    c2.validate(Validator(), copy=True)


if __name__ == "__main__":
    run_example()
