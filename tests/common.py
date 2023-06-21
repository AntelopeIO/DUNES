import os
import platform
import subprocess

# Find path for tests, root, and executable:
TEST_PATH = os.path.dirname(os.path.abspath(__file__))
DUNES_ROOT= os.path.split(TEST_PATH)[0]
DUNES_SRC = os.path.join(DUNES_ROOT, *['src','dunes'])
DUNES_EXE = os.path.join(DUNES_ROOT , "dunes")

if platform.system() == 'Windows':
    DUNES_EXE += ".bat"

print("Executable path: ", DUNES_EXE)

# Default addresses
DEFAULT_HTTP_ADDR = "0.0.0.0:8888"
DEFAULT_P2P_ADDR = "0.0.0.0:9876"
DEFAULT_SHIP_ADDR = "0.0.0.0:8080"


# Constants for test container and images
TEST_CONTAINER_NAME = 'dunes_regression_test_container'
TEST_IMAGE_NAME = 'dunes:latest'



def stop_dunes_containers():
    """Stop any container with 'dune' in the name."""

    # Get the list of RUNNING containers.
    completed_process = subprocess.run(['docker','container','ls'], check=False, stdout=subprocess.PIPE)

    # Parse the list for container names.
    for line in completed_process.stdout.decode().split('\n'):
        # On a given line, NAME is the final column.
        strings = line.split()
        index = len(strings)-1
        if index < 1:
            continue
        name = strings[index]

        # Test for 'dune' (backwards compatible name) in name.
        if 'dune' in name:
            subprocess.run(['docker', 'container', 'stop', name], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL, check=False)


def destroy_test_container():
    """Destroy any existing test containers."""
    subprocess.run(['docker', 'container', 'rm', TEST_CONTAINER_NAME, '--force'], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL, check=False)
