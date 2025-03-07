from kodman.utilities import get_env


def test_get_env_string(env_vars):
    var = get_env("KODMAN_TEST_STRING", str)
    assert var == "Test"


def test_get_env_bool(env_vars):
    var = get_env("KODMAN_TEST_BOOL", bool)
    assert var is True


def test_get_env_INT(env_vars):
    var = get_env("KODMAN_TEST_INT", int)
    assert var == 99
