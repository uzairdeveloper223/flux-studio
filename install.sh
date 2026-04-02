#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

readonly REPO="uzairdeveloper223/flux-studio"
readonly RAW_BASE="https://raw.githubusercontent.com/${REPO}/main"
readonly DEST_DIR="/content/flux-studio"

command -v python3 &>/dev/null || { printf 'error: python3 not found\n' >&2; exit 1; }
command -v wget   &>/dev/null || { printf 'error: wget not found\n'    >&2; exit 1; }

mkdir -p "${DEST_DIR}"

printf 'downloading flux-studio ...\n'
wget -q -O "${DEST_DIR}/run_comfyui.py" "${RAW_BASE}/run_comfyui.py"
wget -q -O "${DEST_DIR}/workflow.json"   "${RAW_BASE}/workflow.json"

printf 'starting ...\n'
exec python3 "${DEST_DIR}/run_comfyui.py"
