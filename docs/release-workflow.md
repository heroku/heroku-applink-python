# Release Workflow
updated: 05/16/2025

This document describes the process for releasing new versions of the heroku-applink-python library.

## Overview

The release process is automated through GitHub Actions and consists of three main workflows:

1. Package Library (`package.yml`)
2. Create Tag (`create-tag.yml`)
3. Publish Release (`publish.yml`)

## Release Process

### 1. Creating a Release Branch

There are two ways to start a release:

#### Option 1: GitHub Actions Workflow
1. Go to the "Actions" tab in GitHub
2. Select "Draft Release Branch" workflow
3. Click "Run workflow"
4. Select the type of version bump (major, minor, patch)
5. Optionally provide the previous version for changelog generation

#### Option 2: Command Line Script
Run the draft-release script locally:
```bash
# For a minor version bump
./scripts/release/draft-release minor

# You can also bump from a specific previous version
./scripts/release/draft-release patch 1.2.2
```

Both methods will:
- Create a new release branch (e.g., `release-v1.0.0`)
- Update version in `pyproject.toml`
- Update `CHANGELOG.md` with all changes since the last release
- Create a draft pull request

### 2. Testing and Building

When a pull request is pushed into main from a branch named "release-*:

1. The Package Library workflow runs automatically and:
   - Runs tests across Python 3.10, 3.11, 3.12, and 3.13
   - Runs linting with Ruff
   - Builds the package
   - Uploads the build artifacts from the build

### 3. Creating a Release Tag

After the release branch pull request is merged to main:

1. The Create Tag workflow is triggered, and automatically:
   - Extracts the version from the release branch name
   - Creates a new tag (e.g., `v1.0.0`)
   - Pushes the tag to the repository

### 4. Publishing the Release

When a new tag is pushed during the create tag workflow:

1. The Publish Release workflow is triggered, and automatically:
   - Checks for deployment moratorium using TPS
   - Downloads the build artifacts from the build job
   - Creates a GitHub release with the artifacts
   - Publishes the package to PyPI
   - Records the release in Change Management

## Workflow Files

### package.yml
- Triggers on pushes to main and pull requests
- Runs tests and linting
- Builds the package
- Uploads artifacts when merging from release branches

### create-tag.yml
- Triggers on successful completion of Package Library workflow if it is a release branch
- Creates and pushes version tags

### publish.yml
- Triggers on new version tags pushed to main
- Handles the actual release process
- Publishes to GitHub, PyPI, and Change Management

## Requirements

- GitHub Actions permissions for:
  - `contents: write` (for creating releases)
  - `id-token: write` (for PyPI publishing)
- Environment secrets:
  - `TPS_API_TOKEN_PARAM` - stored in token store
  - `TPS_API_RELEASE_ACTOR_EMAIL` - brittany.jones@heroku.com

## Best Practices

1. Always use the "Draft Release Branch" workflow to start releases
2. Review the changelog entries before merging
3. Ensure all tests pass before merging
4. Wait for the complete release process to finish before starting a new release

### Rolling Back

If an issue is discovered in a production released version:

1. **DO NOT** roll back the release in code or revert the tag
2. Create a new release branch with a version bump
3. Fix the issue in the new release branch
4. Follow the standard release process to deploy the fix
5. Document the issue and fix in the changelog

This "fix forward" approach ensures:
- A clear audit trail of changes
- Proper versioning of fixes
- Consistent release history
- No disruption to users who have already upgraded 