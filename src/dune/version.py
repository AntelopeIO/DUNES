import os
import subprocess

FILE_PATH = os.path.dirname(os.path.abspath(__file__))


# VERSION INFORMATION
def version_major():
    return 1


def version_minor():
    return 1


def version_patch():
    return 0


def version_suffix():
    # For pre-release:    `return "-rcX"`
    # For build-metadata: `return "+metadata"`
    return ""


def version_full():
    return str(version_major()) + "." + str(version_minor()) + "." + str(version_patch()) + version_suffix()
