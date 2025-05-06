#!/usr/bin/env bash

set -e -o pipefail

MAIN_BRANCH="main"

# Usage: ./scripts/create-pre-release-branch.sh 0.3.25 beta patch
# Or:    ./scripts/create-pre-release-branch.sh 0.3.25 "" patch

VERSION="$1"
BETA="$2"
BUMP_TYPE="$3"

if [[ -z "$VERSION" || -z "$BUMP_TYPE" ]]; then
  echo "Usage: $0 <version> <beta (or empty)> <major|minor|patch>"
  exit 1
fi

if [[ "${VERSION}" == *"-"* ]]; then
  echo "package not on stable version. Skipping tagging."
fi

if [[ -n "$BETA" ]]; then
  echo "Pre release detected. This will be published to TestPyPI."
  echo "Make sure to use: python -m pip install --index-url https://test.pypi.org/simple/ your-package-name"
  echo "Skipping version updates in pyproject.toml and documentation for beta release."
fi

if !(command -v gh > /dev/null); then
  echo "GitHub CLI is required for this release script."
  echo "Please install GitHub CLI and try again:"
  echo "https://github.com/cli/cli#installation"
fi

# must be logged into the CLI
if !(gh auth status --hostname "github.com" > /dev/null 2>&1); then
  echo "Not logged into GitHub".
  echo "Please run: gh auth login"
  exit 1
fi

# 1. Checkout and update main branch
# git checkout "${MAIN_BRANCH}"
# git pull origin "${MAIN_BRANCH}"

# # 2. Compose branch name and version string
# if [[ -n "$BETA" ]]; then
#   BRANCH_NAME="${BETA}-release-v${VERSION}-${BUMP_TYPE}"
#   VERSION_STRING="${VERSION}${BETA}"
# else
#   BRANCH_NAME="release-v${VERSION}-${BUMP_TYPE}"
#   VERSION_STRING="${VERSION}"
# fi

# # 3. Create new branch
# git checkout -b "$BRANCH_NAME"
# echo "Created new branch: $BRANCH_NAME"

# 8. Commit all changes
git add .
git commit -m "Bump version to ${VERSION_STRING} for pre-release (${BUMP_TYPE})" || echo "No changes to commit"

# 9. Push the branch
git push --set-upstream origin "$BRANCH_NAME"

# 10. Create a draft pull request using GitHub CLI
if command -v gh >/dev/null 2>&1; then
  if ! gh auth status &>/dev/null; then
    echo "You need to authenticate with GitHub CLI."
    gh auth login
  fi
  gh pr create --base main --head "$BRANCH_NAME" --title "Pre-release: $VERSION_STRING ($BUMP_TYPE)" --body "Automated pre-release PR for version $VERSION_STRING ($BUMP_TYPE)." --draft
  echo "Draft pull request created."
else
  echo "GitHub CLI (gh) not found. Please install it to create a draft PR automatically."
  echo "You can manually open a PR from branch $BRANCH_NAME to main."
fi

echo "Done." 
