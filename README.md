[![CI](https://github.com/marcelldls/kocker/actions/workflows/ci.yml/badge.svg)](https://github.com/marcelldls/kocker/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/marcelldls/kocker/branch/main/graph/badge.svg)](https://codecov.io/gh/marcelldls/kocker)
[![PyPI](https://img.shields.io/pypi/v/kocker.svg)](https://pypi.org/project/kocker)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)

# kocker

A command-line tool that provides a Docker-like interface for Kubernetes operations.

An example usecase would be to facilitate a single CI script where the runner could be
a host with Docker (for example the local machine) or Kubernetes runner (In a CI job).

Source          | <https://github.com/marcelldls/kocker>
:---:           | :---:
PyPI            | `pip install kocker`
Releases        | <https://github.com/marcelldls/kocker/releases>

Some examples:
```
kocker --version
```
