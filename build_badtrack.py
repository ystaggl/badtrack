#!/usr/bin/env python3

import os
import shutil
import subprocess

# Get the current working directory
APP_PATH = os.path.abspath(os.path.dirname(__file__))

# Fixed path for the history folder
HISTORY_FOLDER = "/var/lib/badtrack/history"

# Fixed path for the cache folder (should it go here?)
CACHE_FOLDER = "/var/lib/badtrack/cache"

# Create the badtrack directory structure
os.makedirs(f"{APP_PATH}/badtrack/DEBIAN", exist_ok=True)
os.makedirs(f"{APP_PATH}/badtrack/usr/local/bin/badtrack", exist_ok=True)
os.makedirs(f"{APP_PATH}/badtrack/etc/systemd/system", exist_ok=True)

# Copy the main.py file to the badtrack directory and make it executable
shutil.copy('main.py', f"{APP_PATH}/badtrack/usr/local/bin/badtrack/main.py")
os.chmod(f"{APP_PATH}/badtrack/usr/local/bin/badtrack/main.py", 0o755)

# Create the control file
control_content = """Package: badtrack
Version: 1.0.0
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
Environment=CACHE_FOLDER={CACHE_FOLDER} #Is this correct? it makes the code run but seems definitely wrong

[Install]
WantedBy=multi-user.target"""
with open(f"{APP_PATH}/badtrack/etc/systemd/system/badtrack.service", 'w') as file:
    file.write(service_content)

# Changing the permissions of the badtrack.service file
os.chmod(f"{APP_PATH}/badtrack/etc/systemd/system/badtrack.service", 0o644)


def add_environment_variable(path):
    # Create the folder if it doesn't exist
    os.makedirs(path, exist_ok=True)
    # Change permissions of the folder
    subprocess.run(["chmod", "--recursive", "755", path]) #I don't like mixing subprocess.run with os.chmod, but this is the easiest way to make it recursive
    return

add_environment_variable(HISTORY_FOLDER)
add_environment_variable(CACHE_FOLDER)

# Create the post-installation script
postinst_content = f"""#!/bin/bash
getent passwd badtrackuser > /dev/null || sudo useradd -r -s /bin/false badtrackuser
# Set ownership of folders to badtrackuser
chown -R badtrackuser:badtrackuser \"{HISTORY_FOLDER}\"
chown -R badtrackuser:badtrackuser \"{CACHE_FOLDER}\"
systemctl daemon-reload
systemctl enable badtrack
systemctl start badtrack
"""

with open(f"{APP_PATH}/badtrack/DEBIAN/postinst", 'w') as file:
    file.write(postinst_content)


# Make the post-installation script executable
os.chmod(f"{APP_PATH}/badtrack/DEBIAN/postinst", 0o755)

# Build the Debian package
subprocess.run(["dpkg-deb", "--build", f"{APP_PATH}/badtrack"])

print("badtrack.deb package has been created.")
