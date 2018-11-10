#!/usr/bin/python
"""Code for backing up pictures and videos captured to Dropbox"""
import sys
import os

def main(args):
    """Main function"""
    if args:
        folder_path = args[0]
    else:
        folder_path = '/var/lib/motion'
    if not os.path.exists(folder_path):
        print "Folder Path: " + folder_path + " doesn't exist, exiting."
        raise ValueError("Incorrect Parameters")

    print "Grabbing files from " + folder_path

if __name__ == "__main__":
    main(sys.argv[1:])
