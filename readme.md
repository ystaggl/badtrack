
# Quick setup

Build badtracksecrets:

`EMAIL_USER=\<username> EMAIL_PASSWORD=\<password> ./build_secrets.py

Then, Build badtrack:

`./build_badtrack.py`

Then, install badtrack and badtracksecrets:

`dpkg -i badtrack.deb badtracksecrets.deb`

Check that everything is working:

`systemctl status badtrack`