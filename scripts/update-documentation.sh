#!/bin/bash

# update-documentation.sh
# Script to update version in pyproject.toml and CHANGELOG.md with git log entries since last tag
#
# Usage:
#   ./scripts/update-documentation.sh 0.1.1
#
# This will:
#   1. Update the version in pyproject.toml
#   2. Update CHANGELOG.md with all commits since the last tag
#   3. Format the changelog with proper headers and commit references

set -e

# Function to print usage
usage() {
    echo "Usage: $0 <version>"
    echo "Example: $0 0.1.1"
    exit 1
}

# Function to update version in pyproject.toml
update_pyproject_version() {
    local version=$1
    local pyproject_file="pyproject.toml"
    
    if [ ! -f "$pyproject_file" ]; then
        echo "Error: $pyproject_file not found"
        exit 1
    fi
    
    # Update version in pyproject.toml
    sed -i '' "s/^version = \".*\"/version = \"$version\"/" "$pyproject_file"
    echo "Updated version to $version in $pyproject_file"
}

# Function to categorize commit message
categorize_commit() {
    local message=$1
    local hash=$2
    local body=$3

    # First try conventional commit format
    if [[ "$message" =~ ^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\([a-z-]+\))?: ]]; then
        local type="${BASH_REMATCH[1]}"
        case "$type" in
            feat) echo "features" ;;
            fix) echo "fixes" ;;
            docs) echo "docs" ;;
            *) echo "other" ;;
        esac
        return
    fi

    # If not conventional, analyze message content
    message_lower=$(echo "$message" | tr '[:upper:]' '[:lower:]')
    
    # Features
    if [[ "$message_lower" =~ ^(add|create|implement|new|update|upgrade|enhance|improve|support|adds|creates|implements|updates|upgrades|enhances|improves|supports) ]]; then
        echo "features"
        return
    fi

    # Bug Fixes
    if [[ "$message_lower" =~ ^(fix|fixes|fixed|resolve|resolves|resolved|correct|corrects|corrected|bug|issue|error|err|typo) ]]; then
        echo "fixes"
        return
    fi

    # Documentation
    if [[ "$message_lower" =~ ^(doc|docs|document|documentation|readme|comment|comments|note|notes|changelog) ]]; then
        echo "docs"
        return
    fi

    # Default to other
    echo "other"
}

