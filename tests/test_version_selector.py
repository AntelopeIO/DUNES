#!/usr/bin/env python3

"""Test CDT/Leap version selector
"""
import sys
from unittest.mock import patch
from unittest import TestCase
from os.path import dirname, realpath
import pytest

sys.path.insert(1, sys.path.append(dirname(realpath(__file__)) + "/../src/dunes"))
# pylint: disable=wrong-import-position
import version_selector

@patch('version_selector.available_versions_from_url')
@pytest.mark.safe
def test_version_selector_leap(mock_available_versions):
    # Arrange
    mock_available_versions.return_value = ["v1"]

    # Act
    result = version_selector.available_versions("leap")

    # Assert
    assert result == ["v1"]
    mock_available_versions.assert_called_once_with(
        "https://api.github.com/repos/antelopeio/leap/releases")


@patch('version_selector.available_versions_from_url')
@pytest.mark.safe
def test_version_selector_cdt(mock_available_versions):
    # Arrange
    mock_available_versions.return_value = ["v1", "v2"]

    # Act
    result = version_selector.available_versions("CdT")

    # Assert
    assert result == ["v1", "v2"]
    mock_available_versions.assert_called_once_with(
        "https://api.github.com/repos/antelopeio/cdt/releases")


@pytest.mark.safe
class test_version_selector(TestCase):
    @patch('version_selector.available_versions')
    @patch('builtins.input')
    def test_version_selector_exit_low(self, mock_input, mock_available_versions):
        mock_input.return_value = "0"
        mock_available_versions.return_value = ["v1", "v2"]

        with self.assertRaises(SystemExit):
            version_selector.get_version("leap")

    @patch('version_selector.available_versions')
    @patch('builtins.input')
    def test_version_selector_exit_high(self, mock_input, mock_available_versions):
        mock_input.return_value = "3"
        mock_available_versions.return_value = ["v1", "v2"]

        with self.assertRaises(SystemExit):
            version_selector.get_version("leap")

    @patch('version_selector.available_versions')
    @patch('builtins.input')
    def test_version_selector_exit_invalid(self, mock_input, mock_available_versions):
        mock_input.return_value = "abc"
        mock_available_versions.return_value = ["v1", "v2"]

        with self.assertRaises(SystemExit):
            version_selector.get_version("cdt")
