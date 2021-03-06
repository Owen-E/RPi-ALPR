#!/usr/bin/python
import StringIO
import subprocess
import os
import time
from datetime import datetime
from PIL import Image
from subprocess import call
from subprocess import Popen

# Motion detection settings:
# Threshold (how much a pixel has to change by to be marked as "changed")
# Sensitivity (how many changed pixels before capturing an image)
# ForceCapture (whether to force an image to be captured every forceCaptureTime seconds)
threshold = 20
sensitivity = 100
forceCapture = True
forceCaptureTime = 60 * 60 # Once an hour

# File settings
saveWidth = 1280
saveHeight = 960
diskSpaceToReserve = 40 * 1024 * 1024 # Keep 40 mb free on disk
#This file contains code from an author I have not yet attributed, this will be declared in the next update

filename = ""
min_temp = 0
sec_temp = 0

# Capture a small test image (for motion detection)
def captureTestImage():
    command = "raspistill -bm -md 4 -ex sports -p '1100,450,800,600' -hf -vf -op 250 -w %s -h %s -t 1 -e bmp -o -" % (100, 75)
    #command = "raspistill -ex sports --nopreview -hf -vf -op 250 -w %s -h %s -t 1 -e bmp -o -" % (100, 75)
    imageData = StringIO.StringIO()
    imageData.write(subprocess.check_output(command, shell=True))
    imageData.seek(0)
    im = Image.open(imageData)
    buffer = im.load()
    imageData.close()
    return im, buffer

# Save a full size image to disk
def saveImage(width, height, diskSpaceToReserve):
    keepDiskSpaceFree(diskSpaceToReserve)
    time = datetime.now()
    global min_temp
    global sec_temp
    min_temp = time.minute
    sec_temp = time.second
    global filename
    filename = "/home/pi/Desktop/capture-%04d%02d%02d-%02d%02d%02d.jpg" % (time.year, time.month, time.day, time.hour, time.minute, time.second)
    subprocess.call("raspistill -md 1 -bm -ex sports -p '1100,450,800,600' -hf -vf -w 1296 -h 972 -t 1 -e jpg -q 15 -o %s" % filename, shell=True)
    print "Captured %s" % filename

# Keep free space above given level
def keepDiskSpaceFree(bytesToReserve):
    if (getFreeSpace() < bytesToReserve):
        for filename in sorted(os.listdir(".")):
            if filename.startswith("capture") and filename.endswith(".jpg"):
                os.remove(filename)
                print "Deleted %s to avoid filling disk" % filename
                if (getFreeSpace() > bytesToReserve):
                    return

# Get available disk space
def getFreeSpace():
    st = os.statvfs(".")
    du = st.f_bavail * st.f_frsize
    return du
        
# Get first image
image1, buffer1 = captureTestImage()

# Reset last capture time
lastCapture = time.time()

while (True):

    # Get comparison image
    image2, buffer2 = captureTestImage()

    # Count changed pixels
    changedPixels = 0
    for x in xrange(0, 100):
        for y in xrange(0, 75):
            # Just check green channel as it's the highest quality channel
            pixdiff = abs(buffer1[x,y][1] - buffer2[x,y][1])
            if pixdiff > threshold:
                changedPixels += 1

    # Check force capture
    if forceCapture:
        if time.time() - lastCapture > forceCaptureTime:
            changedPixels = sensitivity + 1
                
    # Save an image if pixels changed
    if changedPixels > sensitivity:
        lastCapture = time.time()
        saveImage(saveWidth, saveHeight, diskSpaceToReserve)

        #create new results file with timestamp matching the feeder image
        #time2 = datetime.now()
        #textfilename = "/home/pi/Desktop/result-%02d%02d.txt" % (time2.minute, time2.second)
        textfilename = "/home/pi/Desktop/result-%02d%02d.txt" % (min_temp, sec_temp)
        
        with open(textfilename, 'a') as output:
            process = subprocess.Popen("/usr/local/src/openalpr/openalpr/src/alpr %s" % filename ,shell=True,stdout=output)
        #print "filename fed to alpr = %s" % filename
        #out = process.stdout.read(1)
        #print "%s" % out
    
    # Swap comparison buffers
    image1 = image2
    buffer1 = buffer2