# Check if version is provided
if [ $# -ne 1 ]; then
    usage
fi

VERSION=$1
CHANGELOG_FILE="CHANGELOG.md"
TODAY=$(date +%Y-%m-%d)

# Update version in pyproject.toml
update_pyproject_version "$VERSION"

# Get the last tag
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")

echo "Last tag: $LAST_TAG"

# Get the previous tag for comparison link
PREV_TAG=""
if [ -n "$LAST_TAG" ]; then
    # Get all tags sorted by creation date
    TAGS=($(git tag --sort=creatordate))
    for ((i=0; i<${#TAGS[@]}; i++)); do
        if [ "${TAGS[$i]}" = "$LAST_TAG" ] && [ $i -gt 0 ]; then
            PREV_TAG="${TAGS[$((i-1))]}"
            break
        fi
    done
fi

echo "Previous tag: $PREV_TAG"

# Get the repository URL
REPO_URL=$(git config --get remote.origin.url | sed 's/\.git$//' | sed 's/git@github.com:/https:\/\/github.com\//')

echo "Repository URL: $REPO_URL"

# Create temporary directory for our files
TEMP_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_DIR"' EXIT

# Create temporary files in the temp directory
NEW_CONTENT="$TEMP_DIR/new_content"
FEATURES_TMP="$TEMP_DIR/features"
FIXES_TMP="$TEMP_DIR/fixes"
DOCS_TMP="$TEMP_DIR/docs"
OTHER_TMP="$TEMP_DIR/other"
OLD_CONTENT="$TEMP_DIR/old_content"

# Save the old changelog if it exists
if [ -f "$CHANGELOG_FILE" ]; then
    cp "$CHANGELOG_FILE" "$OLD_CONTENT"
fi

# Create the new version content
if [ -n "$PREV_TAG" ]; then
    VERSION_HEADER="# [$VERSION]($REPO_URL/compare/$PREV_TAG...$VERSION) ($TODAY)"
else
    VERSION_HEADER="# [$VERSION]($REPO_URL/compare/HEAD...$VERSION) ($TODAY)"
fi

echo "Version header: $VERSION_HEADER"

cat > "$NEW_CONTENT" << EOL
$VERSION_HEADER


EOL

# Get all commits since last tag
if [ -n "$LAST_TAG" ]; then
    COMMITS=$(git log --pretty=format:"%s|%H" $LAST_TAG..HEAD)
else
    COMMITS=$(git log --pretty=format:"%s|%H")
fi

echo "Found $(echo "$COMMITS" | wc -l) commits to process"

echo "$COMMITS" | while IFS='|' read -r message hash; do
    # Skip merge commits
    if [[ ! $message =~ ^Merge ]]; then
        # Format the commit message
        if [[ "$message" =~ ^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\([a-z-]+\))?: ]]; then
            # Remove the type prefix for conventional commits
            formatted_message="${message#*:}"
        else
            formatted_message="$message"
        fi

        # Add breaking change notice if present
        if [[ "$formatted_message" == *"BREAKING CHANGE"* ]]; then
            formatted_message="$formatted_message (BREAKING CHANGE)"
        fi

        # Extract PR or issue number if present in the message
        ref_number=""
        ref_type=""
        # Look for (#1234) or #1234 in the message
        if [[ "$message" =~ \(#([0-9]+)\) ]]; then
            ref_number="${BASH_REMATCH[1]}"
            ref_type="pull"
        elif [[ "$message" =~ \#([0-9]+) ]]; then
            ref_number="${BASH_REMATCH[1]}"
            ref_type="issues"
        fi

        # Format the reference with PR/issue and commit hash
        if [ -n "$ref_number" ]; then
            reference="([#$ref_number]($REPO_URL/$ref_type/$ref_number)) ([${hash:0:7}]($REPO_URL/commit/$hash))"
        else
            reference="([${hash:0:7}]($REPO_URL/commit/$hash))"
        fi

        # Categorize the commit
        category=$(categorize_commit "$message" "$hash" "$formatted_message")
        
        echo "Processing commit: $message ($category)"
        
        # Add to appropriate category file
        case "$category" in
            features) echo "* $formatted_message $reference" >> "$FEATURES_TMP" ;;
            fixes) echo "* $formatted_message $reference" >> "$FIXES_TMP" ;;
            docs) echo "* $formatted_message $reference" >> "$DOCS_TMP" ;;
            other) echo "* $formatted_message $reference" >> "$OTHER_TMP" ;;
        esac
    fi
done

# Append categorized commits in order
if [ -s "$FEATURES_TMP" ]; then
    echo "### Features" >> "$NEW_CONTENT"
    cat "$FEATURES_TMP" >> "$NEW_CONTENT"
    echo -e "\n\n" >> "$NEW_CONTENT"
fi

if [ -s "$FIXES_TMP" ]; then
    echo "### Bug Fixes" >> "$NEW_CONTENT"
    cat "$FIXES_TMP" >> "$NEW_CONTENT"
    echo -e "\n\n" >> "$NEW_CONTENT"
fi

if [ -s "$DOCS_TMP" ]; then
    echo "### Documentation" >> "$NEW_CONTENT"
    cat "$DOCS_TMP" >> "$NEW_CONTENT"
    echo -e "\n\n" >> "$NEW_CONTENT"
fi

if [ -s "$OTHER_TMP" ]; then
    echo "### Other Changes" >> "$NEW_CONTENT"
    cat "$OTHER_TMP" >> "$NEW_CONTENT"
    echo -e "\n\n" >> "$NEW_CONTENT"
fi

# Create the new changelog file
if [ -f "$OLD_CONTENT" ]; then
    # Extract the header (up to and including the guidelines)
    HEADER_END_LINE=$(awk '/^# Change ?Log$/ {h=1} h && /^$/ {print NR; exit}' "$OLD_CONTENT")
    if [ -z "$HEADER_END_LINE" ]; then
        HEADER_END_LINE=4 # fallback if no blank line found
    fi
    # Write the standardized header
    echo "# ChangeLog" > "$CHANGELOG_FILE"
    echo >> "$CHANGELOG_FILE"
    echo "All notable changes to this project will be documented in this file." >> "$CHANGELOG_FILE"
    echo "See [Conventional Commits](https://conventionalcommits.org) for commit guidelines." >> "$CHANGELOG_FILE"
    echo >> "$CHANGELOG_FILE"
    # Insert the new version entry
    cat "$NEW_CONTENT" >> "$CHANGELOG_FILE"
    # Append the rest of the old changelog, skipping any duplicate header or blank lines
    tail -n +$((HEADER_END_LINE + 1)) "$OLD_CONTENT" | sed '/^# Change ?Log$/d;/^All notable changes to this project will be documented in this file\./d;/^See \[Conventional Commits\]/d' >> "$CHANGELOG_FILE"
else
    # If no old content, just use the new content
    cat "$NEW_CONTENT" > "$CHANGELOG_FILE"
fi

echo "Changelog updated successfully for version $VERSION"
