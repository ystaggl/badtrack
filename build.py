from eluthia.decorators import chmod, copy_folder, file, git_clone, empty_folder
from eluthia.defaults import control
from eluthia.functional import pipe
from eluthia.py_configs import deb822


@chmod(0o755)
@file
def postinst(full_path, package_name, apps):
    return f'''\
        #!/bin/bash
        getent passwd badtrackuser > /dev/null || sudo useradd -r -s /bin/false badtrackuser
        chown -R badtrackuser:badtrackuser \"/var/lib/badtrack/\"
        # Reload the systemd daemon to recognize the new service file
        systemctl daemon-reload

        # Enable and start the service
        systemctl enable {package_name}
        systemctl restart {package_name}
    '''

@file
def systemd_service(full_path, package_name, apps):
    environment_variables = '\n'.join(
        f"        Environment={variable}={value}"
        for variable, value in apps[package_name]['env'].items()).strip()

    return f'''\
        [Unit]
        Description=BadTrack Service
        After=network.target
        [Service]
        Type=simple
        User=badtrackuser
        WorkingDirectory=/usr/local/bin/badtrack

        # https://fhackts.wordpress.com/2014/11/27/systemd-journal-not-showing-python-3-print/
        # https://stackoverflow.com/questions/230751/how-can-i-flush-the-output-of-the-print-function
        ExecStart=/usr/bin/python3 -u /usr/local/bin/badtrack/main.py

        {environment_variables}
        [Install]
        WantedBy=multi-user.target
    '''

def get_package_tree(package_name, apps):
    return {
        'DEBIAN': {
            'postinst': postinst,
            'control': file(pipe(
                # @file
                # def custom_control(file_path, package_name, apps):
                #    return deb822({
                #        **control(file_path, package_name, apps),
                #        'Description': 'Badtrack!',
                #    })
                control,
                lambda d: {**d, 'Description': 'Badtrack!'},
                deb822)),
        },
        'etc': {
            'systemd': {
                'system': {
                    f'{package_name}.service': systemd_service,
                },
            },
        },
        'usr': {
            'local': {
                'bin': {
                    'badtrack': git_clone(apps[package_name]['folder']),
                }
            },
        },
        'var': {
            'lib': {
                'badtrack': {
                    'history': empty_folder,
                    'cache': empty_folder,
                }
            }
        }
    }
