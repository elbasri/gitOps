#!/bin/bash

# Check if the correct number of arguments was provided
if [ $# -ne 2 ]; then
    echo "Usage: $0 /path/to/repo /path/to/folder_with_multiple_folders"
    exit 1
fi

# Set the repo and source directory paths from the arguments
repo_directory=$1
source_directory=$2

# Check if the provided repo path exists and is a git repository
if [ ! -d "$repo_directory/.git" ]; then
    echo "Error: Directory $repo_directory is not a Git repository."
    exit 1
fi

# Check if the provided source directory path exists
if [ ! -d "$source_directory" ]; then
    echo "Error: Directory $source_directory does not exist."
    exit 1
fi

# Change to the repo directory
cd "$repo_directory" || exit

# Get all local branches
branches=$(git branch --format='%(refname:short)')

# Function to copy folders and commit the changes
copy_folders_to_branch() {
    branch=$1

    echo "Switching to branch: $branch"

    # Checkout the branch
    git checkout $branch
    if [ $? -ne 0 ]; then
        echo "Failed to checkout branch $branch"
        return
    fi

    # Copy all folders from the source directory to the current branch
    cp -r "$source_directory"/* .

    # Stage, commit, and push the changes
    git add .
    git commit -m "Add new folders from $source_directory to $branch"
    git push origin $branch
    echo "Successfully added folders from $source_directory to $branch"
}

# First, start with the main branch (or any default branch you use)
git checkout main
echo "Switched to main branch"

# Copy the folders and commit to the main branch
copy_folders_to_branch "main"

# Loop through each branch and apply the folder addition, excluding 'main' since it's already done
for branch in $branches
do
    if [ "$branch" != "main" ]; then
        copy_folders_to_branch $branch
    fi
done

# Return to the main branch after the process is done (optional)
git checkout main

echo "All done!"
