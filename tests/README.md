# Pytest Validation for DUNES

# WARNING

Some of these tests are destructive. Avoid running them when there is important data in your container!

## Getting Started

Make sure you have a recent version of `pytest` installed. Development was initially done with version `7.1`.

Pytest can be installed with [pip](https://pypi.org/project/pytest/)
or - very likely - is part of your Linux distribution. Additionally,
the source is available [here](https://github.com/pytest-dev/pytest).

Following the [instructions](../README.md#getting-started) for
building and installing DUNES.

## Running the Tests

From the root directory, execute all the tests as follows:
```
$ pytest ./tests/
```

If you need to run a single test, it can be done similar to the example below:
```
$ pytest ./tests/test_version.py
```

More information regarding running and developing tests with pytest
can be found [here](https://docs.pytest.org/en/stable/).

## What to do when you find a defect?

Check DUNES's github site to see if the issue already exists. Make sure
that your issue isn't already fixed in the main DUNES branch by
rerunning the tests there if you haven't already. If the problem is
repeatable in the main branch and no issue already exists, add a new
issue including what platform (e.g. Ubuntu 20.04 x86, OSX arm64, etc),
complier, python version, pytest version, and steps we might need to
repeat the defect.

## Adding new tests

Make sure any new tests follow the same basic format as exist
here. You can use [test_version.py](test_version.py) as a sample.

Note that you will NEED to run pylint against the tests. This can be
done from the root directory like this:
```
$ pylint ./tests/<my_new_test>.py
```
