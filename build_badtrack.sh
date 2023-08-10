#!/bin/bash

# Check if APP_PATH environment variable is set; if not, default to /home/username/Desktop/robinBadTrack/
if [ -z "$APP_PATH" ]; then
  APP_PATH="/home/$(whoami)/Desktop/robinBadTrack"
fi

# Create the directory if it doesn't exist
mkdir -p "$APP_PATH"

# Create the badtrack directory structure
mkdir -p "$APP_PATH/badtrack/DEBIAN"
mkdir -p "$APP_PATH/badtrack/usr/local/bin"
mkdir -p "$APP_PATH/badtrack/usr/local/share/badtrack"
mkdir -p "$APP_PATH/badtrack/usr/local/bin/badtrack"

# Make the pre-installation script executable
chmod +x "\$APP_PATH/badtrack/DEBIAN/preinst"

# Copy the main.py file to the badtrack directory and make it executable
cp main.py "$APP_PATH/badtrack/usr/local/bin/badtrack"
cp main.py "$APP_PATH/main.py"
cp main.py "$APP_PATH/badtrack/usr/local/bin/badtrack/main.py"
chmod +x "$APP_PATH/badtrack/usr/local/bin/badtrack/main.py"
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
echo "#!/bin/bash

# Create the directory with proper permissions
mkdir -p "/var/lib/badtrack/history"
chown -R $(whoami):$(whoami) "/var/lib/badtrack/history"
chmod 755 "/var/lib/badtrack/history"

# Create the systemd service file
cat <<EOL | sudo tee /etc/systemd/system/badtrack.service
[Unit]
Description=BadTrack Service
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=/usr/local/bin/badtrack
ExecStart=/usr/bin/python3 /usr/local/bin/badtrack/main.py

[Install]
WantedBy=multi-user.target
EOL

# Set the correct permissions for the service file
sudo chmod 644 /etc/systemd/system/badtrack.service

# Reload the systemd daemon to recognize the new service file
sudo systemctl daemon-reload

# Enable and start the service
sudo systemctl enable badtrack
sudo systemctl start badtrack" > "$APP_PATH/badtrack/DEBIAN/postinst"

# Make the post-installation script executable
chmod +x "$APP_PATH/badtrack/DEBIAN/postinst"

# Build the Debian package
dpkg-deb --build "$APP_PATH/badtrack"

# Print the status
sudo systemctl status badtrack

echo "badtrack.deb package has been created."

