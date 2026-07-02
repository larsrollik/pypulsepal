from importlib.metadata import version


def test_version_is_non_empty_string():
    result = version("pypulsepal")
    assert isinstance(result, str)
    assert result
