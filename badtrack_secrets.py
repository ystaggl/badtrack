#!/usr/bin/env python3
import os
if __name__ == '__main__':
    with open(f'/var/lib/badtrack/secrets.env','w+') as secretsfile:
        secretsfile.write(f"EMAIL_USER = {os.environ['badtracksecrets_user']}")
        secretsfile.write("\n")
        secretsfile.write(f"EMAIL_PASSWORD = {os.environ['badtracksecrets_pass']}")
    os.chmod(f'/var/lib/badtrack/secrets.env',0o600)