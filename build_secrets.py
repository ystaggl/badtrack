#!/usr/bin/env python3

import os
import shutil
import subprocess

# Get the current working directory
APP_PATH = os.path.abspath(os.path.dirname(__file__))

# Create the badtracksecrets directory structure
os.makedirs(f"{APP_PATH}/badtracksecrets/DEBIAN", exist_ok=True)
os.makedirs(f"{APP_PATH}/badtracksecrets/usr/local/bin/badtracksecrets", exist_ok=True)
os.makedirs(f"{APP_PATH}/badtracksecrets/var/lib/badtrack", exist_ok=True)

# Copy the badtrack_secrets.py file to the badtracksecrets directory and make it executable
shutil.copy('badtrack_secrets.py', f"{APP_PATH}/badtracksecrets/usr/local/bin/badtracksecrets/badtrack_secrets.py")
os.chmod(f"{APP_PATH}/badtracksecrets/usr/local/bin/badtracksecrets/badtrack_secrets.py", 0o755)

# Create the control file.
control_content = """\
Package: badtracksecrets
Version: 1.0.0
Depends: python3
Section: custom
Priority: optional
Architecture: all
Essential: no
Installed-Size: 1024
Maintainer: Your Name <your-email@example.com>
Description: badtracksecrets is a sample package
"""
with open(f"{APP_PATH}/badtracksecrets/DEBIAN/control", 'w') as file:
    file.write(control_content)

# Create the post-installation script
postinst_content = f"""\
#!/bin/bash
getent passwd badtrackuser > /dev/null || sudo useradd -r -s /bin/false badtrackuser
export badtracksecrets_user='mb36340'
export badtracksecrets_pass=''
python3 /usr/local/bin/badtracksecrets/badtrack_secrets.py
"""

with open(f"{APP_PATH}/badtracksecrets/DEBIAN/postinst", 'w') as file:
    file.write(postinst_content)

# Make the post-installation script executable
os.chmod(f"{APP_PATH}/badtracksecrets/DEBIAN/postinst", 0o755)

# Build the Debian package
subprocess.run(["dpkg-deb", "--build", f"{APP_PATH}/badtracksecrets"],check=True)
print("badtracksecrets.deb package has been created.")
