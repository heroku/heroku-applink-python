# Manual and Automated Release Workflows
updated: 06/20/2025

This document describes the process for releasing new versions of the heroku-applink-python library automatically through Github actions, or manually. 

## Overview

The automated release process is automated through GitHub Actions and consists of three main workflows:

1. Test, Lint, and Build (`test-lint-build.yml`)
2. Create Github Tag and Release (`tag-and-release.yml`)
3. Publish to PyPI and Change Management (`publish.yml`)

## Automated Release Process

### 1. Creating a Release Branch

Run the draft-release script locally:
```bash
# For a minor version bump
./scripts/release/draft-release minor

# You can also bump from a specific previous version
./scripts/release/draft-release patch 1.2.2
```

This method will:
- Create a new release branch (e.g., `release-v$VERSION`)
- Update version in `pyproject.toml`
- Update `CHANGELOG.md` with all changes since the last release
- Create a draft pull request

**Requirements**
- Review all changelog entries
- The commit message for the release branch must include "Merge pull request" and "release-v$VERSION" to trigger the release workflows.

ex.
```
Merge pull request release-v$VERSION
```

### 2. Testing and Building

When a pull request is pushed into main from a branch named `release-*`, with commit message `Merge pull request release-*`:

1. The Test, Lint, and Build workflow runs automatically and:
   - Runs tests across Python 3.10, 3.11, 3.12, and 3.13
   - Runs linting with Ruff
   - Builds the package

### 3. Creating a Release Tag

After the release branch pull request is merged to main and the Test, Lint, and Build workflow completes successfully:

1. The Create Github Tag and Release workflow is triggered, and automatically:
   - Extracts the version from the release branch name
   - Creates a new tag (e.g., `v$VERSION`)
   - Pushes the tag to the repository
   - Creates a Github release

### 4. Publishing the Release

When the Create Github Tag and Release workflow completes successfully:

1. The Publish Release workflow is triggered, and automatically:
   - Checks for deployment moratorium using TPS and obtains release lock
   - Checks out the new tag and builds the package
   - Publishes the package to PyPI
   - Records the release in Change Management

## Workflow Files

### test-lint-build.yml
- Triggers on pushes to main and pull requests
- Runs tests and linting
- Builds the package

### tag-and-release.yml
- Triggers on successful completion of Test, Lint, and Build workflow if it is a release branch and contains the necessary commit message
- Creates and pushes version tags
- Creates a Gihub release

### publish.yml
- Triggers on successful completion of Create Github Tag and Release
- Handles the actual release process
- Checks for moratorium and obtains release locks
- Publishes to PyPI, and Change Management

## Requirements

- GitHub Actions permissions for:
  - `contents: write` (for creating releases)
  - `id-token: write` (for PyPI publishing)
- Environment secrets:
  - `TPS_API_TOKEN_PARAM` - stored in token store
  - `TPS_API_RELEASE_ACTOR_EMAIL` - brittany.jones@salesforce.com
- Release Branch Commit Message
   - The commit message for the release branch must include "Merge pull request" and "release-v$VERSION" to trigger the release workflows

## Best Practices

1. Always use the "Draft Release" script to generate the release branch
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


# Manual Release Workflow

The automated release process is new, and may need some debugging pending more runs in production. In the case you need to release a new version and the release workflow in github actions fails, you can do a manual release.

## Manual Release Process

### 1. Creating a Release Branch

Run the draft-release script locally:
```bash
# For a minor version bump, auto generating the version
./scripts/release/draft-release minor

# You can also bump from a specific previous version
./scripts/release/draft-release patch 1.2.2
```

This method will:
- Create a new release branch (e.g., `release-v$VERSION`)
- Update version in `pyproject.toml`
- Update `CHANGELOG.md` with all changes since the last release
- Create a draft pull request

**Requirements**
- Review all changelog entries
- The commit message for the release branch must include "Merge pull request" and "release-v$VERSION" to trigger the release workflows.
```
Merge pull request release-v$VERSION
```

### 2. Moratorium Check and Obtain Release Lock
Run script manually to check for moratorium and obtain release lock.

```bash
# Get the latest SHA from the most recent commit (ensure this commit is the release branch commit to main)
export SHA="$(git rev-parse origin/main)"

./scripts/release/tps-check-lock heroku-applink-python $SHA
```

**Required environment variables**
TPS_API_TOKEN - This can be found in team password manager


### 3. Pushing the tag to Github

Once the release branch as been merged into main, you will want to push the signed tag to github. 

```bash
export VERSION="1.0.0"

git tag -s v$VERSION -m "Release v$VERSION"
```

### 4. Build the package

Check out the latest tag, and then run uv build to build the package. You should see the new version generated in the dist directory. 

```bash
git checkout $(git describe --tags --abbrev=0)

uv build
```

### 5. Create the Github Release

```bash
gh release create v$VERSION --generate-notes dist/*.whl dist/*.tar.gz
```

### 6. Publish to PyPI
Publish the package to pypi using __token__ as the username, and the shared team heroku applink manual publishing token as the token. 

```bash
uv publish
```

### 7. Publish to Change Management
Run script manually to publish to change management. Ensure you are using '@salesforce' email address. 

```bash
export ACTOR_EMAIL="brittany.jones@salesforce.com"

./scripts/release/tps-record-release heroku-applink-python $SHA $ACTOR_EMAIL
```

**Required environment variables**

TPS_API_TOKEN - This can be found in team password manager
