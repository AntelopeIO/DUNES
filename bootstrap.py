#!/usr/bin/env python3

import os
import platform
import subprocess
import argparse
import sys


# Find path for root and source.
DUNES_ROOT = os.path.dirname(os.path.abspath(__file__))
DUNES_SRC  = os.path.join(DUNES_ROOT , *['src','dunes'])

# Import version info rather than call DUNES executable.
sys.path.insert(0, DUNES_SRC)
from version import version_full # pylint: disable=import-error, wrong-import-position



def commit_hash():
    """Determine the short git commit hash value for this repo."""

    git_command = ['git', '-C', DUNES_ROOT, 'rev-parse', '--short', 'HEAD']
    try:
        return subprocess.check_output(git_command, stderr=None, encoding='utf-8').strip()
    except Exception as err:  # pylint: disable=bad-option-value, broad-exception-caught
        print( f'Failed to determine git short hash: {err=}', file=sys.stderr)
    return None


def push_image(tag, verbose=False, dry_run=False):      # pylint: disable=redefined-outer-name
    """Attempt to push tagged builds to ghcr.io."""

    push_command = ['docker', 'push', tag]

    if verbose:
        print(f'Push: {push_command}')

    if dry_run:
        return True

    if not subprocess.run(push_command, stderr=None, check=False).returncode:
        return True

    print(f'Failed to push image {tag}.', file=sys.stderr)
    return False


def tag_image(tag, verbose=False, dry_run=False):        # pylint: disable=redefined-outer-name
    """Tag an existing 'dunes' image with the provided tag."""

    if tag is None:
        return False

    tag_command = ['docker', 'tag', 'dunes', tag]

    if verbose:
        print(f'Tagging: {tag_command}')

    if dry_run is True:
        return True

    # expect a zero result for success
    if not subprocess.run(tag_command, stderr=None, check=False).returncode:
        return True

    print(f'Failed to apply tag: {tag}', file=sys.stderr)
    return False


def build_image(leap_version=None, cdt_version=None, contracts_version=None, tag='dunes', verbose=False, dry_run=False):  # pylint: disable=too-many-arguments, redefined-outer-name
    """Build a docker image for working with DUNES.

    """

    barg = '--build-arg'

    # Set user id to a default value
    user_id = 0

    # Set group id based on platform
    group_id = 0
    if platform.system() == "Darwin":
        group_id = 200

    # pylint: disable=line-too-long
    build_command = ['docker', 'build', '--no-cache', '-f','Dockerfile', '-t',tag, barg,f'USER_ID={user_id}', barg,f'GROUP_ID={group_id}', DUNES_ROOT]

    if leap_version:
        build_command.extend( [barg, f'LEAP_VERSION={leap_version}'] )

    if cdt_version:
        build_command.extend( [barg, f'CDT_VERSION={cdt_version}'] )

    if contracts_version:
        build_command.extend( [barg, f'CONTRACTS_VERSION={contracts_version}'] )

    if verbose:
        print(f'Build command: {build_command}' )

    if dry_run:
        return True

    if not subprocess.run(build_command, stderr=None, check=False).returncode:
        return True

    print('Failed to build the image.', file=sys.stderr)
    return False


if __name__ == "__main__":

    # Create the CLI code
    parser = argparse.ArgumentParser(
        prog='bootstrap',
        description='Generate a Docker image for DUNES.'
        #epilog='Text at the bottom of help'
    )

    # Add arguments.
    #  pylint:disable=line-too-long
    parser.add_argument('-c', '--cdt',    dest='cdt_version',    action='store',      help='Set the leap version to CDT_VERSION.')
    parser.add_argument('-l', '--leap',   dest='leap_version',   action='store',      help='Set the CDT version to LEAP_VERSION.')
    parser.add_argument('--contracts',       dest='contracts_version', action='store',help='Set the reference-contract version to CONTRACTS_VERSION. Nominally a commit hash.')
    parser.add_argument('-r','--release', dest='release_build',  action='store_true', help='Tag the image with the version reported by DUNES.')
    parser.add_argument('-p','--push',    dest='push_image',     action='store_true', help='Push release and latest image to ghcr.io. Implies --release.')
    parser.add_argument('--tag',          dest='tag',            action='store',      help='ONLY tag the image with the user provided tag TAG.')
    parser.add_argument('--verbose',      dest='verbose',        action='store_true', help='Print the commands as they are executed.')
    parser.add_argument('--dry-run',      dest='dry_run',        action='store_true', help='Perform a dry run: print the commands that would be executed and exit with success.')

    # Parse the arguments.
    args = parser.parse_args()


    # Handle setting dependent arguments.
    if args.push_image:
        args.release_build=True
    if args.dry_run:
        print("Performing dry run.")
        args.verbose=True


    # Apply sanity checking.
    if args.tag and args.release_build: # remember push_image implies release_build
        parser.print_help(sys.stderr)
        print('\nError: --tag is incompatible with --release', file=sys.stderr)
        if args.push_image:
            print('Error: --tag is incompatible with --push', file=sys.stderr)
        sys.exit(1)


    # Determine the tag.
    # pylint: disable=invalid-name
    tag = 'dunes'
    if args.tag:
        tag = args.tag

    # Call the build command
    if not build_image(
        tag=tag,
        cdt_version=args.cdt_version,
        leap_version=args.leap_version,
        contracts_version=args.contracts_version,
        verbose=args.verbose,
        dry_run=args.dry_run,):

        sys.exit(1)

    # If the user sent us an explicit tag, then we are done here.
    if args.tag:
        sys.exit(0)

    # Determine which tags we need.
    tags = []
    if args.release_build:
        ver = version_full()
        tags.extend( [f'dunes:{ver}', f'ghcr.io/antelopeio/dunes:{ver}', 'ghcr.io/antelopeio/dunes:latest'] )

    # Attempt the tagging
    tag_result = True
    for mytag in tags:
        tag_result &= tag_image(mytag, verbose=args.verbose, dry_run=args.dry_run)

    # Report an error
    if not tag_result and not args.push_image:
        print('Not all tagging succeeded.', file=sys.stderr)
        sys.exit(1)

    push_result = True
    if args.push_image:
        if not tag_result:
            print('Not all tagging succeeded, will not attempt to push builds.', file=sys.stderr)
            sys.exit(1)

        for mytag in tags:
            push_result &= push_image(mytag, verbose=args.verbose, dry_run=args.dry_run)

    if not push_result:
        print('Failed to push some tagged images.', file=sys.stderr)

    commit_hash_result=True
    commit_hash = commit_hash()
    if commit_hash:
        commit_hash_result = tag_image(f'dunes:{commit_hash}', verbose=args.verbose, dry_run=args.dry_run)

    if commit_hash_result and push_result and tag_result:
        sys.exit(0)

    sys.exit(1)
