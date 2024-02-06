import csv

a = []
with open("control.csv", mode='r') as file:
    csv_file = csv.reader(file)
    for lines in csv_file:
        a.append(lines)
        print(lines)
    
    print(a)
    
    control = int(input("Enter file number to be executed: "))