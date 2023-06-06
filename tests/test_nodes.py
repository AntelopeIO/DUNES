#!/usr/bin/env python3

"""Test various DUNES commands.

This script tests that the compiled binary produce expected output for these commands:
  --start
  --config
  --stop
  --remove
  --simple-list
  --list
  --get-active
  --set-active
  --export-node
  --import-node
"""


import os
import shutil                   # rmtree
import subprocess
import pytest

# pylint: disable=unused-wildcard-import,wildcard-import
from common import *                   # local defines
from container import container


# Globals
NODE_ALPHA = "ALPHA_NODE"
NODE_BRAVO = "BRAVO_NODE"
NODE_CHARLIE = "CHARLIE_NODE"

CONFIG_PATH = TEST_PATH
CONFIG_FILE = os.path.join(TEST_PATH, "config.ini")
CONFIG_FILE_CUST = os.path.join(TEST_PATH, "mycustconfig001.ini")

EXPORT_DIR = os.path.join(TEST_PATH, "temp")

ALT_HTTP_ADDR="0.0.0.0:9991"
ALT_P2P_ADDR="0.0.0.0:9992"
ALT_SHIP_ADDR="0.0.0.0:9993"
ALT_HTTP_ADDR_CUST="0.0.0.0:9996"
ALT_P2P_ADDR_CUST="0.0.0.0:9997"
ALT_SHIP_ADDR_CUST="0.0.0.0:9998"


def remove_all():
    """ Remove any existing nodes. """

    # Call dunes, check the return is True.
    completed_process = subprocess.run([DUNES_EXE, "--simple-list"],
                                       check=True, stdout=subprocess.PIPE)

    # Convert the captured stdin to a list.
    result_list = completed_process.stdout.decode().replace('\r', '').split("\n")

    # Remove the header.
    result_list.pop(0)

    # Remove all the entries in the list.
    for entry in result_list:
        # ignore empty entries.
        if len(entry) == 0:
            continue
        # Remove the entry
        name = entry.split('|')[0]
        print("Removing: ", name)
        subprocess.run([DUNES_EXE, "--remove", name], check=True)


def validate_node_state( node_name, active_state, running_state ):
    """Validate the result of a call to `dunes --simple-list` contains the
    node in a given state.

    :param node_name: The node to search for.
    :param active_state: True/False
    :param running_state: True/False
    """

    # Validate the entry
    assert active_state in (True, False)
    assert running_state in (True, False)

    expect = node_name + "|"
    if active_state:
        expect += "Y|"
    else:
        expect += "N|"
    if running_state:
        expect += "Y|"
    else:
        expect += "N|"
    expect += DEFAULT_HTTP_ADDR + "|" + DEFAULT_P2P_ADDR + "|" + DEFAULT_SHIP_ADDR

    # Call dunes, check the return is True.
    completed_process = subprocess.run([DUNES_EXE, "--simple-list"],
                                       check=True, stdout=subprocess.PIPE)

    # Convert the captured stdin to a list for comparison with expected output.
    result_list = completed_process.stdout.decode().replace('\r', '').split("\n")

    assert expect in result_list


