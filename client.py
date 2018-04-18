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
            while bytesToSend != "":
                bytesToSend = f.read(1024)
                s.send(bytesToSend)

    else: 
        print("Error: The given file does not exist!")

    s.close()
    # sys.exit()



def DownloadCommand(UserFileName, s):
    filename = UserFileName.split("/")[1]        # filename is the filename only
    if filename != 'q':
        data = s.recv(1024).decode("utf-8")
        if data[:6] == 'EXISTS':
            filesize = data[6:]
            f = open('new_'+filename, 'wb')
            data = s.recv(1024)
            totalRecv = len(data)
            f.write(data)
            while totalRecv < int(filesize):
                data = s.recv(1024)
                totalRecv += len(data)
                f.write(data)
            print("Download Complete!")
            f.close()
        else:
            print("File Does Not Exist!")

    s.close()


def Main():
    script, ip, port = argv
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
 
    s.connect((ip, int(port)))

    while True:
        cmd = input("What do you want?")
        s.send(cmd.encode("utf-8"))
        command = cmd.split()
        if (command[0] == "upload"): UploadCommand(command[1], s)
        if (command[0] == "download"): DownloadCommand(command[1], s)        
        # data = s.recv(1024)
        # print(data.decode("utf-8"))



if __name__ == '__main__':
    Main()

