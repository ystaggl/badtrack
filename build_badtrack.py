#!/usr/bin/env python3

import os
import shutil
import subprocess
import inspect

# Get the current working directory
APP_PATH = os.path.abspath(os.path.dirname(__file__))
PACKAGE_NAME = "badtrack"

# Fixed path for the environment variable folders
HISTORY_FOLDER = "/var/lib/badtrack/history"
CACHE_FOLDER = "/var/lib/badtrack/cache"


def package_directory(path):
    """
    Adds directory to the package filestructure.
    Arguments:
        Path - the path of the directory.
    Example Usage:
        package_directory(/var/lib/example/) - When the package is installed, the directory /var/lib/example/ will be added to the filesystem.
    """
    if path[0] == '/':
        path = path[1:]
    os.makedirs(f"{APP_PATH}/{PACKAGE_NAME}/{path}", exist_ok=True)
    return


def package_file(path,contents=None,existing_file=None):
    """
    Add a file to the package.
    Arguments:
        Path - the path of the installed file
        contents - If a new file is being written, this should be set to the contents of the file
        existing_file - If instead an existing file is being added to the package, this should be the path to that file.
    """
    if path[0] == "/":
         path = path[1:]

    if contents == None:
        shutil.copy(existing_file, f"{APP_PATH}/{PACKAGE_NAME}/{path}")
        return

    with open(f'{APP_PATH}/{PACKAGE_NAME}/{path}','w+') as file:
        file.write(contents)
    return


def format_control_file(
    package=PACKAGE_NAME,
    version='1.0.0',
    depends='',
    section='custom',
    priority='optional',
    architecture='all',
    essential='no',
    installed_size='1024',
    maintainer='Your Name <your-email@example.com>',
    description=f'{PACKAGE_NAME} is a sample package'):
        """
        Formats the control file
        """

        control_content = inspect.cleandoc(f"""\
        Package: {package}
        Version: {version}
        Depends: {depends}
        Section: {section}
        Priority: {priority}
        Architecture: {architecture}
        Essential: {essential}
        Installed-Size: {installed_size}
        Maintainer: {maintainer}
        Description: {description}
        """)
        control_content += "\n"
        return control_content


def build_package():
    """
    Builds the debian package
    """
    subprocess.run(["dpkg-deb", "--build", f"{APP_PATH}/{PACKAGE_NAME}"],check=True)
    print(f"{PACKAGE_NAME}.deb package has been created.")
    return


if __name__ == '__main__':
    # Setup text files

    # Setup environment file
    envfile_text = inspect.cleandoc(f"""\
    EMAIL_HOST = 'relay.mailbaby.net'
    EMAIL_PORT = '465'
    EMAIL_FROM = 'sender@obsi.com.au'
    EMAIL_TO = 'yannstaggl@gmail.com'
    """)

    # Setup service file
    service_content = inspect.cleandoc(f"""\
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
    EnvironmentFile=/var/lib/badtrack/.env
    EnvironmentFile=/var/lib/badtrack/secrets.env

    [Install]
    WantedBy=multi-user.target
    """)

    # Setup postinst
    postinst_content = inspect.cleandoc(f"""\
    #!/bin/bash
    getent passwd badtrackuser > /dev/null || sudo useradd -r -s /bin/false badtrackuser
    # Set ownership of folders to badtrackuser
    chown -R badtrackuser:badtrackuser \"{HISTORY_FOLDER}\"
    chown -R badtrackuser:badtrackuser \"{CACHE_FOLDER}\"
    chown badtrackuser:badtrackuser \"{APP_PATH}/badtrack/var/lib/badtrack/.env\"
    systemctl enable badtrack
    systemctl daemon-reload
    systemctl restart badtrack
    """)

    # Setup control file
    control_content = format_control_file(depends="badtracksecrets")

    # Create the badtrack directory structure
    package_directory("DEBIAN")
    package_directory(CACHE_FOLDER)
    package_directory(HISTORY_FOLDER)
    package_directory("/etc/systemd/system/")
    package_directory("/usr/local/bin/badtrack")

    # Add files to package
    package_file("/DEBIAN/control",contents=control_content)
    package_file("/DEBIAN/postinst",contents=postinst_content)
    package_file("/var/lib/badtrack/.env",contents=envfile_text)
    package_file("/etc/systemd/system/badtrack.service",contents=service_content)
    package_file("/usr/local/bin/badtrack/main.py",existing_file="main.py")

    # Set permissions for badtrack files
    os.chmod(f"{APP_PATH}/{PACKAGE_NAME}/DEBIAN/postinst", 0o755)
    os.chmod(f"{APP_PATH}/{PACKAGE_NAME}/var/lib/badtrack/.env", 0o755)
    os.chmod(f"{APP_PATH}/{PACKAGE_NAME}/var/lib/badtrack/cache",0o755)
    os.chmod(f"{APP_PATH}/{PACKAGE_NAME}/var/lib/badtrack/history",0o755)
    os.chmod(f"{APP_PATH}/{PACKAGE_NAME}/etc/systemd/system/badtrack.service", 0o644)
    os.chmod(f"{APP_PATH}/{PACKAGE_NAME}/usr/local/bin/badtrack/main.py", 0o755)

    # Build the debian package
    build_package()
