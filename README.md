# configlayer

configlayer

## Installation

## Developer Installation

Follow the below steps are cloning or creating a new git repository with `git init`.
Make sure you are in the root directory of your project.

```shell
# create a new virtual environment (e. g. venv)
python3 -m venv .venv

# activate the virtual environment
source .venv/bin/activate

# install pip-compile for auto-generating requirement files
pip install pip-tools

# generate requirement files
make refresh-requirements

# install the requirements and install 'configlayer' as editable package
make install
```

You can run the pre-commit hooks with `pre-commit` or automatically run them before commits with `pre-commit install`.

## Dependency Management

The location of where dependencies are declared depends on their scope.

- Package dependencies must be put into `pyproject.toml [project] .dependencies`.
- Opt-in dependencies must be put into `pyproject.toml [project] .optional-dependencies`.
- Testing dependencies must be put into `requirements/testing.in`.
- Linting dependencies must be put into `requirements/linting.in`.

We generate the requirements files with `make refresh-requirements`. Reinstall with `make install`.

## Publish

Build the project with `hatch build`.
Now run `hatch publish --repo test` to upload the package to `test.pypi.org`.
Use `hatch publish --repo main` to upload to the production PyPI.
Define custom targets as per defined [here](https://hatch.pypa.io/latest/publish/#repository).
