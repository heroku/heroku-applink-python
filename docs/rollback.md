# Applink Python SDK Rollback Guide

This document describes the steps to safely rollback a problem release of the Applink Python SDK on GitHub, PyPI, and TestPyPI. In general, it is best practice to address issues by releasing a new fix or patch, rather than rolling back to a previous release.

---

## When to Rollback

- A critical bug or regression is discovered in the latest release.
- The release was published by mistake.
- Security or compliance issues require immediate rollback.

---

## Rollback Steps

### 1. **Identify the Previous Stable Version**

- Check the [CHANGELOG.md](./CHANGELOG.md) or [release notes](./release_note.md) for the last known good version (e.g., `v1.2.2`).

### 2. **Revert the Release Tag on GitHub**

- Delete the problematic tag locally and remotely:
  ```bash
  git tag -d v1.2.3
  git push origin :refs/tags/v1.2.3
  ```
- (Optional) Delete the corresponding GitHub release from the [Releases](https://github.com/heroku/heroku-applink-python/releases) page.

### 3. **Restore the Previous Version**

- Checkout the commit for the previous stable version:
  ```bash
  git checkout v1.2.2
  ```
- (Optional) Create a rollback branch for clarity:
  ```bash
  git checkout -b rollback-v1.2.2
  ```

### 4. **Re-Publish the Previous Version**

- Create and push a new tag for the rollback (if needed):
  ```bash
  git tag v1.2.4-rollback
  git push origin v1.2.4-rollback
  ```
- This will trigger the release workflow and publish the rollback version.

### 5. **Remove the Problematic Version from PyPI/TestPyPI**

- **PyPI:**  
  - Go to [https://pypi.org/project/heroku-applink/](https://pypi.org/project/heroku-applink/)
  - Click "Manage this project" → "Release history"
  - Find the problematic version and click "Delete"
- **TestPyPI:**  
  - Go to [https://test.pypi.org/project/heroku-applink/](https://test.pypi.org/project/heroku-applink/)
  - Follow the same steps as above.

### 6. **Notify Users**

- Announce the rollback in your project's communication channels (GitHub Discussions, Issues, Slack, etc.).
- Update the [release notes](./release_note.md) and [CHANGELOG.md](./CHANGELOG.md) to document the rollback.

---

## Example Rollback Scenario

Suppose `v1.2.3` introduced a critical bug. To rollback to `v1.2.2`:

1. Delete the `v1.2.3` tag and GitHub release.
2. Delete version `1.2.3` from PyPI/TestPyPI.
3. Tag the previous commit as `v1.2.4-rollback` and push.
4. Let the release workflow publish the rollback version.
5. Notify users and update documentation.

---

## Notes

- PyPI does not allow re-uploading a file for the same version. Always use a new version number for rollbacks (e.g., `v1.2.4-rollback`).
- Rollbacks should be used sparingly and documented clearly.

---

**Questions?**  
Open an issue or ask in the project's discussion board.
