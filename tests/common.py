import os
import platform

# Find path for tests:
TEST_PATH = os.path.dirname(os.path.abspath(__file__))

# Set path for executable:
DUNE_EXE = os.path.join( os.path.split(TEST_PATH)[0] , "dune")

if platform.system() == 'Windows':
    DUNE_EXE += ".bat"
    
print("Executable path: ", DUNE_EXE)

# Default addresses
DEFAULT_HTTP_ADDR="0.0.0.0:8888"
DEFAULT_P2P_ADDR="0.0.0.0:9876"
DEFAULT_SHIP_ADDR="0.0.0.0:8080"
