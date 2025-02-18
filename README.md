[![CI](https://github.com/marcelldls/kodman/actions/workflows/ci.yml/badge.svg)](https://github.com/marcelldls/kodman/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/marcelldls/kodman/branch/main/graph/badge.svg)](https://codecov.io/gh/marcelldls/kodman)
[![PyPI](https://img.shields.io/pypi/v/kodman.svg)](https://pypi.org/project/kodman)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)

# kodman

A command-line tool that provides a Docker-like interface for Kubernetes operations.

An example usecase would be to facilitate a single CI script where the runner could be
a host with Docker (for example the local machine) or Kubernetes runner (In a CI job).

Source          | <https://github.com/marcelldls/kodman>
:---:           | :---:
PyPI            | `pip install kodman`
Releases        | <https://github.com/marcelldls/kodman/releases>

Some examples:
```
kodman --version
```

# Design decisions

## Why argparse over click/typer?
The docker api is not POSIX compliant.
For example: `docker run --network=host imageID dnf -y install java`
Click/Typer does not allow this (and is correct).
They would expect: `docker run --network=host imageID -- dnf -y install java`
See Section 12.2 Guideline 10 https://pubs.opengroup.org/onlinepubs/9699919799/basedefs/V1_chap12.html#tag_12_02
