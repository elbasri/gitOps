import os
import sys
import subprocess
import shutil

def check_arguments():
    if len(sys.argv) != 3:
        print("Usage: python script.py /path/to/repo /path/to/folder_with_multiple_folders")
        sys.exit(1)

def validate_directories(repo_directory, source_directory):
    # Check if the repo directory is a valid git repository
    if not os.path.isdir(os.path.join(repo_directory, ".git")):
        print(f"Error: Directory {repo_directory} is not a Git repository.")
        sys.exit(1)

    # Check if the source directory exists
    if not os.path.isdir(source_directory):
        print(f"Error: Directory {source_directory} does not exist.")
        sys.exit(1)

def run_command(command, cwd=None):
    result = subprocess.run(command, shell=True, cwd=cwd, text=True, capture_output=True)
    return result.returncode, result.stdout.strip(), result.stderr.strip()

def copy_folders_to_branch(repo_directory, branch, source_directory):
    print(f"Switching to branch: {branch}")
    
    # Checkout the branch
    return_code, stdout, stderr = run_command(f"git checkout {branch}", cwd=repo_directory)
    
    # Handle branch switching
    if return_code != 0:
        print(f"Failed to checkout branch {branch}: {stderr}")
        return
    elif "Already on" in stdout or "Switched to branch" in stdout:
        print(f"Successfully switched to branch {branch}: {stdout}")
    
    # Copy all folders from source directory to the current branch
    for item in os.listdir(source_directory):
        src_path = os.path.join(source_directory, item)
        dest_path = os.path.join(repo_directory, item)
        
        # If the folder already exists in the repo, remove it before copying
        if os.path.exists(dest_path):
            print(f"Folder {item} already exists in the repository. Replacing it.")
            if os.path.isdir(dest_path):
                shutil.rmtree(dest_path)  # Remove directory and all its contents
            else:
                os.remove(dest_path)  # Remove file if it's a file
        
        # Copy the folder or file from source to repo
        if os.path.isdir(src_path):
            shutil.copytree(src_path, dest_path)
        else:
            shutil.copy2(src_path, dest_path)
    
    # Stage, commit, and push the changes
    run_command("git add .", cwd=repo_directory)
    run_command(f'git commit -m "Replace folders from {source_directory} in {branch}"', cwd=repo_directory)
    run_command(f"git push origin {branch}", cwd=repo_directory)
    print(f"Successfully replaced folders from {source_directory} in {branch}")

def main():
    check_arguments()

    repo_directory = sys.argv[1]
    source_directory = sys.argv[2]

    validate_directories(repo_directory, source_directory)

    # Change to the main branch first
    print("Switched to main branch")
    run_command("git checkout main", cwd=repo_directory)
    
    # Copy folders and commit to the main branch
    copy_folders_to_branch(repo_directory, "main", source_directory)

    # Get all branches
    return_code, branches_output, _ = run_command("git branch --format='%(refname:short)'", cwd=repo_directory)
    branches = branches_output.splitlines()

    # Loop through each branch and copy folders, excluding 'main'
    for branch in branches:
        if branch != "main":
            copy_folders_to_branch(repo_directory, branch, source_directory)

    # Optionally switch back to the main branch after completion
    run_command("git checkout main", cwd=repo_directory)
    print("All done!")

if __name__ == "__main__":
    main()
