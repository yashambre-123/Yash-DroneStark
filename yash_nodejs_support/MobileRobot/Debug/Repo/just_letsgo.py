from csv import reader

with open('/home/dronestark/Yash-DroneStark/yash_nodejs_support/MobileRobot/Debug/Repo/NodeTable.csv', 'r') as read_obj:
    csv_reader = reader(read_obj)
    header = next(csv_reader)
    data = list(csv_reader)


print(data)
for row in data:
    print(row)
# def my_func(data):
#     for row in data:
#         print(row)
        
# my_func(data)
                        
    # for row in csv_reader:
    #     row[0] = int(row[0])
    #     row[1] = int(row[1])
    #     row[2] = int(row[2])
    #     row[3] = int(row[3])
    #     row[4] = int(row[4])