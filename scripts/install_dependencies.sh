#!/usr/bin/env bash

# ╔██████╗██████╗ ██╗██╗     ██╗╔██████╗
# ██╔════╝██╔══██╗██║╚██╗   ██╔╝██╔═══██╗
# ██║     ██████╔╝██║ ╚██╗ ██╔╝ ██║   ██║
# ██║     ██╔██═╝ ██║  ╚████╔╝  ██║   ██╝
# ╚██████╗██║ ██╗ ██║   ╚██╔╝   ╚██████╝
# © Guilherme Santana
# https://gmdsantana.com
# https://github.com/GMDSantana/crivo

# install_dependencies.sh
# Installs Crivo and its dependencies into a virtual environment (.venv) in
# the repository. Works from any directory and does not upgrade system
# packages. Pass --dev to also install the test dependencies.
#
# Usage: scripts/install_dependencies.sh [--dev]

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${REPO_DIR}/.venv"
PYTHON="${PYTHON:-python3}"

REQUIREMENTS="requirements.txt"
if [[ "${1:-}" == "--dev" ]]; then
    REQUIREMENTS="requirements-dev.txt"
fi

if ! command -v "${PYTHON}" >/dev/null 2>&1 || ! "${PYTHON}" -c 'import venv, ensurepip' >/dev/null 2>&1; then
    if command -v apt-get >/dev/null 2>&1; then
        echo "Installing Python 3 and venv support with apt..."
        sudo apt-get update
        sudo apt-get install -y python3 python3-venv python3-pip
    else
        echo "Error: Python 3 with the venv module is required (looked for '${PYTHON}')." >&2
        exit 1
    fi
fi

if ! "${PYTHON}" -c 'import sys; sys.exit(sys.version_info < (3, 10))'; then
    echo "Error: Crivo requires Python 3.10 or newer; '${PYTHON}' is $("${PYTHON}" -V 2>&1)." >&2
    exit 1
fi

if [[ ! -x "${VENV_DIR}/bin/python" ]]; then
    echo "Creating virtual environment in ${VENV_DIR}..."
    "${PYTHON}" -m venv "${VENV_DIR}"
fi

"${VENV_DIR}/bin/python" -m pip install --upgrade pip
"${VENV_DIR}/bin/python" -m pip install -r "${REPO_DIR}/${REQUIREMENTS}"
"${VENV_DIR}/bin/python" -m pip install -e "${REPO_DIR}"

echo "Dependencies installed successfully."
echo "Activate the environment with: source ${VENV_DIR}/bin/activate"
echo "Then run: crivo --help"
