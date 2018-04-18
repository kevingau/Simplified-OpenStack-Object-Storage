import socket
from contextlib import closing
import hashlib
import math
import os
import subprocess
import sys
# import threading
# from sys import argv

def get_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 0))
    addr, port = s.getsockname()
    s.close()
    return port


def get_free_address():
    host = socket.gethostbyname(socket.gethostname())
    return host


def FilenameHash(filename):
    h = hashlib.md5(filename.encode("utf-8")).hexdigest()
    x = bin(int(h, 16))[2:]        # convert hex to binary
    x_16 =  x[112:]        # take last 16 digit as index
    return x_16


def UploadCommand(UserFileName, partition, s, disklist, loginname):
    username = UserFileName.split("/")[0] 
    filename = UserFileName.split("/")[1]        # filename is the filename only
    filesize = s.recv(1024).decode("utf-8")
    l = len(disklist)

    # filetmp is for file which uploaded to server temporarily
    directory = "/tmp/filetmp/"
    if not os.path.exists(directory): os.makedirs(directory)        # create a folder
    
    # receive data from client and write into file
    file = directory + filename
    f = open(str(file), 'wb')
    data = s.recv(1024)
    totalRecv = len(data)
    f.write(data)
    while totalRecv < int(filesize):
        data = s.recv(1024)
        totalRecv += len(data)
        f.write(data)
    f.close()
    print("Upload Complete!")

    # decide which disk to be main disk and backup disk
    UserFileHash = int(FilenameHash(UserFileName), 2)        # convert binary to decimal
    i = 0
    while i < l:
        if (UserFileHash >= 2**(int(partition))*i/l and UserFileHash < 2**(int(partition))*(i+1)/l): 
            uploadmaindisk = disklist[i]
            if (i != (l-1)): uploadbackupdisk = disklist[i+1]
            else: uploadbackupdisk = disklist[0]
            print("main disk: "+uploadmaindisk)
            print("back up disk: "+uploadbackupdisk)
        i += 1            

    # create a script commandfile.sh to run two cammand: CreatFolder and CopyFile
    commandfile = open('commandfile.sh', 'w')
    os.chmod("./commandfile.sh", 0o700)
    CreatFolder = "ssh -o \"StrictHostKeyChecking no\" "+loginname+"@"+uploadmaindisk+" \"mkdir -p /tmp/"+loginname+"/"+username+"\"";
    CopyFile = "scp -B /tmp/filetmp/"+filename+" "+loginname+"@"+uploadmaindisk+":/tmp/"+loginname+"/"+username+"/"+filename;
    commandfile.write(CreatFolder+'\n')
    commandfile.write(CopyFile+'\n')
    commandfile.close()
    os.system('sh commandfile.sh')
    os.remove('commandfile.sh')

    # do the same thing for backup
    commandfile = open('commandfile.sh', 'w')
    os.chmod("./commandfile.sh", 0o700)
    CreatFolder = "ssh -o \"StrictHostKeyChecking no\" "+loginname+"@"+uploadbackupdisk+" \"mkdir -p /tmp/"+loginname+"/"+username+"\"";
    CopyFile = "scp -B /tmp/filetmp/"+filename+" "+loginname+"@"+uploadbackupdisk+":/tmp/"+loginname+"/"+username+"/"+filename;
    commandfile.write(CreatFolder+'\n')
    commandfile.write(CopyFile+'\n')
    commandfile.close()
    os.system('sh commandfile.sh')
    os.remove('commandfile.sh')
    
    # remove temporary file and folder in server
    os.remove('/tmp/filetmp/'+filename)
    os.rmdir('/tmp/filetmp')
    # sys.exit()



def DownloadCommand(UserFileName, partition, s):
    filename = UserFileName.split("/")[1]        # filename is the filename only
    if os.path.isfile(filename):
        filesize = str(os.path.getsize(filename))
        s.send(("EXISTS " + filesize).encode("utf-8"))
        with open(filename, 'rb') as f:
            bytesToSend = f.read(1024)
            s.send(bytesToSend)
            while bytesToSend != "":
                bytesToSend = f.read(1024)
                s.send(bytesToSend)
    else:
        s.send("ERR ")

    s.close()


def Main():
    # script, partition, ip0, ip1, ip2, ip3 = argv
    script = sys.argv[0]
    partition = sys.argv[1]
    disklist = sys.argv[2:]

    loginname = os.getlogin()
    host = get_free_address()
    port = get_free_port()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Socket successfully created")
    
    s.bind((host, port))
    s.listen(5)
    print("Listening on %s %d" % (host, port))

    while True:
        conn, addr = s.accept()
        print('Got connection from', addr)


    # while True:
        data = conn.recv(1024).decode("utf-8")
        command = data.split( )
        if (command[0] == "upload"): UploadCommand(command[1], partition, conn, disklist, loginname)
            # t = threading.Thread(target = UploadCommand, args = (command[1], partition, conn))
            # t.start()
        if (command[0] == "download"): DownloadCommand(command[1], partition, conn)
        # if (command[0] == "list"): ListCommand(command[1])
        # if (command[0] == "delete"): DeleteCommand(command[1])

        # conn.send("server received you message.".encode("utf-8"))    
    s.close()


if __name__ == '__main__':
    Main()










# https://pypi.python.org/pypi/uhashring/0.4
# https://gist.github.com/kevinkindom/108ffd675cb9253f8f71
