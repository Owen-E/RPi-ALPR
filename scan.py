# This file is intended for use in Python 3.4

import glob, os, time, shutil
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from apscheduler.schedulers.blocking import BlockingScheduler
import subprocess
from subprocess import call
sched = BlockingScheduler()
from datetime import datetime

# URL to submit license plate reports to
regoURL = "https://chrysalid-bee-4342.dataplicity.io/processreader.php";

# Runs autonomously, every 15 seconds
@sched.scheduled_job('interval', seconds=15)
def scan():
    print (" ")
    print ("- - - Scanning & deleting old results/images - - -")
    os.chdir("/home/pi/Desktop");
    for file in glob.glob("result*.txt"):
        #save filename for later use (saving the associated capture)
        ID = (os.path.basename(file))
        ID = ID[7:]
        ID = ID.split('.',1)[0]
        print(ID)
        print(file)
        f = open(file,'r')
        contents = f.read()
       # f.close()
        if(os.stat(file).st_size == 0):
            print ('   > File empty, awaiting ALPR result') #ignore file until ALPR has filled it
        elif('No license' in contents):
            print ('   > Nothing found, removing result') # ALPR reported no plate. delete file.
            os.remove(file)
        elif('plate0' in contents): # ALPR returned list of plates 
            with open(file,'r') as ins:
                array = []
                for line in ins:
                    if('-' in line):
                        x = line[6:]
                        x = x.split('\t',1)[0]
                        array.append(x)
            print (array)
            #if array is not 10 section long, need to pad
            while(len(array) < 10):
                array.append(array[0])

            
            post_fields = {'plate1': array[0],
                           'plate2': array[1],
                           'plate3': array[2],
                           'plate4': array[3],
                           'plate5': array[4],
                           'plate6': array[5],
                           'plate7': array[6],
                           'plate8': array[7],
                           'plate9': array[8],
                           'plate10': array[9]}

            #Transmit report
            request = Request(regoURL,urlencode(post_fields).encode())
            #Retrieve response from server
            json = urlopen(request).read().decode()
            time.sleep(1)
            print(json)
            if('not found' in json):
                print ('found a not detected')
                print ("searching for %s.jpg" % ID)

                #If server reports that the license plate was not found in the database, save the photo
                for IMG in glob.glob("*%s.jpg" % ID):
                    print("Moving %s to /home/pi/Desktop/savedpics/%s" % (os.path.abspath(IMG) , os.path.basename(IMG)))
                    
                    Upload = "/home/pi/Desktop/Dropbox-Uploader-master/dropbox_uploader.sh upload %s %s" % (os.path.abspath(IMG) ,os.path.basename(IMG))
                    subprocess.call(Upload, shell=True)
                    time.sleep(1)
                    
            os.remove(file)
    now = time.time()
    i = 0
    #remove captures older than a minute (manual garbage collection)
    for IMGfile in glob.glob("capture*"):
        if(os.stat(IMGfile).st_mtime < now - 60):
            os.remove(IMGfile)
            i = i + 1
    #remove empty files older than 2 mins (manual garbage collection)
    for TXTfile in glob.glob("result*.txt"):
        if(os.stat(TXTfile).st_mtime < now - 120):
            os.remove(TXTfile)
            i = i + 1
    if(i > 0):
        print ("- Removed %d old files" % i )

sched.start()
