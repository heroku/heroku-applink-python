#!/usr/bin/env bash

set -e -o pipefail

MAIN_BRANCH="main"

# Function to display usage
usage() {
    echo "Usage: $0 <bump_type> <release_type> [previous_version]"
    echo "  bump_type: major, minor, or patch"
    echo "  release_type: stable, beta, or alpha"
    echo "  previous_version: optional previous version for changelog"
    exit 1
}

# Function to get commit messages for changelog
get_changelog() {
    local since_tag=$1
    if [[ -z "$since_tag" ]]; then
        git log --graph --format="%h %s" | while read -r line; do
            echo "* $line"
        done
    else
        git log --graph --format="%h %s" "${since_tag}..HEAD" | while read -r line; do
            echo "* $line"
        done
    fi
}

# Check if required arguments are provided
if [ "$#" -lt 2 ] || [ "$#" -gt 3 ]; then
    usage
fi

BUMP_TYPE=$1
RELEASE_TYPE=$2
PREV_VERSION=$3

# Validate bump type
if [[ ! "$BUMP_TYPE" =~ ^(major|minor|patch)$ ]]; then
    echo "Error: bump_type must be one of: major, minor, patch"
    usage
fi

# Validate release type
if [[ ! "$RELEASE_TYPE" =~ ^(stable|beta|alpha)$ ]]; then
    echo "Error: release_type must be one of: stable, beta, alpha"
    usage
fi

# Get current version from pyproject.toml
CURRENT_VERSION=$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
BASE_VERSION=$(echo "$CURRENT_VERSION" | sed 's/-[a-z].*$//')

# Split version into components
IFS='.' read -r -a VERSION_PARTS <<< "$BASE_VERSION"
MAJOR="${VERSION_PARTS[0]}"
MINOR="${VERSION_PARTS[1]}"
PATCH="${VERSION_PARTS[2]}"

# Generate new version based on bump type
case "$BUMP_TYPE" in
    major)
        NEW_VERSION="$((MAJOR + 1)).0.0"
        ;;
    minor)
        NEW_VERSION="$MAJOR.$((MINOR + 1)).0"
        ;;
    patch)
        NEW_VERSION="$MAJOR.$MINOR.$((PATCH + 1))"
        ;;
esac

# Add release type suffix if needed
if [ "$RELEASE_TYPE" != "stable" ]; then
    NEW_VERSION="${NEW_VERSION}-${RELEASE_TYPE}"
fi

echo "Current version: $CURRENT_VERSION"
echo "New version: $NEW_VERSION"

# Check if we're on the main branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [[ "$CURRENT_BRANCH" != "$MAIN_BRANCH" && "$CURRENT_BRANCH" != "heads/$MAIN_BRANCH" ]]; then
    echo "Error: Must be on $MAIN_BRANCH branch"
    exit 1
fi

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo "Error: GitHub CLI (gh) is not installed"
    exit 1
fi

# Check if user is authenticated with GitHub
if ! gh auth status &> /dev/null; then
    echo "Error: Not authenticated with GitHub. Please run 'gh auth login'"
    exit 1
fi

# Create new branch
BRANCH_NAME="release-v${NEW_VERSION}"
git checkout -b "$BRANCH_NAME"

# Get changelog
if [ -n "$PREV_VERSION" ]; then
    CHANGELOG=$(get_changelog "v$PREV_VERSION")
else
    CHANGELOG=$(get_changelog)
fi

# For stable releases, update version in pyproject.toml
if [ "$RELEASE_TYPE" = "stable" ]; then
    sed -i '' "s/^version = \".*\"/version = \"$NEW_VERSION\"/" pyproject.toml
    git add pyproject.toml
fi

# Create changelog entry
{
    echo "## [$NEW_VERSION] - $(date +%Y-%m-%d)"
    echo ""
    echo "$CHANGELOG"
    echo ""
} > CHANGELOG.md.new

# Update CHANGELOG.md
if [ -f CHANGELOG.md ]; then
    # Get the header (everything before the first ##)
    sed -n '1,/^##/p' CHANGELOG.md | sed '$d' > CHANGELOG.md.tmp
    # Add the new version section
    cat CHANGELOG.md.new >> CHANGELOG.md.tmp
    # Add the rest of the existing content (everything after the first ##)
    sed -n '/^##/,$p' CHANGELOG.md >> CHANGELOG.md.tmp
    mv CHANGELOG.md.tmp CHANGELOG.md
else
    # Create initial changelog if it doesn't exist
    {
        echo "# Changelog"
        echo ""
        echo "All notable changes to this project will be documented in this file."
        echo ""
        echo "The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),"
        echo "and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)."
        echo ""
        cat CHANGELOG.md.new
    } > CHANGELOG.md
fi
rm CHANGELOG.md.new

# Add and commit changes
git add CHANGELOG.md
git commit -m "$RELEASE_TYPE v$NEW_VERSION"
git push origin "$BRANCH_NAME"

# Create PR
gh pr create \
    --title "$RELEASE_TYPE v$NEW_VERSION" \
    --body "$RELEASE_TYPE version bump and documentation updates.

Changes:
- Updated version to $NEW_VERSION
- Generated changelog
- Created release notes
- Updated documentation
- Using pre-built and tested package" \
    --base main \
    --head "$BRANCH_NAME" \
    --draft

