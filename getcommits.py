
import os
import subprocess
from git import Repo
import json
import datetime

def get_commit_messages_between_releases(repo_url, newer_version, older_version=None):
    """Gets all commit messages between two releases in a Git repository.

    Args:
        repo_path: The path to the local Git repository.
        older_version: The tag of the older release.
        newer_version: The tag of the newer release.

    Returns:
        A list of commit messages.
    """

    repo = Repo.clone_from(repo_url, f".temp_repo/{repo_url}")
    commit_messages = []
    if older_version is not None:

        # Ensure that release_tag1 is older than release_tag2 (if necessary):
        base = repo.merge_base(older_version, newer_version)  # Find common ancestor
        if repo.is_ancestor(newer_version, base):  # release_tag2 is newer
            older_version, newer_version = newer_version, older_version

        commit_messages = repo.iter_commits(f"{older_version}..{newer_version}")
    else:
        commit_messages = repo.iter_commits(f"{newer_version}")
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
        print(repo)
        if "url" not in repo or "new_version" not in repo:
            print("XXX - ERROR: \n" + repo)
            continue

        path = repo["url"]        
        new_version = repo["new_version"]
        old_version = None
        if "old_version" in repo:
            old_version = repo["old_version"]

        if os.path.exists(f".temp_repo/{path}"):  # check if repo has already been created
            continue

        commits_by_release = get_commit_messages_between_releases(path, new_version, old_version)
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

