import json
import sys
import requests


def available_versions_from_url(url):
    versions = []
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    response = requests.get(url, headers=headers, timeout=30)
    data = json.loads(response.text)

    for release in data:
        versions.append(release["tag_name"])

    return versions


def available_versions(project):
    url = ""
    project_lowercase = project.lower()

    if project_lowercase == "leap":
        url = "https://api.github.com/repos/antelopeio/leap/releases"
    elif project_lowercase == "cdt":
        url = "https://api.github.com/repos/antelopeio/cdt/releases"
    else:
        print("Unknown project " + project)
        sys.exit()

    return available_versions_from_url(url)


def get_version(project):
    versions = available_versions(project)
    print("Available " + project + " versions:")
    for index, version in enumerate(versions):
        print(str(index + 1) + ") " + version)

    user_choice = input(
        "Enter which version you want to choose [1," + str(len(versions)) + "]? ")
    try:
        user_choice = int(user_choice)
    # pylint: disable=bare-except
    except:
        print("Improper version choosen.")
        sys.exit()

    if user_choice < 1 or user_choice > len(versions):
        print("Improper version choosen.")
        sys.exit()

    chosen_element = versions[user_choice - 1]

    return chosen_element[1:]
