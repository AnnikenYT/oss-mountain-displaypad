#!/usr/bin/env bash
# Automated release script for oss-mountain-displaypad packages.
# Usage: ./scripts/release.sh [patch|minor|major|VERSION]

set -euo pipefail

# 0. Ensure working tree is clean
if [ -n "$(git status --porcelain)" ]; then
  echo "❌ Error: Git working tree is dirty. Please commit or stash changes before releasing."
  exit 1
fi

BUMP_TYPE="${1:-patch}"

# 1. Bump versions using Poetry
echo "📦 Bumping version ($BUMP_TYPE)..."
cd packages/driver
poetry version "$BUMP_TYPE"
NEW_VERSION=$(poetry version -s)
cd ../library
poetry version "$NEW_VERSION"

# Update inter-package dependency in library pyproject.toml
if [[ "$OSTYPE" == "darwin"* ]]; then
  sed -i '' "s/displaypad-driver>=[0-9.]*/displaypad-driver>=$NEW_VERSION/" pyproject.toml
else
  sed -i "s/displaypad-driver>=[0-9.]*/displaypad-driver>=$NEW_VERSION/" pyproject.toml
fi
cd ../..

# Update __version__ strings in __init__.py files
if [[ "$OSTYPE" == "darwin"* ]]; then
  sed -i '' "s/__version__ = \"[0-9.]*\"/__version__ = \"$NEW_VERSION\"/" packages/driver/src/displaypad_driver/__init__.py
  sed -i '' "s/__version__ = \"[0-9.]*\"/__version__ = \"$NEW_VERSION\"/" packages/library/src/displaypad_lib/__init__.py
else
  sed -i "s/__version__ = \"[0-9.]*\"/__version__ = \"$NEW_VERSION\"/" packages/driver/src/displaypad_driver/__init__.py
  sed -i "s/__version__ = \"[0-9.]*\"/__version__ = \"$NEW_VERSION\"/" packages/library/src/displaypad_lib/__init__.py
fi

TAG="v$NEW_VERSION"
echo "✨ Target Version: $NEW_VERSION (Tag: $TAG)"

# 2. Commit version bump
git add packages/driver/pyproject.toml \
        packages/library/pyproject.toml \
        packages/driver/src/displaypad_driver/__init__.py \
        packages/library/src/displaypad_lib/__init__.py

git commit -m "chore(release): bump version to $TAG"

# 3. Create git tag
git tag "$TAG"

# 4. Push commit and tags to remote
echo "🚀 Pushing commit and tags to remote..."
git push origin main --tags

echo "🎉 Successfully tagged and pushed $TAG!"
