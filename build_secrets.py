#!/usr/bin/env python3

import os
import subprocess
import shutil
from argparse import ArgumentParser, SUPPRESS
import inspect


# Get the current working directory
APP_PATH = os.path.abspath(os.path.dirname(__file__))
PACKAGE_NAME = "badtracksecrets"


def custom_argparser():
    """
    Returns a custom argument parser which allows for named arguments to be required
    """
    # Get username and password
    parser = ArgumentParser(add_help=False) # Disable default help
    parser.required = parser.add_argument_group('required arguments')
    parser.optional = parser.add_argument_group('optional arguments')
    parser.optional.add_argument( # Add back help
        '-h',
        '--help',
        action='help',
        default=SUPPRESS,
        help='show this help message and exit'
    )
    return parser


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
    if contents == None:
        shutil.copy(existing_file, f"{APP_PATH}/{PACKAGE_NAME}/{path}")
        return

    with open(f'{APP_PATH}/{PACKAGE_NAME}/{path}','w+') as file:
        file.write(contents)
    return


def create_control_file(
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
        Creates the control file
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
        with open(f"{APP_PATH}/{PACKAGE_NAME}/DEBIAN/control", 'w') as file:
            file.write(control_content)
        return


def build_package():
    """
    Builds the debian package
    """
    subprocess.run(["dpkg-deb", "--build", f"{APP_PATH}/{PACKAGE_NAME}"],check=True)
    print(f"{PACKAGE_NAME}.deb package has been created.")
    return


class PostInst():
    """
    Object to control postinst script
    """
    def __init__(self):
        self.contents = "#!/bin/bash"
        return

    def add_commands(self,commands):
        for command in commands:
            self.contents += "\n"
            self.contents += command
        return

    def write_postinst(self):
        with open(f"{APP_PATH}/{PACKAGE_NAME}/DEBIAN/postinst", 'w') as file:
            file.write(self.contents)
        os.chmod(f"{APP_PATH}/{PACKAGE_NAME}/DEBIAN/postinst", 0o755)
        return


if __name__ == '__main__':
    # Create the badtracksecrets directory structure
    package_directory("DEBIAN")
    package_directory("/var/lib/badtrack/")

    # Create the control file
    create_control_file(version="1")

    # Add argument parser
    parser = custom_argparser()
    parser.required.add_argument('-u',"--USER", help="Email server username", required=True)
    parser.required.add_argument('-p',"--PASSWORD", help="Email server password", required=True)
    args=parser.parse_args()

    # Create secrets.env
    secret_contents = inspect.cleandoc(f"""\
    EMAIL_USER = {args.USER}
    EMAIL_PASSWORD = {args.PASSWORD}
    """)
    package_file("/var/lib/badtrack/secrets.env",contents=secret_contents)

    # Set permissions for secrets.env
    os.chmod(f'{APP_PATH}/{PACKAGE_NAME}/var/lib/badtrack/secrets.env',0o600)

    # Set owner of secrets.env to badtrackuser
    postinst = PostInst()
    postinst_commands = ["getent passwd badtrackuser > /dev/null || sudo useradd -r -s /bin/false badtrackuser",
                         f"chown -R badtrackuser:badtrackuser \"/var/lib/badtrack/secrets.env\""]
    postinst.add_commands(postinst_commands)

    # Write postinst
    postinst.write_postinst()

    # Build package
    build_package()
