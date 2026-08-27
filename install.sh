#!/bin/sh
# Legacy source checkout installer.
#
# The npm entry point is bin/project-interview-skill.js. This wrapper exists so
# users who cloned the repository can still run ./install.sh with the same flags.

set -eu

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CLI="${SCRIPT_DIR}/bin/project-interview-skill.js"

if ! command -v node >/dev/null 2>&1; then
    printf '[error] Node.js is required for this installer.\n' >&2
    printf 'Install Node.js, then run one of:\n' >&2
    printf '  npx project-interview-skill install --trae\n' >&2
    printf '  ./install.sh --trae\n' >&2
    exit 1
fi

if [ ! -f "$CLI" ]; then
    printf '[error] Missing CLI entry: %s\n' "$CLI" >&2
    exit 1
fi

case "${1:-}" in
    install|doctor|help|--help|-h)
        exec node "$CLI" "$@"
        ;;
    *)
        exec node "$CLI" install "$@"
        ;;
esac
