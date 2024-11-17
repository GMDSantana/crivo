#!/bin/bash

# ╔██████╗██████╗ ██╗██╗     ██╗╔██████╗
# ██╔════╝██╔══██╗██║╚██╗   ██╔╝██╔═══██╗
# ██║     ██████╔╝██║ ╚██╗ ██╔╝ ██║   ██║
# ██║     ██╔██═╝ ██║  ╚████╔╝  ██║   ██╝
# ╚██████╗██║ ██╗ ██║   ╚██╔╝   ╚██████╝
# © Guilherme Santana
# https://gmdsantana.com
# https://github.com/GMDSantana/crivo

# install_dependencies.sh
# Script to automate the installation of dependencies for Crivo

# Update package list and upgrade existing packages
sudo apt update && sudo apt upgrade -y

# Install Python 3 and pip if not already installed
sudo apt install -y python3 python3-pip

# Install required Python packages
pip3 install -r ../requirements.txt

# Confirm successful installation
echo "Dependencies installed successfully."

