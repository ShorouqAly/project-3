#!/usr/bin/env bash

# Download and extract static FFmpeg
curl -L https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz -o ffmpeg.tar.xz
tar -xf ffmpeg.tar.xz
cd ffmpeg-*-amd64-static

# Move the binaries into the /usr/local/bin directory (which should be writable on Render at runtime)
mkdir -p ../ffmpeg-bin
cp ffmpeg ffprobe ../ffmpeg-bin/
cd ..

# Make sure the binaries are executable
chmod +x ffmpeg-bin/ffmpeg ffmpeg-bin/ffprobe

# Export path so your app can use it later
export PATH=$PWD/ffmpeg-bin:$PATH

# Continue with Python setup
pip install -r requirements.txt
