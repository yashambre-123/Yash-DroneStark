
import cv2
import numpy as np
import sys
import time
from collections import deque
from csv import reader



def read_from_csv():
    #data = str(data)
    #print(data)
    # skip first line i.e. read header first and then iterate over each row od csv as a list
    decodedData = ''
    nodeType = ''
    with open('/home/dronestark/Yash-DroneStark/yash_nodejs_support/MobileRobot/Debug/Repo/NodeTable.csv', 'r') as read_obj:
        csv_reader = reader(read_obj)
        header = next(csv_reader)
        # Check file as empty
        if header != None:
            #print("Header present")
            # Iterate over each row after the header in the csv
            for row in csv_reader:
                # row variable is a list that represents a row in csv
                print(row[0])
            #print(decodedData)

read_from_csv()