# pylint: disable=too-many-branches
def validate_node_list( node_list ):
    """Validate the result of a call to `dunes --simple-list` contains all
    the nodes and states in node_list.

    :param node_list: A list of lists with the form:
        [node name, active (t/F), running (t/F), http_addr, p2p_addr, ship_addr].
        where node name is required, but other values have reasonable defaults.
    """

    # Test algorithm:
    #   Build the list of expected results.
    #   Get the actual results.
    #   For each entry in the actual results,
    #     Test the entry is in expected and remove it.
    #   Test that all entries are removed from expected results.

    # Create a list of expected strings.
    expect_list = ["Node|Active|Running|HTTP|P2P|SHiP"]
    for entry in node_list:

        # Valid the array count in the entry.
        is_valid = True
        if not len(entry) in (1, 2, 3, 4, 5, 6):
            print("len() should be a value between 1 and 6 but is: ", len(entry), " value: ", entry)
            is_valid = False

        # Determine if this entry should be active.
        active = False
        if len(entry) > 1:
            active = entry[1]
            if active not in (True, False):
                print("Invalid value for Active. Expect True/False, received: ", active)
                is_valid = False

        # Determine if this entry should be running.
        running = False
        if len(entry) > 2:
            running = entry[2]
            if running not in (True, False):
                print("Invalid value for Running. Expect True/False, received: ", running)
                is_valid = False

        # Determine the expected ip addrs.
        http_addr=DEFAULT_HTTP_ADDR
        if len(entry) > 3:
            http_addr = entry[3]
        p2p_addr=DEFAULT_P2P_ADDR
        if len(entry) > 4:
            p2p_addr = entry[4]
        ship_addr = DEFAULT_SHIP_ADDR
        if len(entry) > 5:
            ship_addr = entry[5]

        assert is_valid

        # Make an expected string for this entry and append it the  expected results list
        temp = entry[0] + "|"
        if entry[1]:
            temp += "Y|"
        else:
            temp += "N|"
        if entry[2]:
            temp += "Y|"
        else:
            temp += "N|"
        temp += http_addr + "|" + p2p_addr + "|" + ship_addr
        expect_list.append(temp)

    # Call dunes, check the return is True.
    completed_process = subprocess.run([DUNES_EXE, "--simple-list"],
                                       check=True, stdout=subprocess.PIPE)

    # Convert the captured stdin to a list for comparison with expected output.
    result_list = completed_process.stdout.decode().replace('\r', '').split("\n")

    # Iterate over the elements in the results list
    for entry in result_list:
        # Ignore empty lines.
        if entry == "":
            continue
        # Test a value exists in expect_list, then remove it.
        assert entry in expect_list
        expect_list.remove(entry)

    # Test that there are no entries remaining in expect_list.
    assert not expect_list


def expect_empty_verbose_list():
    """Test that the output of list options are empty."""

    # List of expected output lines from `dunes --list`.
    empty_verbose_list = \
        "Node Name   | Active? | Running? | HTTP           | P2P          | SHiP          \n" + \
        "---------------------------------------------------------------------------------\n"

    # Call the tool, check expected value.
    completed_process = subprocess.run([DUNES_EXE, "--list"], check=True, stdout=subprocess.PIPE)
    assert completed_process.stdout.decode().replace('\r', '') == empty_verbose_list


