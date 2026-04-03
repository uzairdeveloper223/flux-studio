#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

readonly REPO="uzairdeveloper223/flux-studio"
readonly RAW_BASE="https://raw.githubusercontent.com/${REPO}/main"

_detect_platform() {
    if [[ -d "/kaggle" ]]; then
        printf 'kaggle'
    elif [[ -d "/content" ]]; then
        printf 'colab'
    else
        printf 'unknown'
    fi
}

readonly PLATFORM="$(_detect_platform)"

case "${PLATFORM}" in
    colab)
        readonly DEST_DIR="/content/flux-studio"
        readonly SCRIPT="run_comfyui.py"
        ;;
    kaggle)
        readonly DEST_DIR="/kaggle/working/flux-studio"
        readonly SCRIPT="run_comfyui_kaggle.py"
        ;;
    *)
        printf 'error: unsupported platform (expected Colab or Kaggle)\n' >&2
        exit 1
        ;;
esac

command -v python3 &>/dev/null || { printf 'error: python3 not found\n' >&2; exit 1; }
command -v wget   &>/dev/null || { printf 'error: wget not found\n'    >&2; exit 1; }

mkdir -p "${DEST_DIR}"

printf 'platform: %s\n' "${PLATFORM}"
printf 'downloading flux-studio ...\n'
wget -q -O "${DEST_DIR}/run_comfyui.py" "${RAW_BASE}/${SCRIPT}"
wget -q -O "${DEST_DIR}/workflow.json"   "${RAW_BASE}/workflow.json"

printf 'starting ...\n'
exec python3 "${DEST_DIR}/run_comfyui.py"
