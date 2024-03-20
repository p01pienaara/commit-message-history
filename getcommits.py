
import os
import subprocess
from git import Repo
import json

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

def get_commit_messages(repo_url, num_releases=3):
    """Fetches commit messages from a repository for a specified number of releases.

    Args:
        repo_url: The URL of the Git repository.
        num_releases: The number of recent releases to consider.

    Returns:
        A list of commit messages, grouped by release tag.
    """

    if not os.path.exists(".temp_repo"):  # Create a temporary directory
        os.mkdir(".temp_repo")

    os.chdir(".temp_repo")
    subprocess.run(["git", "clone", repo_url])  # Clone the repository

    repo_name = repo_url.split("/")[-1].replace(".git", "")
    os.chdir(repo_name)

    # Get release tags
    release_tags = subprocess.check_output(
        ["git", "tag", "-l", "--sort=-version:refname"]
    ).decode("utf-8").splitlines()[:num_releases]

    all_commits = []
    for i in range(len(release_tags)):
        if i == len(release_tags) - 1:
            start_tag = "HEAD"  # Get from beginning to latest tag
        else:
            start_tag = release_tags[i + 1]

        commits = subprocess.check_output(
            ["git", "log", "--pretty=format:%s", f"{start_tag}..{release_tags[i]}"]
        ).decode("utf-8").splitlines()
        all_commits.append((release_tags[i], commits))

    os.chdir("../..")  # Clean up
    subprocess.run(["rm", "-rf", ".temp_repo"])
    return all_commits

def write_commits_to_file(filename, all_commits):
    """Writes commit messages to a text file.

    Args:
        filename: The name of the output text file.
        all_commits: A list of commit messages, grouped by dependency and release tag.
                     (This would be an output from combining both of your previous scripts.) 
    """

    with open(filename, "w") as f:
        for commit in all_commits:
            f.write(f"- {commit}\n")

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
    filepath = "dependencies.json"  # Assuming your JSON data is in this file
    dependencies = read_json_file(filepath)

    all_commits = []
    for repo in dependencies:
        path = repo["url"]
        if os.path.exists(f".temp_repo/{path}"):  # check if repo has already been done
            continue
        commits_by_release = get_commit_messages_between_releases(path, repo["old_version"], repo["new_version"])
        print(commits_by_release)
        repo_name = repo["path"]
        print(f"--- Commits for {repo_name} ---")
        all_commits.append('')
        all_commits.append(f"--- Commits for {repo_name} ---")
        all_commits.append('')
        for commit in commits_by_release:
            if "🚀" in commit or "Merge " in commit:
                continue
            print(f"{commit}")
            all_commits.append(f"{commit}")

    subprocess.run(["rm", "-rf", ".temp_repo"])
    # Write to file
    write_commits_to_file("commit_log.txt", all_commits)