# pylint: disable=too-many-statements
@pytest.mark.destructive
def test_nodes():
    """Run the tests."""

    # Remove any container that already exists and create a fresh one.
    cntr = container('dunes_container', 'dunes:latest')
    if cntr.exists():
        subprocess.run([DUNES_EXE, "--destroy-container"], check=True)
    subprocess.run([DUNES_EXE, "--start-container"], check=True)

    # Ensure there are no existing nodes.
    #   Tests `--simple-list` and `--list`
    remove_all()
    validate_node_list([])
    expect_empty_verbose_list()

    # Create a node and test its state.
    #   Tests `--start` when the node needs to be created.
    subprocess.run([DUNES_EXE, "--start", NODE_ALPHA], check=True)
    validate_node_state(NODE_ALPHA, True, True)
    # Stop the node and test its state.
    #   Tests `--stop`
    subprocess.run([DUNES_EXE, "--stop", NODE_ALPHA], check=True)
    validate_node_state(NODE_ALPHA, True, False)
    # Restart the node and test its state.
    #   Tests `--start` when the node already exists.
    subprocess.run([DUNES_EXE, "--start", NODE_ALPHA], check=True)
    validate_node_state(NODE_ALPHA, True, True)

    # Create a 2nd node and test the state of both nodes.
    #   Tests the behavior of `--start` on an already active, running node.
    subprocess.run([DUNES_EXE, "--start", NODE_BRAVO], check=True)
    validate_node_state(NODE_BRAVO, True, True)
    validate_node_list([[NODE_ALPHA, False, False],[NODE_BRAVO, True, True]])

    # Test --get-active shows NODE_BRAVO
    #   Tests `--get-active`.
    assert subprocess.run([DUNES_EXE, "--get-active"], check=True, stdout=subprocess.PIPE).stdout.decode().replace('\r', '') \
        == (NODE_BRAVO + "\n")

    # Test --set-active works to switch to NODE_ALPHA and --get active returns the correct value.
    #   Tests `--set-active` switch active node while run state is left unchanged.
    subprocess.run([DUNES_EXE, "--set-active", NODE_ALPHA], check=True)
    validate_node_list([[NODE_ALPHA, True, False],[NODE_BRAVO, False, True]]) # Note this is TF,FT
    assert subprocess.run([DUNES_EXE, "--get-active"], check=True, stdout=subprocess.PIPE).stdout.decode().replace('\r', '') \
        == (NODE_ALPHA + "\n")

    # Remove NODE_ALPHA, ensure it is no longer in the list.
    #   Tests `--remove`.
    subprocess.run([DUNES_EXE, "--remove", NODE_ALPHA], check=True)
    validate_node_list([[NODE_BRAVO, False, True]]) # Note the state of NODE_BRAVO is FT

    # Remove anything to get to a clean slate.
    remove_all()

    # Test `--start` where start includes a config path.
    subprocess.run([DUNES_EXE, "--start", NODE_ALPHA, "--config", CONFIG_PATH], check=True)
    validate_node_list([[NODE_ALPHA, True, True, ALT_HTTP_ADDR, ALT_P2P_ADDR, ALT_SHIP_ADDR]])

    # Test `--start` where start includes a config file named config.ini
    subprocess.run([DUNES_EXE, "--start", NODE_BRAVO, "--config", CONFIG_FILE], check=True)
    validate_node_list([[NODE_ALPHA, False, False, ALT_HTTP_ADDR, ALT_P2P_ADDR, ALT_SHIP_ADDR],
                        [NODE_BRAVO, True, True, ALT_HTTP_ADDR, ALT_P2P_ADDR, ALT_SHIP_ADDR]])

    subprocess.run([DUNES_EXE,"--stop", NODE_BRAVO], check=True)
    validate_node_list([[NODE_ALPHA, False, False, ALT_HTTP_ADDR, ALT_P2P_ADDR, ALT_SHIP_ADDR],
                        [NODE_BRAVO, True,  False, ALT_HTTP_ADDR, ALT_P2P_ADDR, ALT_SHIP_ADDR]])

    # Test `--start` where start includes a config file with customized name mycustconfig001.ini
    subprocess.run([DUNES_EXE, "--start", NODE_BRAVO, "--config", CONFIG_FILE_CUST], check=True)
    validate_node_list([[NODE_ALPHA, False, False, ALT_HTTP_ADDR, ALT_P2P_ADDR, ALT_SHIP_ADDR],
                        [NODE_BRAVO, True, True, ALT_HTTP_ADDR_CUST, ALT_P2P_ADDR_CUST, ALT_SHIP_ADDR_CUST]])

    # stop and then start NODE_BRAVO again using standard config.ini
    subprocess.run([DUNES_EXE,"--stop", NODE_BRAVO], check=True)
    subprocess.run([DUNES_EXE, "--start", NODE_BRAVO, "--config", CONFIG_FILE], check=True)
    validate_node_list([[NODE_ALPHA, False, False, ALT_HTTP_ADDR, ALT_P2P_ADDR, ALT_SHIP_ADDR],
                        [NODE_BRAVO, True, True, ALT_HTTP_ADDR, ALT_P2P_ADDR, ALT_SHIP_ADDR]])

    # Test `--start` with invalid config file path.
    #   pylint: disable=subprocess-run-check
    completed_process = subprocess.run([DUNES_EXE, "--start", NODE_ALPHA, "--config", "unknown_config"], check=False)
    assert completed_process.returncode != 0
    validate_node_list([[NODE_ALPHA, False, False, ALT_HTTP_ADDR, ALT_P2P_ADDR, ALT_SHIP_ADDR],
                        [NODE_BRAVO, True, True, ALT_HTTP_ADDR, ALT_P2P_ADDR, ALT_SHIP_ADDR]])

    # Test `--config` alone.
    #   pylint: disable=subprocess-run-check
    completed_process = subprocess.run([DUNES_EXE, "--config", "unknown_config"], check=False)
    assert completed_process.returncode != 0
    validate_node_list([[NODE_ALPHA, False, False, ALT_HTTP_ADDR, ALT_P2P_ADDR, ALT_SHIP_ADDR],
                        [NODE_BRAVO, True, True, ALT_HTTP_ADDR, ALT_P2P_ADDR, ALT_SHIP_ADDR]])

    #
    # Testing the import and export of nodes may not be sophisticated
    # enough.
    #

    # remove any existing directory and ensure a fresh one is created.
    if os.path.exists(EXPORT_DIR):
        print("Removing EXPORT_DIR: ", EXPORT_DIR)
        shutil.rmtree(EXPORT_DIR)
    os.mkdir(EXPORT_DIR)

    # Just add an additional node for export.
    subprocess.run([DUNES_EXE, "--start", NODE_CHARLIE], check=True)
    validate_node_list([[NODE_ALPHA, False, False, ALT_HTTP_ADDR, ALT_P2P_ADDR, ALT_SHIP_ADDR],
                        [NODE_BRAVO, False, True, ALT_HTTP_ADDR, ALT_P2P_ADDR, ALT_SHIP_ADDR],
                        [NODE_CHARLIE, True, True, DEFAULT_HTTP_ADDR, DEFAULT_P2P_ADDR, DEFAULT_SHIP_ADDR]])

    # things we need to test:
    #  export to TEST_PATH, TEST_PATH/my_file.tgz, TEST_PATH/does_not_exist_yet/my_file.tgz

    # Test --export-node using standard filename.
    subprocess.run([DUNES_EXE, "--export-node", NODE_ALPHA, EXPORT_DIR], check=True)
    assert os.path.exists( os.path.join(EXPORT_DIR,  NODE_ALPHA+".tgz") )

    # Below check documents current behavior: node_bravo is active, however before exporting node_charlie was active.
    # Fix this in issue https://github.com/AntelopeIO/DUNES/issues/159
    validate_node_list([[NODE_ALPHA, False, False, ALT_HTTP_ADDR, ALT_P2P_ADDR, ALT_SHIP_ADDR],
                        [NODE_BRAVO, True, True, ALT_HTTP_ADDR, ALT_P2P_ADDR, ALT_SHIP_ADDR],
                        [NODE_CHARLIE, False, True, DEFAULT_HTTP_ADDR, DEFAULT_P2P_ADDR, DEFAULT_SHIP_ADDR]])

    # Test --export-node using provided filename.
    subprocess.run([DUNES_EXE, "--export-node", NODE_BRAVO, os.path.join(EXPORT_DIR, "bravo_export.tgz")], check=True)
    assert os.path.exists( os.path.join(EXPORT_DIR,"bravo_export.tgz") )

    validate_node_list([[NODE_ALPHA, False, False, ALT_HTTP_ADDR, ALT_P2P_ADDR, ALT_SHIP_ADDR],
                        [NODE_BRAVO, True, True, ALT_HTTP_ADDR, ALT_P2P_ADDR, ALT_SHIP_ADDR],
                        [NODE_CHARLIE, False, True, DEFAULT_HTTP_ADDR, DEFAULT_P2P_ADDR, DEFAULT_SHIP_ADDR]])

    # Test --export-node using non-existing path.
    subprocess.run([DUNES_EXE, "--export-node", NODE_CHARLIE, os.path.join(EXPORT_DIR, *["new_path","charlie_export.tgz"])], check=True)
    assert os.path.exists( os.path.join(EXPORT_DIR, *["new_path","charlie_export.tgz"]) )

    validate_node_list([[NODE_ALPHA, False, False, ALT_HTTP_ADDR, ALT_P2P_ADDR, ALT_SHIP_ADDR],
                        [NODE_BRAVO, False, True, ALT_HTTP_ADDR, ALT_P2P_ADDR, ALT_SHIP_ADDR],
                        [NODE_CHARLIE, True, True, DEFAULT_HTTP_ADDR, DEFAULT_P2P_ADDR, DEFAULT_SHIP_ADDR]])

    # Clean up before import.
    remove_all()

    # Test --import-node
    #  Import each node from the export tests and
    subprocess.run([DUNES_EXE, "--import-node", os.path.join(EXPORT_DIR, "ALPHA_NODE.tgz"), NODE_ALPHA], check=True)
    validate_node_list([[NODE_ALPHA, True, True, ALT_HTTP_ADDR, ALT_P2P_ADDR, ALT_SHIP_ADDR]])

    subprocess.run([DUNES_EXE, "--import-node", os.path.join(EXPORT_DIR, "bravo_export.tgz"), NODE_BRAVO], check=True)
    validate_node_list([[NODE_ALPHA, False, False, ALT_HTTP_ADDR, ALT_P2P_ADDR, ALT_SHIP_ADDR],
                        [NODE_BRAVO, True, True, ALT_HTTP_ADDR, ALT_P2P_ADDR, ALT_SHIP_ADDR]])

    subprocess.run([DUNES_EXE, "--import-node", os.path.join(EXPORT_DIR, *["new_path","charlie_export.tgz"]), NODE_CHARLIE], check=True)
    validate_node_list([[NODE_ALPHA, False, False, ALT_HTTP_ADDR, ALT_P2P_ADDR, ALT_SHIP_ADDR],
                        [NODE_BRAVO, False, True, ALT_HTTP_ADDR, ALT_P2P_ADDR, ALT_SHIP_ADDR],
                        [NODE_CHARLIE, True, True, DEFAULT_HTTP_ADDR, DEFAULT_P2P_ADDR, DEFAULT_SHIP_ADDR]])

    # Finally, clean everything up before final return.
    remove_all()


