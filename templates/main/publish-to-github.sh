#!/bin/bash
# Script to publish the main repository and submodules to GitHub
# 
# Usage:
#   1. Create three repositories on GitHub:
#      - ${PROJECT_NAME} (main repo)
#      - ${PROJECT_NAME}-core (backend submodule)
#      - ${PROJECT_NAME}-web (frontend submodule)
#   2. Update the URLs below with your GitHub username and repository names
#   3. Run this script from the main repository root

set -e

# Configuration - UPDATE THESE WITH YOUR GITHUB DETAILS
GITHUB_USERNAME="yourusername"
MAIN_REPO_NAME="${PROJECT_NAME}"
CORE_REPO_NAME="${PROJECT_NAME}-core"
WEB_REPO_NAME="${PROJECT_NAME}-web"

# Build GitHub URLs (using SSH)
MAIN_REPO="git@github.com:${GITHUB_USERNAME}/${MAIN_REPO_NAME}.git"
CORE_REPO="git@github.com:${GITHUB_USERNAME}/${CORE_REPO_NAME}.git"
WEB_REPO="git@github.com:${GITHUB_USERNAME}/${WEB_REPO_NAME}.git"

# Function to get current branch name
get_current_branch() {
    git rev-parse --abbrev-ref HEAD
}

# Function to create and push first-commit branch
create_and_push_first_commit_branch() {
    local remote_url="$1"
    
    # Get the first commit hash
    local first_commit=$(git rev-list --max-parents=0 HEAD | head -n 1)
    
    if [ -z "$first_commit" ]; then
        echo "  ⚠ Warning: Could not find first commit"
        return 1
    fi
    
    # Check if first-commit branch already exists
    if git show-ref --verify --quiet refs/heads/first-commit; then
        echo "  Branch 'first-commit' already exists, updating..."
        git branch -f first-commit "$first_commit"
    else
        echo "  Creating 'first-commit' branch from first commit..."
        git branch first-commit "$first_commit"
    fi
    
    # Push the first-commit branch
    echo "  Pushing 'first-commit' branch..."
    git push -u origin first-commit || {
        echo "  ⚠ Warning: Failed to push first-commit branch"
        return 1
    }
    
    return 0
}

# Function to push to remote, trying main first, then master, then current branch
push_to_remote() {
    local remote_url="$1"
    local current_branch=$(get_current_branch)
    
    # Try main first
    if git show-ref --verify --quiet refs/heads/main; then
        echo "  Pushing main branch..."
        git push -u origin main && return 0
    fi
    
    # Try master
    if git show-ref --verify --quiet refs/heads/master; then
        echo "  Pushing master branch..."
        git push -u origin master && return 0
    fi
    
    # Fall back to current branch
    echo "  Pushing current branch (${current_branch})..."
    git push -u origin "${current_branch}" && return 0
    
    echo "  ⚠ Error: Could not determine branch to push"
    return 1
}

echo "═══════════════════════════════════════════════════════════"
echo "Publishing to GitHub"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Main repo:    ${MAIN_REPO}"
echo "Core repo:    ${CORE_REPO}"
echo "Web repo:     ${WEB_REPO}"
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."
echo ""

# Push core submodule
echo "Pushing core submodule..."
cd ${BACKEND_NAME}
if git remote get-url origin >/dev/null 2>&1; then
    echo "  Updating existing remote..."
    git remote set-url origin "$CORE_REPO"
else
    echo "  Adding remote..."
    git remote add origin "$CORE_REPO"
fi

# Create and push first-commit branch
set +e  # Temporarily disable exit on error
create_and_push_first_commit_branch "$CORE_REPO"
first_commit_result=$?
set -e  # Re-enable exit on error

# Also push the current branch
set +e  # Temporarily disable exit on error for push
push_to_remote "$CORE_REPO"
push_result=$?
set -e  # Re-enable exit on error

if [ $first_commit_result -eq 0 ] && [ $push_result -eq 0 ]; then
    echo "  ✓ Core submodule pushed (including first-commit branch)"
else
    echo "  ✗ Failed to push core submodule"
    exit 1
fi
cd ..
echo ""

# Push web submodule
echo "Pushing web submodule..."
cd ${FRONTEND_NAME}
if git remote get-url origin >/dev/null 2>&1; then
    echo "  Updating existing remote..."
    git remote set-url origin "$WEB_REPO"
