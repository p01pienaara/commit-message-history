
import os
import subprocess
from git import Repo
import json
import datetime

def get_commit_messages_between_releases(repo_url, release_tag1, release_tag2):
    """Gets all commit messages between two releases in a Git repository.

    Args:
        repo_path: The path to the local Git repository.
        release_tag1: The tag of the older release.
        release_tag2: The tag of the newer release.

    Returns:
        A list of commit messages.
    """

    repo = Repo.clone_from(repo_url, f".temp_repo/{repo_url}")

    # Ensure that release_tag1 is older than release_tag2 (if necessary):
    base = repo.merge_base(release_tag1, release_tag2)  # Find common ancestor
    if repo.is_ancestor(release_tag2, base):  # release_tag2 is newer
        release_tag1, release_tag2 = release_tag2, release_tag1

    commit_messages = repo.iter_commits(f"{release_tag1}..{release_tag2}")
    repo.close()
    return [commit.message for commit in commit_messages]

def write_commits_to_file(filename, all_commits):
    """Writes commit messages to a text file.

    Args:
        filename: The name of the output text file.
        all_commits: A list of commit messages, grouped by dependency and release tag.
                     (This would be an output from combining both of your previous scripts.) 
    """

    with open(filename, "w") as f:
        for commit in all_commits:
            f.write(f"{commit}")

def read_json_file(filepath):
    """Reads data from a JSON file.

    Args:
        filepath: The path to the JSON file.

    Returns:
        The parsed data (often a list or dictionary).
    """

    with open(filepath, "r") as file:
        data = json.load(file)
    return data

def fetch():
    filepath = "dependencies.json"  
    dependencies = read_json_file(filepath)
    
    today = datetime.date.today()
    formatted_date = today.strftime("%d-%m-%Y")
    all_commits = [f"{formatted_date}"]
    for repo in dependencies:
        path = repo["url"]
        old_version = repo["old_version"]
        new_version = repo["new_version"]

        if os.path.exists(f".temp_repo/{path}"):  # check if repo has already been created
            continue

        commits_by_release = get_commit_messages_between_releases(path, old_version, new_version)
        print(commits_by_release)
        repo_name = repo["path"]
        print(f"--- Commits for {repo_name} ---")
        all_commits.append(f"\n--- Commits for {repo_name} ({old_version} - {new_version}) ---\n")
        for commit in commits_by_release:
            if "🚀" in commit or "Merge " in commit:
                continue
            print(f"{commit}")
            all_commits.append(f"{commit}")

    subprocess.run(["rm", "-rf", ".temp_repo"])
    # Write to file
    write_commits_to_file("commit_log.txt", all_commits)

