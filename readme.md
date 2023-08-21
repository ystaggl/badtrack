
# Quick setup

Build badtracksecrets:

`python3 ./build_secrets.py -u <Email Username> -p <Email Password>`

Then, Build badtrack:

`python3 ./build_badtrack.py`

Then, install badtrack and badtracksecrets:

`sudo dpkg -i badtrack.deb badtracksecrets.deb`

Check that everything is working:

`sudo systemctl status badtrack`