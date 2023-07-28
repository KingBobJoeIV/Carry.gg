import random
import requests
from app.core.constants import SKINS


def get_border_by_level(level):
    if 30 <= level < 50:
        pass


def skin_info():
    base_url = "https://api.github.com/repos/"
    username = "InFinity54"
    repository = "Lol_DDragon"
    branch = "master"  # Replace with the desired branch name
    directory_path = "img/champion/loading/"

    # Step 1: Get the SHA of the latest commit on the specified branch
    commit_url = f"{base_url}{username}/{repository}/commits/{branch}"
    response = requests.get(commit_url)
    if response.status_code == 200:
        commit_data = response.json()
        latest_commit_sha = commit_data["sha"]
    else:
        print("Error:", response.status_code)
        exit()

    # Step 2: Get the tree of the latest commit
    tree_url = f"{base_url}{username}/{repository}/git/trees/{latest_commit_sha}?recursive=1"
    response = requests.get(tree_url)
    if response.status_code == 200:
        tree_data = response.json()
        files_in_directory = [
            item["path"] for item in tree_data["tree"] if item["type"] == "blob" and directory_path in item["path"]
        ]
    else:
        print("Error:", response.status_code)
        exit()

    # Step 3: Filter files that are specifically in the directory
    files_in_directory = [file_name for file_name in files_in_directory if file_name.startswith(directory_path)]

    # Step 4: Create global mapping
    for s in files_in_directory:
        data = s.split("/")[-1].split("_")
        if data[0] not in SKINS: # champ
            SKINS[data[0]] = []
        SKINS[data[0]].append(int(data[1].split(".")[0])) # add the number


def randomize_skins_by_champ(name):
    return random.choice(SKINS[name])
