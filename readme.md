
# Quick setup

First setup environment variables:
1. Rename .env.example to .env
2. Replace the variables with real values
3. Place .env in /var/lib/badtrack/

Next, Build badtracksecrets:

`python3 ./build_secrets.py -u <Email Username> -p <Email Password>`

Then, Build badtrack:

`python3 ./build_badtrack.py`

Then, install badtrack and badtracksecrets:

`sudo dpkg -i badtrack.deb badtracksecrets.deb`

Check that everything is working:

`sudo systemctl status badtrack`