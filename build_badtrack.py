#!/usr/bin/env python3

import os
import shutil
import subprocess

# Get the current working directory
APP_PATH = os.path.abspath(os.path.dirname(__file__))

# Fixed path for the environment variable folders
HISTORY_FOLDER = "/var/lib/badtrack/history"
CACHE_FOLDER = "/var/lib/badtrack/cache"

# Create the badtrack directory structure
os.makedirs(f"{APP_PATH}/badtrack/DEBIAN", exist_ok=True)
os.makedirs(f"{APP_PATH}/badtrack/usr/local/bin/badtrack", exist_ok=True)
os.makedirs(f"{APP_PATH}/badtrack/etc/systemd/system", exist_ok=True)
os.makedirs(f"{APP_PATH}/badtrack/var/lib/badtrack/history", exist_ok=True)
os.makedirs(f"{APP_PATH}/badtrack/var/lib/badtrack/cache", exist_ok=True)

# Copy the main.py file to the badtrack directory and make it executable
shutil.copy('main.py', f"{APP_PATH}/badtrack/usr/local/bin/badtrack/main.py")
os.chmod(f"{APP_PATH}/badtrack/usr/local/bin/badtrack/main.py", 0o755)

# Set perissions for environment variable folders.
os.chmod(f"{APP_PATH}/badtrack/var/lib/badtrack/history",0o755)
os.chmod(f"{APP_PATH}/badtrack/var/lib/badtrack/cache",0o755)

# Create the control file. Reference for dependencies: https://www.debian.org/doc/debian-policy/ch-relationships.html
control_content = """\
Package: badtrack
Version: 1.0.0
Depends: python3
Section: custom
Priority: optional
Architecture: all
Essential: no
Installed-Size: 1024
Maintainer: Your Name <your-email@example.com>
Description: Badtrack is a sample package
"""
with open(f"{APP_PATH}/badtrack/DEBIAN/control", 'w') as file:
    file.write(control_content)

# Create the systemd service file within the package
service_content = f"""\
[Unit]
Description=BadTrack Service
After=network.target

[Service]
Type=simple
User=badtrackuser
WorkingDirectory=/usr/local/bin/badtrack
ExecStart=/usr/bin/python3 /usr/local/bin/badtrack/main.py
Environment=HISTORY_FOLDER={HISTORY_FOLDER}
Environment=CACHE_FOLDER={CACHE_FOLDER}
EnvironmentFile={APP_PATH}/.env


[Install]
WantedBy=multi-user.target
"""
with open(f"{APP_PATH}/badtrack/etc/systemd/system/badtrack.service", 'w') as file:
    file.write(service_content)

# Changing the permissions of the badtrack.service file
os.chmod(f"{APP_PATH}/badtrack/etc/systemd/system/badtrack.service", 0o644)

# Create the post-installation script
postinst_content = f"""\
#!/bin/bash
getent passwd badtrackuser > /dev/null || sudo useradd -r -s /bin/false badtrackuser
# Set ownership of folders to badtrackuser
chown -R badtrackuser:badtrackuser \"{HISTORY_FOLDER}\"
chown -R badtrackuser:badtrackuser \"{CACHE_FOLDER}\"
systemctl enable badtrack
systemctl daemon-reload
systemctl restart badtrack
"""

with open(f"{APP_PATH}/badtrack/DEBIAN/postinst", 'w') as file:
    file.write(postinst_content)

# Make the post-installation script executable
os.chmod(f"{APP_PATH}/badtrack/DEBIAN/postinst", 0o755)

# Build the Debian package
subprocess.run(["dpkg-deb", "--build", f"{APP_PATH}/badtrack"],check=True)
print("badtrack.deb package has been created.")
