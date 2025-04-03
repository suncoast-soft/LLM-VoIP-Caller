#!/bin/bash
set -e

echo ">>> Updating system and installing core dependencies..."
sudo apt update && sudo apt upgrade -y
sudo apt install -y \
  software-properties-common build-essential curl git wget unzip \
  libssl-dev libffi-dev libxml2-dev libxslt1-dev zlib1g-dev \
  libncurses5-dev libsqlite3-dev uuid-dev libjansson-dev libedit-dev libreadline-dev \
  libsndfile1 espeak ffmpeg python3.10 python3.10-dev python3.10-venv

echo ">>> Creating Python 3.10 virtual environment..."
python3.10 -m venv venv
source venv/bin/activate

echo ">>> Upgrading pip and installing dependencies from requirements.txt..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

echo ">>> Downloading and building Asterisk from source..."
cd /usr/src
sudo wget http://downloads.asterisk.org/pub/telephony/asterisk/asterisk-20-current.tar.gz
sudo tar -xzf asterisk-20-current.tar.gz
cd asterisk-20*/

echo ">>> Downloading MP3 codec and installing Asterisk prerequisites..."
sudo contrib/scripts/get_mp3_source.sh
sudo contrib/scripts/install_prereq install

echo ">>> Configuring and building Asterisk..."
sudo ./configure
sudo make menuselect # optional: interactive config
sudo make -j$(nproc)
sudo make install
sudo make samples
sudo make config

echo ">>> Creating Asterisk user and fixing permissions..."
sudo useradd -m asterisk || true
sudo chown -R asterisk:asterisk /var/lib/asterisk /etc/asterisk /var/{log,run,spool}/asterisk /usr/lib/asterisk
sudo sed -i 's|^#runuser.*|runuser = asterisk|' /etc/asterisk/asterisk.conf
sudo sed -i 's|^#rungroup.*|rungroup = asterisk|' /etc/asterisk/asterisk.conf

echo ">>> Starting Asterisk as a system service..."
sudo systemctl restart asterisk

echo ">>> Checking Asterisk CLI availability..."
sudo asterisk -rx "core show version"

echo "✅ All done! To connect to Asterisk, run: sudo asterisk -rvvv"
