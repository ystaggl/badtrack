#!/bin/bash

# Check if APP_PATH environment variable is set; if not, default to /home/username/Desktop/robinBadTrack/
if [ -z "$APP_PATH" ]; then
  APP_PATH="/home/$(whoami)/Desktop/robinBadTrack/"
fi

# Create the directory if it doesn't exist
mkdir -p "$APP_PATH"

# Create the badtrack directory structure
mkdir -p "$APP_PATH/badtrack/DEBIAN"
mkdir -p "$APP_PATH/badtrack/usr/local/bin"
mkdir -p "$APP_PATH/badtrack/usr/local/share/badtrack"

# Create the history directory in the current working directory
mkdir -p history

# Copy the main.py file to the badtrack directory and make it executable
cp main.py "$APP_PATH/badtrack/usr/local/bin/badtrack"
chmod +x "$APP_PATH/badtrack/usr/local/bin/badtrack"

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

# Create the post-installation script
echo "#!/bin/sh
systemctl enable badtrack
systemctl start badtrack" > "$APP_PATH/badtrack/DEBIAN/postinst"
chmod +x "$APP_PATH/badtrack/DEBIAN/postinst"

# Create the systemd service file
cat <<EOL | sudo tee /etc/systemd/system/badtrack.service
[Unit]
Description=BadTrack Service
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$APP_PATH
ExecStart=/usr/bin/python3 $APP_PATH/main.py  # Run main.py directly

[Install]
WantedBy=multi-user.target
EOL

# Change ownership of the badtrack directory to the current user
sudo chown -R $(whoami):$(whoami) "$APP_PATH/badtrack"

# Build the Debian package
dpkg-deb --build "$APP_PATH/badtrack"

# Install the Debian package
sudo dpkg -i "$APP_PATH/badtrack.deb"

# Reload systemd daemon
sudo systemctl daemon-reload

# Print the status
sudo systemctl status badtrack

echo "badtrack.deb package has been created."

