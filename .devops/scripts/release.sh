#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/../.." && pwd -P)"
DEV_BRANCH="dev"
MAIN_BRANCH="main"
CHECKOUT_SCRIPT="$SCRIPT_DIR/checkout-branch.sh"

usage() {
  cat <<'USAGE'
Usage: release.sh [version]

Fast-forwards main from dev, pushes to origin, and triggers GitHub Actions deploy.
Optionally creates a GitHub release with the provided version tag.

Examples:
  release.sh           # Just merge dev → main and deploy
  release.sh v1.2.0    # Merge, deploy, and create release v1.2.0
USAGE
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

VERSION="${1:-}"

cd "$REPO_ROOT"

if [[ -n "$(git status --porcelain)" ]]; then
  echo "Error: uncommitted changes. Commit or stash first." >&2
  exit 1
fi

printf '\n==> Syncing %s branch\n' "$DEV_BRANCH"
"$CHECKOUT_SCRIPT" "$DEV_BRANCH"
git push origin "$DEV_BRANCH"

printf '\n==> Syncing %s branch\n' "$MAIN_BRANCH"
"$CHECKOUT_SCRIPT" "$MAIN_BRANCH"

printf '\n==> Fast-forwarding %s from %s\n' "$MAIN_BRANCH" "$DEV_BRANCH"
if ! git merge --ff-only "$DEV_BRANCH"; then
  echo "Error: cannot fast-forward. Resolve manually." >&2
  exit 1
fi

git push origin "$MAIN_BRANCH"

if [[ -n "$VERSION" ]]; then
  printf '\n==> Creating GitHub release %s\n' "$VERSION"
  gh release create "$VERSION" --title "$VERSION" --generate-notes
fi

printf '\n✅ Release pushed! GitHub Actions deploying from %s.\n' "$MAIN_BRANCH"

printf '\n==> Switching back to %s\n' "$DEV_BRANCH"
"$CHECKOUT_SCRIPT" "$DEV_BRANCH"
