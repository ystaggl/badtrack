#!/bin/bash

sudo systemctl stop badtrack ; 
sudo systemctl daemon-reload ; 
sudo rm -r /var/lib/badtrack/ ; 
sudo rm /etc/systemd/system/badtrack.service ; 
sudo rm -r /home/a/Desktop/badtrack/badtrack ; 
sudo rm /home/a/Desktop/badtrack/badtrack.deb ;
sudo userdel -r badtrackuser

