#!/usr/bin/env python3

import os
import subprocess
import shutil
import inspect

# Get the current working directory
APP_PATH = os.path.abspath(os.path.dirname(__file__))

PACKAGE_NAME = "badtracksecrets"


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


def clean_login(login):
    """
    Allows login to be specified both with surrounding quotes and without.
    """
    if login[0] != login[-1]:
        return login
    return login.strip("\'\"")


if __name__ == '__main__':
    # Setup text files

    # Create the control file
    control_contents = format_control_file(version="1")

    # Create secrets.env
    email_user = clean_login(os.environ["EMAIL_USER"])
    email_password = clean_login(os.environ["EMAIL_PASSWORD"])
    secret_contents = inspect.cleandoc(f"""\
    EMAIL_USER = \'{email_user}\'
    EMAIL_PASSWORD = \'{email_password}\'
    """)

    # Set owner of secrets.env to badtrackuser
    postinst_contents = inspect.cleandoc(f"""\
    #!/bin/bash
    getent passwd badtrackuser > /dev/null || sudo useradd -r -s /bin/false badtrackuser
    chown -R badtrackuser:badtrackuser \"/var/lib/badtrack/secrets.env\"
    """)


    # Create directory structure
    package_directory("DEBIAN")
    package_directory("/var/lib/badtrack/")

    # Package files
    package_file("/DEBIAN/control",contents=control_contents)
    package_file("/DEBIAN/postinst",contents=postinst_contents)
    package_file("/var/lib/badtrack/secrets.env",contents=secret_contents)

    # Set permissions
    os.chmod(f"{APP_PATH}/{PACKAGE_NAME}/DEBIAN/postinst", 0o755)
    os.chmod(f'{APP_PATH}/{PACKAGE_NAME}/var/lib/badtrack/secrets.env',0o600)

    # Build package
    build_package()
