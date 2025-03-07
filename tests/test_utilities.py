from kodman.utilities import get_env


def test_get_env_string(env_vars):
    var = get_env("KODMAN_TEST_STRING", str)
    assert var == "Test"


def test_get_env_bool_true(env_vars):
    var = get_env("KODMAN_TEST_BOOL_TRUE", bool)
    assert var is True


def test_get_env_bool_false(env_vars):
    var = get_env("KODMAN_TEST_BOOL_FALSE", bool)
    assert var is False


def test_get_env_int(env_vars):
    var = get_env("KODMAN_TEST_INT", int)
    assert var == 99


def test_get_env_none(env_vars):
    var = get_env("KODMAN_TEST_NONE", int)
    assert var is None
