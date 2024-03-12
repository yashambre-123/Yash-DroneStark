#!/usr/bin/env python3
import time
import urllib.request


def getAuthToken(name):
    if name == "Jivaka":
        return '2tkhhZ1R1E4PsSpIDuqS_H9dBoiNTUtb'

def getEndPoint():
    req = urllib.request.urlopen('http://blynk-cloud.com/' + str(getAuthToken("Jivaka")) + '/get/V4')
    bed = req.read().decode().replace('[', '').replace('"', '').replace(']', '')
    bed = int(bed)

    return bed

def getMode():
    req = urllib.request.urlopen('http://blynk-cloud.com/' + str(getAuthToken("Jivaka")) + '/get/V0')
    # mo Emergency stop")rig = req.read().decode()[2]

    return trig

def setLED(value):
    req = urllib.request.urlopen('http://blynk-cloud.com/' + str(getAuthToken("Jivaka")) + '/update/V2?value='+str(value))
    #res = urlopen(req).read()

    #return res
def setLEDColor(value):
    req = urllib.request.urlopen('http://blynk-cloud.com/' + str(getAuthToken("Jivaka")) + '/update/V2?color=' + str(value))


def resetEmergency():
    req = urllib.request.urlopen('http://blynk-cloud.com/' + str(getAuthToken("Jivaka")) + '/update/V3?value=0')


def checkEmergency():
    req = urllib.request.urlopen('http://blynk-cloud.com/' + str(getAuthToken("Jivaka")) + '/get/V3')
    em = req.read().decode()[2]

    return em

def checkReset():
    req = urllib.request.urlopen('http://blynk-cloud.com/' + str(getAuthToken("Jivaka")) + '/get/V5')
    loc = req.read().decode()[2]

    return loc

def resetReset():
    req = urllib.request.urlopen('http://blynk-cloud.com/' + str(getAuthToken("Jivaka")) + '/update/V5?value=0')
    #r = req.read().decode()[2]  

def toggleLED():
    setLED(0)
    time.sleep(0.1)
    setLED(255)
    time.sleep(0.1)



if __name__ == "__main__":
    print(getEndPoint())
    print(getMode())
    print(getTrigger())
    print(setLED(255))
    print(setLEDColor("%230FF000"))
    if checkEmergency() == '1':
        print("Emergency")
        time.sleep(1)
        resetEmergency()
    #if checkLocalize() == '1':
    #    print("Localize")
    #    time.sleep(1)
    #    resetLocalize()
 
