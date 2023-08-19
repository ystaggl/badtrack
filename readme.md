
# Quick setup

First setup environment variables:
1. Rename .env.example to .env
2. Replace the variables with real values
3. If using git, add .env to .gitignore or ./.git/info/exclude 

Example exclude file:
```
#git ls-files --others --exclude-from=.git/info/exclude
# Lines that start with '#' are comments.
# For a project mostly in C, the following would be a good set of
# exclude patterns (uncomment them if you want to use them):
# *.[oa]
# *~
.env
```

Next, configure the username/password in badtrack_secrets.py (Hint: Ctrl+F search 'export')

Next, build badtracksecrets:

`python3 ./badtrack_secrets.py`

Then, install it:

`sudo dpkg -i badtracksecrets.deb`

Then build badtrack:

`./build_badtrack.py`

Finally, install badtrack:

`sudo dpkg -i badtrack.deb`

Check that everything is working:

`sudo systemctl status badtrack`