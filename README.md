# RPi-ALPR

Motionpic.py takes pictures when motion is detected. Scan.pi processes these, reports to the server, and uploads photos if the plate is unknown. Checkview.sh is intended for remote debugging, and forces a picture to be taken and uploaded. The system must be rebooted after usage, as the camera daemon is disabled.


Dependancies (will take roughly 6 hours to install the first three):

openCV 3.2.0

tesseract 3.03-rc1

leptonica 1.7.0

Dropbox-Uploader

Dataplicity for remote access (for now)

