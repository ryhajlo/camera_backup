#!/usr/bin/python
"""Code for backing up pictures and videos captured to Dropbox"""
import sys
import os
import glob
from os import listdir
from os.path import isfile, join
import subprocess
from Adafruit_IO import Client
import base64

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

    # Get the list of files in that directory
    pictures = glob.glob(join(folder_path, '2*.jpg')) # Use the leading 2 to prevent us from getting 'latest.jpg'
    videos = glob.glob(join(folder_path, '*.avi'))
    latest_picture = max(pictures, key=os.path.getctime)
    print "The latest picture is: " + latest_picture

    # Upload the files to dropbox
    # Build our command to upload files
    command = []
    command.append('/home/pi/Dropbox-Uploader/dropbox_uploader.sh')
    command.append('upload')
    for picture in pictures:
        print "Will upload: " + picture
        command.append(picture)
    command.append('/camera/pictures/')
    subprocess.call(command)
    print "Finished uploading pictures"

    # Do the same for videos
    command = []
    command.append('/home/pi/Dropbox-Uploader/dropbox_uploader.sh')
    command.append('upload')
    for video in videos:
        print "Will upload: " + video
        command.append(video)
    command.append('/camera/videos/')
    subprocess.call(command)
    print "Finished uploading videos"

    # Upload the latest picture to Adafruit IO
    aio = Client('ryhajlo', 'b5fe0936d9a84629a2d49cd45858fc67')
    with open(latest_picture, "rb") as imageFile:
        str = base64.b64encode(imageFile.read())
  
    print "Uploading latest to Adafruit IO"
    aio.send('pic', str )
    print "Finished uploading to Adafruit IO"

    # Now that everything is uploaded, delete it all
    for picture in pictures:
        print "Deleting " + picture
        os.remove(picture)
    for video in videos:
        print "Deleting " + video
        os.remove(video)

if __name__ == "__main__":
    main(sys.argv[1:])
