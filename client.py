import socket
import hashlib
from sys import argv
import os
import sys


def UploadCommand(UserFileName, s):
    filename = UserFileName.split("/")[1]        # filename is the filename only
    if os.path.isfile(filename):
        print("The given file exists.")
        filesize = str(os.path.getsize(filename))
        s.send(filesize.encode("utf-8"))
        with open(filename, 'rb') as f:
            bytesToSend = f.read(1024)
            s.send(bytesToSend)
            try:
                bytesToSend = f.read(1024)
                s.send(bytesToSend)
            except: pass
    else: 
        print("Error: The given file does not exist!")
    
    # receive and display the result from server
    data = s.recv(1024)
    print(data.decode("utf-8"))
    
    return 0


def DownloadCommand(UserFileName, s):
    data = s.recv(1024)
    if data.decode("utf-8") == "The file is not exist.":
        print(data.decode("utf-8"))
        return 0
    else:
        print(data.decode("utf-8"))        

    filename = UserFileName.split("/")[1]        # filename is the filename only
    if filename != 'q':
        filesize = s.recv(1024).decode("utf-8")
        f = open(filename, 'wb')
        data = s.recv(1024)
        totalRecv = len(data)
        f.write(data)
        while totalRecv < int(filesize):
            data = s.recv(1024)
            totalRecv += len(data)
            f.write(data)
        print("Download Complete!")
        f.close()

    # display the result
    f = open(filename, 'r')
    file_contents = f.read()
    print ("The content is as below:")    
    print (file_contents)
    f.close()

    return 0


def ListCommand(UserFileName, s):
    username = UserFileName.split("/")[0]
    filesize = s.recv(1024).decode("utf-8")
    f = open('output.txt', 'wb')
    data = s.recv(1024)
    totalRecv = len(data)
    f.write(data)
    while totalRecv < int(filesize):
        data = s.recv(1024)
        totalRecv += len(data)
        f.write(data)
    print("Listing Complete!")
    f.close()
    
    filepath = 'output.txt'  
    with open(filepath) as f:  
        line = f.readline()
        while line:
            print(line.strip())
            line = f.readline()
    os.remove(filepath)



def DeleteCommand(UserFileName, s):
    data = s.recv(1024)
    if data.decode("utf-8") == "The file is not exist.":
        print(data.decode("utf-8"))
        return 0
    else:
        print(data.decode("utf-8")) 
            
    # receive and display the result from server
    data = s.recv(1024)
    print(data.decode("utf-8"))
    return 0


def AddCommand(UserFileName, s):
    # receive and display the result from server
    data = s.recv(1024)
    print(data.decode("utf-8"))

    return 0


def RemoveCommand(UserFileName, s):
    # receive and display the result from server
    data = s.recv(1024)
    print(data.decode("utf-8"))

    return 0


def Main():
    script, ip, port = argv
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
 
    try: 
        while True:
            s.connect((ip, int(port)))
            cmd = input("What do you want?")
            s.send(cmd.encode("utf-8"))
            command = cmd.split()

            if (command[0] == "upload"): UploadCommand(command[1], s)
            if (command[0] == "download"): DownloadCommand(command[1], s)
            if (command[0] == "list"): ListCommand(command[1], s)        
            if (command[0] == "delete"): DeleteCommand(command[1], s)
            if (command[0] == "add"): AddCommand(command[1], s)        
            if (command[0] == "remove"): RemoveCommand(command[1], s)                    

            # data = s.recv(1024)
            # print(data.decode("utf-8"))
    except: pass
    s.close()


if __name__ == '__main__':
    Main()

