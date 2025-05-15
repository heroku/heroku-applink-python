#!/bin/bash

# Check if at least two arguments are provided
if [ "$#" -lt 2 ]; then
    echo "Usage: $0 <bump_type> <previous_version>"
    echo "bump_type: major, minor, or patch"
    echo "previous_version: version to bump from (e.g., 1.2.3)"
    exit 1
fi

BUMP_TYPE=$1
PREV_VERSION=$2

# Validate bump type
if [[ ! "$BUMP_TYPE" =~ ^(major|minor|patch)$ ]]; then
    echo "Error: bump_type must be major, minor, or patch"
    exit 1
fi

# Validate version format
if [[ ! "$PREV_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Error: previous_version must be in format X.Y.Z (e.g., 1.2.3)"
    exit 1
fi

# Split version into components
IFS='.' read -r -a VERSION_PARTS <<< "$PREV_VERSION"
MAJOR="${VERSION_PARTS[0]}"
MINOR="${VERSION_PARTS[1]}"
PATCH="${VERSION_PARTS[2]}"

# Generate new version based on bump type
case $BUMP_TYPE in
    major)
        NEW_VERSION="$((MAJOR + 1)).0.0"
        ;;
    minor)
        NEW_VERSION="${MAJOR}.$((MINOR + 1)).0"
        ;;
    patch)
        NEW_VERSION="${MAJOR}.${MINOR}.$((PATCH + 1))"
        ;;
esac

# Check if we're on main branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "Error: Must be on main branch to create release branch"
    exit 1
fi

# Check if gh CLI is installed and authenticated
if ! command -v gh &> /dev/null; then
    echo "Error: GitHub CLI (gh) is not installed"
    exit 1
fi

if ! gh auth status &> /dev/null; then
    echo "Error: GitHub CLI is not authenticated"
    exit 1
fi

# Create new branch
BRANCH_NAME="release-v${NEW_VERSION}"
git checkout -b "$BRANCH_NAME"

# Update version in pyproject.toml
sed -i '' "s/version = \".*\"/version = \"${NEW_VERSION}\"/" pyproject.toml

# Update documentation
./scripts/update-release-documentation.sh "$NEW_VERSION" "$PREV_VERSION"

# Commit changes
git add pyproject.toml CHANGELOG.md
git commit -m "Bump version to ${NEW_VERSION}"

# Push branch
git push -u origin "$BRANCH_NAME"

# Create pull request
gh pr create \
    --title "Release ${NEW_VERSION}" \
    --body "## Changes in this release
$(cat CHANGELOG.md | sed -n '/^## \[Unreleased\]/,/^## \[/p' | sed '1d' | sed '$d')

## Release Process
1. Review changes
2. Merge this PR
3. Create a tag from the release branch
4. The tag will trigger the publish workflow" \
    --base main \
    --head "$BRANCH_NAME"

echo "Created release branch: $BRANCH_NAME"
echo "Created pull request for version $NEW_VERSION" 
