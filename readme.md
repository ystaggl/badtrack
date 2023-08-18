
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

Then execute the build script:

`./build_badtrack.py`

Finally install the package:

`sudo dpkg -i badtrack.deb`

Check that everything is working:

`sudo systemctl status badtrack`