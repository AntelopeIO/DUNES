import os
import platform

# Find path for tests, root, and executable:
TEST_PATH = os.path.dirname(os.path.abspath(__file__))
DUNES_ROOT= os.path.split(TEST_PATH)[0]
DUNES_EXE = os.path.join(DUNES_ROOT , "dunes")

if platform.system() == 'Windows':
    DUNES_EXE += ".bat"

print("Executable path: ", DUNES_EXE)

# Default addresses
DEFAULT_HTTP_ADDR = "0.0.0.0:8888"
DEFAULT_P2P_ADDR = "0.0.0.0:9876"
DEFAULT_SHIP_ADDR = "0.0.0.0:8080"
