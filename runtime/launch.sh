#!/bin/sh
set -eu
port=${BETAFLIGHT_UCONSOLE_PORT:-5176}
case "$port" in *[!0-9]*|'') echo 'Invalid port' >&2; exit 1;; esac
systemctl --user start betaflight-uconsole.service
for browser in chromium chromium-browser; do
    if command -v "$browser" >/dev/null 2>&1; then
        exec "$browser" --user-data-dir="$HOME/.local/share/betaflight-uconsole/browser" --app="http://127.0.0.1:$port"
    fi
done
echo 'Install Chromium using the operating system package manager.' >&2
exit 1