else
    echo "  Adding remote..."
    git remote add origin "$WEB_REPO"
fi

# Create and push first-commit branch
set +e  # Temporarily disable exit on error
create_and_push_first_commit_branch "$WEB_REPO"
first_commit_result=$?
set -e  # Re-enable exit on error

# Also push the current branch
set +e  # Temporarily disable exit on error for push
push_to_remote "$WEB_REPO"
push_result=$?
set -e  # Re-enable exit on error

if [ $first_commit_result -eq 0 ] && [ $push_result -eq 0 ]; then
    echo "  ✓ Web submodule pushed (including first-commit branch)"
else
    echo "  ✗ Failed to push web submodule"
    exit 1
fi
cd ..
echo ""

# Update .gitmodules with GitHub URLs and branch tracking
echo "Updating .gitmodules..."
if [ -f .gitmodules ]; then
    # Create updated .gitmodules using awk
    awk -v core_repo="${CORE_REPO}" \
        -v web_repo="${WEB_REPO}" \
        -v backend_name="${BACKEND_NAME}" \
        -v frontend_name="${FRONTEND_NAME}" \
    '
    BEGIN {
        in_core = 0
        in_web = 0
        core_url_done = 0
        web_url_done = 0
        core_branch_done = 0
        web_branch_done = 0
        core_ignore_done = 0
        web_ignore_done = 0
    }
    /^\[submodule "/ {
        if ($0 ~ backend_name) {
            in_core = 1
            in_web = 0
            core_url_done = 0
            core_branch_done = 0
            core_ignore_done = 0
        } else if ($0 ~ frontend_name) {
            in_web = 1
            in_core = 0
            web_url_done = 0
            web_branch_done = 0
            web_ignore_done = 0
        } else {
            in_core = 0
            in_web = 0
        }
        print
        next
    }
    /^\[/ {
        in_core = 0
        in_web = 0
        print
        next
    }
    in_core && /^\s*url\s*=/ {
        print "\turl = " core_repo
        core_url_done = 1
        # Always add branch and ignore right after URL
        print "\tbranch = first-commit"
        print "\tignore = all"
        core_branch_done = 1
        core_ignore_done = 1
        next
    }
    in_core && /^\s*branch\s*=/ {
        print "\tbranch = first-commit"
        core_branch_done = 1
        next
    }
    in_core && /^\s*ignore\s*=/ {
        print "\tignore = all"
        core_ignore_done = 1
        next
    }
    in_web && /^\s*url\s*=/ {
        print "\turl = " web_repo
        web_url_done = 1
        # Always add branch and ignore right after URL
        print "\tbranch = first-commit"
        print "\tignore = all"
        web_branch_done = 1
        web_ignore_done = 1
        next
    }
    in_web && /^\s*branch\s*=/ {
        print "\tbranch = first-commit"
        web_branch_done = 1
        next
    }
    in_web && /^\s*ignore\s*=/ {
        print "\tignore = all"
        web_ignore_done = 1
        next
    }
    {
        # Default action: print the line
        print
    }
    ' .gitmodules > .gitmodules.tmp && mv .gitmodules.tmp .gitmodules
    
    # Sync submodule URLs
    git submodule sync
    
    # Stage the updated .gitmodules
    git add .gitmodules
    git commit -m "Update submodule URLs to GitHub remotes, set branch tracking to first-commit, and ignore = all" || echo "  (No changes to commit)"
    echo "  ✓ .gitmodules updated with branch tracking"
else
    echo "  ⚠ Warning: .gitmodules not found"
fi
echo ""

# Push main repository
echo "Pushing main repository..."
if git remote get-url origin >/dev/null 2>&1; then
    echo "  Updating existing remote..."
    git remote set-url origin "$MAIN_REPO"
else
    echo "  Adding remote..."
    git remote add origin "$MAIN_REPO"
fi
set +e  # Temporarily disable exit on error for push
push_to_remote "$MAIN_REPO"
push_result=$?
set -e  # Re-enable exit on error
if [ $push_result -eq 0 ]; then
    echo "  ✓ Main repository pushed"
else
    echo "  ✗ Failed to push main repository"
    exit 1
fi
echo ""

echo "═══════════════════════════════════════════════════════════"
echo "✓ All repositories published to GitHub!"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "To clone this repository with submodules, use:"
echo "  git clone --recurse-submodules ${MAIN_REPO}"
echo ""

