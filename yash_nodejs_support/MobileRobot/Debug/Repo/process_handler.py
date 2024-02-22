import os, signal
import intf_blynk as b

my_process = "letsgo"

def getPid(pstring):
    for line in os.popen("ps ax | grep " + pstring + " | grep -v grep"):
        fields = line.split()
        pid = fields[0]
        return int(pid)
        #os.kill(int(pid), signal.SIGKILL)
    return -1

def emergencyStop(pid):
    os.kill(pid, signal.SIGUSR1)

if __name__ == "__main__":
    while True:
        pid = getPid(my_process)
        #print(pid)
        if int(b.checkEmergency()) == 1:
            if(pid != -1):
                print("Sending Emergency stop")
                emergencyStop(pid)
                while int(b.checkEmergency()) == 1:
                    pass

        if int(b.checkReset()) == 1:
            if(pid != -1):
                print("Goodbye!")
        
