import sys

sys.stderr.write("""
===============================
Unsupported installation method
===============================
configpipe no longer supports installation with `python setup.py install`.
Please use `python -m pip install .` instead.
"""
)
sys.exit(1)


# The below code will never execute, however GitHub is particularly
# picky about where it finds Python packaging metadata.
# See: https://github.com/github/feedback/discussions/6456
#
# To be removed once GitHub catches up.

setup(
    name='configpipe',
    # DEP: pyproject.toml is the authorative source for dependencies.
    #      Update the line below to support GitHub metadata indexing.
    install_requires=[],
)