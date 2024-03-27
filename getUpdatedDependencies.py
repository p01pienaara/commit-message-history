import subprocess
import os
from git import Repo
import re
import json

def get_latest_releases(repo_url, num_releases=4):
    """Gets a specified number of latest release tags from a Git repository.

    Args:
        repo_url: The URL of the Git repository.
        num_releases: The number of release tags to retrieve.

    Returns:
        A list of release tags (e.g., ["v2.1.0", "v2.0.1"]).
    """

    repo = Repo.clone_from(repo_url, ".temp_repo")
    tags = sorted(repo.tags, key=lambda t: t.commit.committed_datetime, reverse=True)
    repo.close()
    return [tag.name for tag in tags[:num_releases]]

def get_diff_between_releases(repo_path, release_tag1, release_tag2, file_path=None):
    """Gets the diff between two releases in a Git repository using GitPython.

    Args:
        repo_path: The path to the local Git repository.
        release_tag1: The tag of the first release.
        release_tag2: The tag of the second release.
        file_path: Optional path to a specific file (if you want the diff for a single file).

    Returns:
        A string containing the diff output.
    """

    repo = Repo(repo_path)

    # Get the commit objects associated with the release tags
    commit1 = repo.commit(release_tag1)
    commit2 = repo.commit(release_tag2)

    # Generate the diff
    if file_path:
        diff = commit1.diff(commit2, paths=file_path, create_patch=True)
    else:
        diff = commit1.diff(commit2, create_patch=True) 

    # Collect diff output for each file changed
    output = ""
    for diff_item in diff:
        output += str(diff_item)  # This includes the diff itself and metadata

    return output

def compare_dependencies(repo_url, num_releases):
    """Compares dependencies between two releases and returns changed dependencies.

    Args:
        repo_url: The URL of the Git repository.
        latest_release: The tag of the latest release.
        previous_release: The tag of the previous release (n-1).

    Returns:
    """
    releases = get_latest_releases(repo_url, num_releases)
    print(f"releases: {releases}")

    return get_diff_between_releases(".temp_repo",releases[num_releases-1], releases[0], "pubspec.yaml")

def compare_dependencies(repo_url, range):
    """Compares dependencies between two releases and returns changed dependencies.

    Args:
        repo_url: The URL of the Git repository.
        latest_release: The tag of the latest release.
        previous_release: The tag of the previous release (n-1).

    Returns:
    """
    print(f"releases: {range[0], range[1]}")
    repo = Repo.clone_from(repo_url, ".temp_repo")
    tags = sorted(repo.tags, key=lambda t: t.commit.committed_datetime, reverse=True)
    repo.close()

    return get_diff_between_releases(".temp_repo",range[1], range[0], "pubspec.yaml")

def parse_git_diff(repo_url, diff_text):
    """Parses git diff output and extracts dependency information.

    Args:
        diff_text: The raw text of the git diff output.

    Returns:
        A list of dictionaries, each containing dependency information in the format:
          { 
             "url": ...,
             "path": ..., 
             "old_version": ..., 
             "new_version": ...
          }
    """

    results = []
    current_dependency = None

    for line in diff_text.splitlines():
        if line.startswith("---") or line.startswith("+++"):
            continue  # Skip header lines

        match = re.search(r"name:\s*(.*)$", line)  # Base name
        if match:
            if current_dependency is None:
                current_dependency = {}
            current_dependency["url"] = repo_url
            current_dependency["path"] = match.group(1)
            continue

        match = re.search(r"\-version:\s*(.*)$", line)  # Base old version
        if match:
            current_dependency["old_version"] = match.group(1)
            continue

        match = re.search(r"\+version:\s*(.*)$", line)  # Base new version
        if match:
            current_dependency["new_version"] = match.group(1)
            results.append(current_dependency)
            current_dependency = None
            continue

        match = re.search(r"^\s*\-\s*ref:\s*(.*)$", line)  # Old version
        if match:
            current_dependency["old_version"] = match.group(1)
            continue

        match = re.search(r"^\s*\+\s*ref:\s*(.*)$", line)  # New version
        if match:
            current_dependency["new_version"] = match.group(1)
            results.append(current_dependency)
            current_dependency = None  # Reset for the next dependency
            continue

        # Find url and path lines
        match = re.search(r"url:\s*(.*)$", line)
        if match:
            if current_dependency is None:
                current_dependency = {}
            current_dependency["url"] = match.group(1)

        match = re.search(r"path:\s*(.*)$", line)
        if match:
            if current_dependency is None:
                current_dependency = {}
            current_dependency["path"] = match.group(1)

    return results

def write_dependencies_to_file(filename, all_dependencies):
    """Writes commit messages to a text file.

    Args:
        filename: The name of the output text file.
        all_commits: A list of commit messages, grouped by dependency and release tag.
                     (This would be an output from combining both of your previous scripts.) 
    """

    with open(filename, "w") as f:
        for commit in all_dependencies:
            f.write(f"- {commit}\n")

def update(repo_url, num_releases):
    changed_dependencies = compare_dependencies(repo_url, num_releases)

    subprocess.run(["rm", "-rf", ".temp_repo"])

    print("changed:")
    print(changed_dependencies)

    dependenciesJson = parse_git_diff(repo_url, changed_dependencies)

    print(dependenciesJson)

    with open("dependencies.json", "w") as outfile:
        json.dump(dependenciesJson, outfile, indent=4)

def updateWithRange(repo_url, range):
    changed_dependencies = compare_dependencies(repo_url, range)

    subprocess.run(["rm", "-rf", ".temp_repo"])

    print("changed:")
    print(changed_dependencies)

    dependenciesJson = parse_git_diff(repo_url, changed_dependencies)

    print(dependenciesJson)

    with open("dependencies.json", "w") as outfile:
        json.dump(dependenciesJson, outfile, indent=4)

def purgeIfNeeded():
    if os.path.exists(f".temp_repo"):
        subprocess.run(["rm", "-rf", ".temp_repo"])
