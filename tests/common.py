import os
import platform

# Find path for tests:
TEST_PATH = os.path.dirname(os.path.abspath(__file__))

# Set path for executable:
if platform.system() == 'Windows':
    DUNE_EXE = os.path.split(TEST_PATH)[0] + r"\dune.bat"
else:
    DUNE_EXE = os.path.split(TEST_PATH)[0] + "/dune"
print("Executable path: ", DUNE_EXE)

# Default addresses
DEFAULT_HTTP_ADDR="0.0.0.0:8888"
DEFAULT_P2P_ADDR="0.0.0.0:9876"
DEFAULT_SHIP_ADDR="0.0.0.0:8080"