@pytest.mark.destructive
def test_start_active_node():
    """start_active_node"""

    # Remove any container that already exists and create a fresh one.
    cntr = container('dunes_container', 'dunes:latest')
    if cntr.exists():
        subprocess.run([DUNES_EXE, "--destroy-container"], check=True)
    subprocess.run([DUNES_EXE, "--start-container"], check=True)

    # Ensure there are no existing nodes.
    #   Tests `--simple-list` and `--list`
    remove_all()
    validate_node_list([])
    expect_empty_verbose_list()

    # Create a node and test its state.
    #   Tests `--start` when the node needs to be created.
    subprocess.run([DUNES_EXE, "--start", NODE_ALPHA], check=True)
    validate_node_state(NODE_ALPHA, True, True)

    # Create a 2nd node and test the state of both nodes.
    subprocess.run([DUNES_EXE, "--start", NODE_BRAVO], check=True)
    validate_node_state(NODE_BRAVO, True, True)
    validate_node_list([[NODE_ALPHA, False, False], [NODE_BRAVO, True, True]])

    # Create a 3rd node
    subprocess.run([DUNES_EXE, "--start", NODE_CHARLIE], check=True)
    validate_node_state(NODE_CHARLIE, True, True)
    validate_node_list([[NODE_ALPHA, False, False], [NODE_BRAVO, False, False], [NODE_CHARLIE, True, True]])

    # Test --get-active shows NODE_BRAVO
    #   Tests `--get-active`.
    assert subprocess.run([DUNES_EXE, "--get-active"], check=True, stdout=subprocess.PIPE).stdout.decode().replace('\r', '') \
        == (NODE_CHARLIE + "\n")

    # Test --set-active works to switch to NODE_ALPHA and --get active returns the correct value.
    #   Tests `--set-active` switch active node while run state is left unchanged.
    subprocess.run([DUNES_EXE, "--set-active", NODE_ALPHA], check=True)
    validate_node_list([[NODE_ALPHA, True, False], [NODE_BRAVO, False, False], [NODE_CHARLIE, False, True]]) # Note this is TF,FT
    assert subprocess.run([DUNES_EXE, "--get-active"], check=True, stdout=subprocess.PIPE).stdout.decode().replace('\r', '') \
        == (NODE_ALPHA + "\n")

    # Make sure you can start active node
    subprocess.run([DUNES_EXE, "--start", NODE_ALPHA], check=True)
    validate_node_state(NODE_ALPHA, True, True)
    validate_node_list([[NODE_ALPHA, True, True], [NODE_BRAVO, False, False], [NODE_CHARLIE, False, False]])

    # Finally, clean everything up before final return.
    remove_all()


