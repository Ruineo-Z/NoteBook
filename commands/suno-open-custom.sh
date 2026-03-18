#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   commands/suno-open-custom.sh [workspace_name] [session_name]
#
# Examples:
#   commands/suno-open-custom.sh
#   commands/suno-open-custom.sh "Ruinow Workspace"
#   HEADED=0 commands/suno-open-custom.sh "Ruinow Workspace" "suno-ci"

WORKSPACE_NAME="${1:-${WORKSPACE_NAME:-Ruinow Workspace}}"
SESSION_NAME="${2:-${SESSION_NAME:-suno}}"
STATE_FILE="${STATE_FILE:-$HOME/.agent-browser/suno.auth-state.json}"
CHROME_BIN="${CHROME_BIN:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
HEADED="${HEADED:-1}"
RESET_DAEMON="${RESET_DAEMON:-1}"

if ! command -v agent-browser >/dev/null 2>&1; then
  echo "agent-browser is not installed or not in PATH." >&2
  exit 127
fi

if [[ ! -f "$STATE_FILE" ]]; then
  echo "State file not found: $STATE_FILE" >&2
  echo "Please login once and save state first." >&2
  exit 1
fi

if [[ ! -x "$CHROME_BIN" ]]; then
  echo "Chrome executable not found: $CHROME_BIN" >&2
  exit 1
fi

echo "[1/4] Open Suno create page..."
restart_daemon() {
  pkill -f '/opt/homebrew/lib/node_modules/agent-browser/.*/daemon.js' >/dev/null 2>&1 || true
  sleep 1
}

open_create_page() {
  local args=(
    --session "$SESSION_NAME"
    --executable-path "$CHROME_BIN"
    --state "$STATE_FILE"
  )
  if [[ "$HEADED" == "1" ]]; then
    args=(--headed "${args[@]}")
  fi

  if ! agent-browser "${args[@]}" open "https://suno.com/create" >/dev/null 2>/tmp/suno-open-custom.err; then
    if grep -qE 'daemon already running|Browser not launched|Arguments can not specify page' /tmp/suno-open-custom.err; then
      echo "  browser daemon not clean, restarting daemon..."
      restart_daemon
      agent-browser "${args[@]}" open "https://suno.com/create" >/dev/null
    else
      cat /tmp/suno-open-custom.err >&2
      return 1
    fi
  fi

  agent-browser --session "$SESSION_NAME" wait 1500 >/dev/null || true
}

if [[ "$RESET_DAEMON" == "1" ]]; then
  echo "  resetting browser daemon to apply state/executable..."
  restart_daemon
fi

open_create_page

workspace_escaped=$(printf '%s' "$WORKSPACE_NAME" | sed 's/\\/\\\\/g; s/"/\\"/g')

echo "[2/4] Select workspace: $WORKSPACE_NAME"
workspace_found=0
for attempt in 1 2 3 4 5 6 7 8; do
  workspace_result=$(
    cat <<EOF | agent-browser --session "$SESSION_NAME" eval --stdin
const target = "${workspace_escaped}";
const nodes = Array.from(document.querySelectorAll('button,[role="button"],a'));
const loginRequired = nodes.some(el => (el.innerText || '').trim() === 'Sign In');
const workspace = nodes.find(el => (el.innerText || '').includes(target));
if (workspace) workspace.click();
({ loginRequired, workspaceFound: Boolean(workspace), url: location.href });
EOF
  )
  echo "  attempt $attempt: $workspace_result"

  if [[ "$workspace_result" == *'"loginRequired": true'* ]]; then
    echo "Suno session is not logged in. Refresh auth state first." >&2
    exit 2
  fi

  if [[ "$workspace_result" == *'"workspaceFound": true'* ]]; then
    workspace_found=1
    break
  fi

  agent-browser --session "$SESSION_NAME" wait 700 >/dev/null || true
done

if [[ "$workspace_found" != "1" ]]; then
  echo "Workspace not found: $WORKSPACE_NAME" >&2
  exit 2
fi

agent-browser --session "$SESSION_NAME" wait 700 >/dev/null || true

echo "[3/4] Switch to Custom mode"
custom_found=0
custom_activated=0
for attempt in 1 2 3 4; do
  custom_click_result=$(
    cat <<'EOF' | agent-browser --session "$SESSION_NAME" eval --stdin
const controls = Array.from(document.querySelectorAll('button,[role="button"],a'));
const modeButtons = controls.filter(el => {
  const txt = (el.innerText || '').trim();
  return txt === 'Simple' || txt === 'Custom';
});

const isActive = (el) => {
  const cls = (el.className || '').toString();
  return (
    el.getAttribute('aria-pressed') === 'true' ||
    el.getAttribute('aria-selected') === 'true' ||
    el.getAttribute('data-state') === 'active' ||
    /\bactive\b/.test(cls)
  );
};

const customCandidates = modeButtons.filter(el => (el.innerText || '').trim() === 'Custom');
const preferred = customCandidates.find(el => /\be1g6uss70\b/.test((el.className || '').toString()));
const targets = preferred ? [preferred, ...customCandidates.filter(el => el !== preferred)] : customCandidates;

let customActivated = false;
let clickedCount = 0;
for (const t of targets) {
  t.click();
  clickedCount += 1;

  const now = Array.from(document.querySelectorAll('button,[role="button"],a'))
    .filter(el => ['Simple', 'Custom'].includes((el.innerText || '').trim()));
  const customNow = now.filter(el => (el.innerText || '').trim() === 'Custom');
  if (customNow.some(isActive)) {
    customActivated = true;
    break;
  }
}

({
  customFound: customCandidates.length > 0,
  customActivated,
  clickedCount,
  url: location.href
});
EOF
  )
  echo "  attempt $attempt: $custom_click_result"

  if [[ "$custom_click_result" == *'"customFound": true'* ]]; then
    custom_found=1
  fi

  if [[ "$custom_click_result" == *'"customActivated": true'* ]]; then
    custom_activated=1
    break
  fi

  agent-browser --session "$SESSION_NAME" wait 500 >/dev/null || true
done

if [[ "$custom_found" != "1" ]]; then
  echo "Custom mode control not found." >&2
  exit 3
fi

agent-browser --session "$SESSION_NAME" wait 700 >/dev/null || true

echo "[4/4] Verify current state and pause"
status=$(
  cat <<'EOF' | agent-browser --session "$SESSION_NAME" eval --stdin
const modeButtons = Array.from(document.querySelectorAll('button,[role="button"],a'))
  .filter(el => ['Simple', 'Custom'].includes((el.innerText || '').trim()))
  .map(el => ({
    text: (el.innerText || '').trim(),
    className: (el.className || '').toString(),
    ariaPressed: el.getAttribute('aria-pressed'),
    ariaSelected: el.getAttribute('aria-selected'),
    dataState: el.getAttribute('data-state')
  }));

const customActive = modeButtons.some(m =>
  m.text === 'Custom' &&
  (
    m.ariaPressed === 'true' ||
    m.ariaSelected === 'true' ||
    m.dataState === 'active' ||
    /\bactive\b/.test(m.className)
  )
);

({
  url: location.href,
  workspaceIdInUrl: location.href.includes('wid='),
  customActive,
  modeButtons
});
EOF
)
echo "$status"

if [[ "$status" != *'"customActive": true'* ]]; then
  echo "Custom mode may not be active; please check current page." >&2
  exit 4
fi

echo "Ready and paused: workspace selected + Custom mode active."
