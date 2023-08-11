#!/bin/bash

# Get the current working directory
APP_PATH="$(pwd)"

# Fixed path for the history folder
HISTORY_FOLDER="/var/lib/badtrack/history"

# Create the badtrack directory structure
mkdir -p "$APP_PATH/badtrack/DEBIAN"
mkdir -p "$APP_PATH/badtrack/usr/local/bin/badtrack"
mkdir -p "$APP_PATH/badtrack/etc/systemd/system"

# Copy the main.py file to the badtrack directory and make it executable
cp main.py "$APP_PATH/badtrack/usr/local/bin/badtrack/main.py"
chmod +x "$APP_PATH/badtrack/usr/local/bin/badtrack/main.py"

# Create the control file
echo "Package: badtrack
Version: 1.0.0
Section: custom
Priority: optional
Architecture: all
Essential: no
Installed-Size: 1024
Maintainer: Your Name <your-email@example.com>
Description: Badtrack is a sample package" > "$APP_PATH/badtrack/DEBIAN/control"

# Create the systemd service file within the package
echo "[Unit]
Description=BadTrack Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/usr/local/bin/badtrack
ExecStart=/usr/bin/python3 /usr/local/bin/badtrack/main.py
Environment=HISTORY_FOLDER=$HISTORY_FOLDER

[Install]
WantedBy=multi-user.target" > "$APP_PATH/badtrack/etc/systemd/system/badtrack.service"

# Create the post-installation script
echo "#!/bin/bash
mkdir -p \"$HISTORY_FOLDER\"
chmod 644 /etc/systemd/system/badtrack.service
systemctl daemon-reload
systemctl enable badtrack
systemctl start badtrack" > "$APP_PATH/badtrack/DEBIAN/postinst"

# Make the post-installation script executable
chmod +x "$APP_PATH/badtrack/DEBIAN/postinst"

# Build the Debian package
dpkg-deb --build "$APP_PATH/badtrack"

echo "badtrack.deb package has been created."