@pytest.mark.destructive
def test_node_start_rmdirtydb():
    """test dune --start with --rmdirtydb"""

    # Remove any container that already exists and create a fresh one.
    cntr = container('dunes_container', 'dunes:latest')
    if cntr.exists():
        subprocess.run([DUNES_EXE, "--destroy-container"], check=True)
    subprocess.run([DUNES_EXE, "--start-container"], check=True)

    # Ensure there are no existing nodes.
    remove_all()
    validate_node_list([])
    expect_empty_verbose_list()

    # Create NODE_ALPHA
    res = subprocess.run([DUNES_EXE,"--start", NODE_ALPHA, "--rmdirtydb"], stdout=subprocess.PIPE, check=True)
    assert b'no action for --rmdirtydb, because node [ ALPHA_NODE ] has never run before' in res.stdout
    validate_node_state(NODE_ALPHA, True, True)

    # verify already running
    res = subprocess.run([DUNES_EXE,"--start", NODE_ALPHA, "--rmdirtydb"], stdout=subprocess.PIPE, check=True)
    assert b'no action for --rmdirtydb, because node [ ALPHA_NODE ] is already running' in res.stdout
    validate_node_state(NODE_ALPHA, True, True)

    # use kill -9  to kill NODE_ALPHA
    pid_node = cntr.find_pid('/app/nodes/' + NODE_ALPHA + ' ')
    assert pid_node != -1
    cntr.execute_cmd(['kill', '-9', pid_node])
    pid_node = cntr.find_pid('/app/nodes/' + NODE_ALPHA + ' ')
    assert pid_node == -1
    validate_node_state(NODE_ALPHA, True, False)

    # start NODE_ALPHA to verify the node fails to start
    res = subprocess.run([DUNES_EXE,"--start", NODE_ALPHA], stdout=subprocess.PIPE, check=False)
    assert b'database dirty flag set' in res.stdout
    validate_node_state(NODE_ALPHA, True, False)

    # start NODE_ALPHA with --rmdirtydb to verify the node starts successfully
    res = subprocess.run([DUNES_EXE,"--start", NODE_ALPHA, "--rmdirtydb"], stdout=subprocess.PIPE, check=False)
    assert res.returncode == 0
    assert b'Found the database dirty flag for node [ ALPHA_NODE ]' in res.stdout
    assert b'using --replay-blockchain of nodeos to clean the dirty flag' in res.stdout
    validate_node_state(NODE_ALPHA, True, True)

    # stop NODE_ALPHA and then bring it up again, verify no dirty database flag set
    subprocess.run([DUNES_EXE,"--stop", NODE_ALPHA], check=True)
    validate_node_state(NODE_ALPHA, True, False)
    res = subprocess.run([DUNES_EXE,"--start", NODE_ALPHA, "--rmdirtydb"], stdout=subprocess.PIPE, check=False)
    assert res.returncode == 0
    assert b'no action for --rmdirtydb, because node [ ALPHA_NODE ] dirty database flag is not yet set' in res.stdout
    validate_node_state(NODE_ALPHA, True, True)

    # Use similar  steps to test the 2nd node NODE_BRAVO
    subprocess.run([DUNES_EXE,"--start", NODE_BRAVO, "--rmdirtydb"], check=True)
    validate_node_state(NODE_BRAVO, True, True)

    pid_node = cntr.find_pid('/app/nodes/' + NODE_BRAVO + ' ')
    assert pid_node != -1
    cntr.execute_cmd(['kill', '-9', pid_node])
    pid_node = cntr.find_pid('/app/nodes/' + NODE_BRAVO + ' ')
    assert pid_node == -1
    validate_node_state(NODE_BRAVO, True, False)

    res = subprocess.run([DUNES_EXE,"--start", NODE_BRAVO], stdout=subprocess.PIPE, check=False)
    assert b'database dirty flag set' in res.stdout
    validate_node_state(NODE_BRAVO, True, False)

    # start NODE_BRAVO with --rmdirtydb to verify the node starts successfully
    res = subprocess.run([DUNES_EXE,"--start", NODE_BRAVO, "--rmdirtydb"], stdout=subprocess.PIPE, check=False)
    assert res.returncode == 0
    assert b'Found the database dirty flag for node [ BRAVO_NODE ]' in res.stdout
    assert b'using --replay-blockchain of nodeos to clean the dirty flag' in res.stdout
    validate_node_state(NODE_BRAVO, True, True)

    # Remove anything to get to a clean slate.
    remove_all()

    # Test --rmdirtydb can be used together with --config in --start
    subprocess.run([DUNES_EXE,"--start", NODE_ALPHA, "--config", CONFIG_PATH, "--rmdirtydb"], check=True)
    validate_node_list([[NODE_ALPHA, True, True, ALT_HTTP_ADDR, ALT_P2P_ADDR, ALT_SHIP_ADDR]])

    # use standard config.ini
    subprocess.run([DUNES_EXE,"--start", NODE_BRAVO, "--config", CONFIG_FILE, "--rmdirtydb"], check=True)
    validate_node_list([[NODE_ALPHA, False, False, ALT_HTTP_ADDR, ALT_P2P_ADDR, ALT_SHIP_ADDR],
                        [NODE_BRAVO, True, True, ALT_HTTP_ADDR, ALT_P2P_ADDR, ALT_SHIP_ADDR]])

    subprocess.run([DUNES_EXE,"--stop", NODE_BRAVO], check=True)
    validate_node_list([[NODE_ALPHA, False, False, ALT_HTTP_ADDR, ALT_P2P_ADDR, ALT_SHIP_ADDR],
                        [NODE_BRAVO, True,  False, ALT_HTTP_ADDR, ALT_P2P_ADDR, ALT_SHIP_ADDR]])

    # use customized .ini
    subprocess.run([DUNES_EXE, "--start", NODE_BRAVO, "--config", CONFIG_FILE_CUST, "--rmdirtydb"], check=True)
    validate_node_list([[NODE_ALPHA, False, False, ALT_HTTP_ADDR, ALT_P2P_ADDR, ALT_SHIP_ADDR],
                        [NODE_BRAVO, True, True, ALT_HTTP_ADDR_CUST, ALT_P2P_ADDR_CUST, ALT_SHIP_ADDR_CUST]])

     # Finally, clean everything up before final return.
    remove_all()
