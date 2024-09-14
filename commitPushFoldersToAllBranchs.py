import os
import subprocess
import sys
import shutil

def run_command(command):
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.stdout.decode().strip(), result.stderr.decode().strip()

def copy_folders_to_branch(repo_directory, source_directory, branch):
    print(f"Switching to branch: {branch}")
    
    # Checkout the branch
    stdout, stderr = run_command(f"git checkout {branch}")
    if stderr:
        print(f"Failed to checkout branch {branch}: {stderr}")
        return

    # Copy all folders from the source directory to the current branch
    for item in os.listdir(source_directory):
        source_path = os.path.join(source_directory, item)
        destination_path = os.path.join(repo_directory, item)
        
        if os.path.isdir(source_path):
            shutil.copytree(source_path, destination_path, dirs_exist_ok=True)
        else:
            shutil.copy2(source_path, destination_path)

    # Stage, commit, and push the changes
    run_command("git add .")
    commit_message = f"Add new folders from {source_directory} to {branch}"
    run_command(f"git commit -m '{commit_message}'")
    run_command(f"git push origin {branch}")
    print(f"Successfully added folders from {source_directory} to {branch}")

def main():
    # Check if the correct number of arguments was provided
    if len(sys.argv) != 3:
        print("Usage: python script.py /path/to/repo /path/to/folder_with_multiple_folders")
        sys.exit(1)

    repo_directory = sys.argv[1]
    source_directory = sys.argv[2]

    # Check if the provided repo path exists and is a git repository
    if not os.path.isdir(os.path.join(repo_directory, '.git')):
        print(f"Error: Directory {repo_directory} is not a Git repository.")
        sys.exit(1)

    # Check if the provided source directory path exists
    if not os.path.isdir(source_directory):
        print(f"Error: Directory {source_directory} does not exist.")
        sys.exit(1)

    # Change to the repo directory
    os.chdir(repo_directory)

    # Get all local branches
    branches, _ = run_command("git branch --format='%(refname:short)'")
    branches = branches.splitlines()

    # First, start with the main branch (or any default branch you use)
    run_command("git checkout main")
    print("Switched to main branch")

    # Copy the folders and commit to the main branch
    copy_folders_to_branch(repo_directory, source_directory, "main")

    # Loop through each branch and apply the folder addition, excluding 'main' since it's already done
    for branch in branches:
        branch = branch.strip()
        if branch != "main":
            copy_folders_to_branch(repo_directory, source_directory, branch)

    # Return to the main branch after the process is done (optional)
    run_command("git checkout main")
    print("All done!")

if __name__ == "__main__":
    main()
