import socket
from contextlib import closing
import hashlib
import math
import os
import subprocess
import sys


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


def UploadCommand(UserFileName, partition, s, DiskList, LoginName, d):
    username = UserFileName.split("/")[0] 
    filename = UserFileName.split("/")[1]        # filename is the filename only
    filesize = s.recv(1024).decode("utf-8")
    l = len(DiskList)

    # filetmp is for file which uploaded to server temporarily
    directory = "/tmp/filetmp/"
    if not os.path.exists(directory): os.makedirs(directory)        # create a folder
    
    # receive data from client and write into file
    file = directory + filename
    f = open(str(file), 'wb')
    data = s.recv(1024)
    TotalRecv = len(data)
    f.write(data)
    while TotalRecv < int(filesize):
        data = s.recv(1024)
        TotalRecv += len(data)
        f.write(data)
    f.close()
    print("File completely upload to server!")

    # decide which disk to be main disk and backup disk
    UserFileHash = int(FilenameHash(UserFileName), 2)        # convert binary to decimal
    i = 0
    while i < l:
        if (UserFileHash >= 2**(int(partition))*i/l and UserFileHash < 2**(int(partition))*(i+1)/l): 
            UploadMainDisk = DiskList[i]
            if (i != (l-1)): UploadBackupDisk = DiskList[i+1]
            else: UploadBackupDisk = DiskList[0]
            print("main disk: "+UploadMainDisk)
            print("backup disk: "+UploadBackupDisk)
        i += 1            

    # create a script commandfile.sh to run two cammands: CreatFolder and CopyFile
    commandfile = open('commandfile.sh', 'w')
    os.chmod("./commandfile.sh", 0o700)
    CreatFolder = "ssh -o \"StrictHostKeyChecking no\" "+LoginName+"@"+UploadMainDisk+" \"mkdir -p /tmp/"+LoginName+"/"+username+"\""
    CopyFile = "scp -B /tmp/filetmp/"+filename+" "+LoginName+"@"+UploadMainDisk+":/tmp/"+LoginName+"/"+username+"/"+filename
    commandfile.write(CreatFolder+'\n')
    commandfile.write(CopyFile+'\n')
    commandfile.close()
    os.system('sh commandfile.sh')
    os.remove('commandfile.sh')

    # do the same thing for backup
    commandfile = open('commandfile.sh', 'w')
    os.chmod("./commandfile.sh", 0o700)
    CreatFolder = "ssh -o \"StrictHostKeyChecking no\" "+LoginName+"@"+UploadBackupDisk+" \"mkdir -p /tmp/"+LoginName+"/"+username+"\""
    CopyFile = "scp -B /tmp/filetmp/"+filename+" "+LoginName+"@"+UploadBackupDisk+":/tmp/"+LoginName+"/"+username+"/"+filename
    commandfile.write(CreatFolder+'\n')
    commandfile.write(CopyFile+'\n')
    commandfile.close()
    os.system('sh commandfile.sh')
    os.remove('commandfile.sh')
    
    # remove temporary file and folder in server
    os.remove('/tmp/filetmp/'+filename)
    os.rmdir('/tmp/filetmp')

    # d for recording files in disks   
    d.get(UploadMainDisk).append(LoginName+"/"+username+"/"+filename)
    d.get(UploadBackupDisk).append(LoginName+"/"+username+"/"+filename)

    # send result back to client
    s.send((username+"/"+filename+" was mainly saved in "+UploadMainDisk+" and saved in "+UploadBackupDisk+" for backup.").encode("utf-8"))    

    print(d)
    return 0


def DownloadCommand(UserFileName, partition, s, DiskList, LoginName, d):
    ### backup not yet
    username = UserFileName.split("/")[0]     
    filename = UserFileName.split("/")[1]        # filename is the filename only
    l = len(DiskList)

    # filetmp is for storing the temporary file which disk send to server 
    directory = "/tmp/filetmp/"
    if not os.path.exists(directory): os.makedirs(directory)        # create a folder

    # find the file's location (main disk and backup disk)
    UserFileHash = int(FilenameHash(UserFileName), 2)        # convert binary to decimal
    i = 0
    while i < l:
        if (UserFileHash >= 2**(int(partition))*i/l and UserFileHash < 2**(int(partition))*(i+1)/l): 
            DownloadMainDisk = DiskList[i]
            if (i != (l-1)): DownloadBackupDisk = DiskList[i+1]
            else: DownloadBackupDisk = DiskList[0]
            print("main disk of the file: "+DownloadMainDisk)
            print("back up disk of the file: "+DownloadBackupDisk)
        i += 1

    # create a script commandfile.sh to run cammand: CopyFile
    commandfile = open('commandfile.sh', 'w')
    os.chmod("./commandfile.sh", 0o700)
    CopyFile = "scp -B "+LoginName+"@"+DownloadMainDisk+":/tmp/"+LoginName+"/"+username+"/"+filename+" "+"/tmp/filetmp/"+filename
    commandfile.write(CopyFile+'\n')
    commandfile.close()
    os.system('sh commandfile.sh')
    os.remove('commandfile.sh')

    file = directory+filename
    if os.path.isfile(file):
        filesize = str(os.path.getsize(file))
        s.send(filesize.encode("utf-8"))
        with open(file, 'rb') as f:
            bytesToSend = f.read(1024)
            s.send(bytesToSend)
            try:
                bytesToSend = f.read(1024)
                s.send(bytesToSend)
            except:
                pass
        f.close()
    else:
        s.send("Error!")
    os.remove('/tmp/filetmp/'+filename)
    os.rmdir('/tmp/filetmp')

    return 0


def ListCommand(UserFileName, partition, s, DiskList, LoginName, d):
    username = UserFileName.split("/")[0]
    l = len(DiskList)

    directory = "/tmp/filetmp/"
    if not os.path.exists(directory): os.makedirs(directory)        # create a folder

    commandfile = open('commandfile.sh', 'w')
    os.chmod("./commandfile.sh", 0o700)
    
    i = 0
    while i < l:
        GetDiskList = "ssh -o \"StrictHostKeyChecking no\" "+LoginName+"@"+DiskList[i]+" \"cd /tmp/"+LoginName+"/"+username+" ; "+"ls -lrt >> ~/output"+str(i)+".txt"+"\""
        CopyFile = "scp -B "+LoginName+"@"+DiskList[i]+":~/output"+str(i)+".txt"+" "+"/tmp/filetmp/"+"output"+str(i)+".txt"
        RemoveOutput = "ssh -o \"StrictHostKeyChecking no\" "+LoginName+"@"+DiskList[i]+" \"rm ~/output"+str(i)+".txt"+"\""
        commandfile.write(GetDiskList+'\n')
        commandfile.write(CopyFile+'\n')
        commandfile.write(RemoveOutput+'\n')    
        i += 1
    commandfile.close()
    os.system('sh commandfile.sh')
    
    OutputNames = []
    for i in range(l):
        OutputNames.append(directory+"output"+str(i)+".txt")

    with open(directory+'output.txt', 'w') as outfile:
        for oname in OutputNames:
            with open(oname) as infile:
                outfile.write(infile.read())

    # GetDiskList = "ssh -o \"StrictHostKeyChecking no\" "+LoginName+"@"+DiskList[0]+" \"cd /tmp/"+LoginName+"/"+username+" ; "+"ls -lrt >> ~/output.txt"+"\""
    # CopyFile = "scp -B "+LoginName+"@"+DiskList[0]+":~/output.txt"+" "+"/tmp/filetmp/"+"output.txt"
    # RemoveOutput = "ssh -o \"StrictHostKeyChecking no\" "+LoginName+"@"+DiskList[0]+" \"rm ~/output.txt"+"\""
    # commandfile.write(GetDiskList+'\n')
    # commandfile.write(CopyFile+'\n')
    # commandfile.write(RemoveOutput+'\n')    
    # commandfile.close()
    # os.system('sh commandfile.sh')
    
    filesize = str(os.path.getsize(directory+'output.txt'))
    s.send(filesize.encode("utf-8"))
    with open(directory+'output.txt', 'rb') as f:
        bytesToSend = f.read(1024)
        s.send(bytesToSend)
        try:
            bytesToSend = f.read(1024)
            s.send(bytesToSend)
        except:
            pass
    
    os.remove('/tmp/filetmp/output.txt')
    os.rmdir('/tmp/filetmp')

    return 0


def DeleteCommand(UserFileName, partition, s, DiskList, LoginName, d):
    username = UserFileName.split("/")[0]     
    filename = UserFileName.split("/")[1]        # filename is the filename only
    l = len(DiskList)
    
    UserFileHash = int(FilenameHash(UserFileName), 2)        # convert binary to decimal
    i = 0
    while i < l:
        if (UserFileHash >= 2**(int(partition))*i/l and UserFileHash < 2**(int(partition))*(i+1)/l): 
            FileMainDisk = DiskList[i]
            if (i != (l-1)): FileBackupDisk = DiskList[i+1]
            else: FileBackupDisk = DiskList[0]
            print("file is mainly in: "+FileMainDisk)
            print("backup file is in: "+FileBackupDisk)
        i += 1

    # create a script commandfile.sh to run cammand: DeleteFile
    commandfile = open('commandfile.sh', 'w')
    os.chmod("./commandfile.sh", 0o700)
    DeleteFile = "ssh -o \"StrictHostKeyChecking no\" "+LoginName+"@"+FileMainDisk+" \"cd /tmp/"+LoginName+"/"+username+" ; "+"rm "+filename+"\""
    commandfile.write(DeleteFile+'\n')
    commandfile.close()
    os.system('sh commandfile.sh')
    os.remove('commandfile.sh')

    # delete backup file
    commandfile = open('commandfile.sh', 'w')
    os.chmod("./commandfile.sh", 0o700)
    DeleteFile = "ssh -o \"StrictHostKeyChecking no\" "+LoginName+"@"+FileBackupDisk+" \"cd /tmp/"+LoginName+"/"+username+" ; "+"rm "+filename+"\""
    commandfile.write(DeleteFile+'\n')
    commandfile.close()
    os.system('sh commandfile.sh')
    os.remove('commandfile.sh')

    # delete file record in d    
    
    # send result back to client
    s.send((username+"/"+filename+" was deleted from main disk: "+FileMainDisk+" and backup disk: "+FileBackupDisk).encode("utf-8"))    
    return 0


def Main():
    script = sys.argv[0]
    partition = sys.argv[1]
    DiskList = sys.argv[2:]

    LoginName = os.getlogin()
    host = get_free_address()
    port = get_free_port()

    # d for recording files in disks
    d = {}
    for i in DiskList:
        d[i] = []

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Socket successfully created")
    
    s.bind((host, port))
    s.listen(5)
    print("Listening on %s %d" % (host, port))

    try:
        while True:
            print("Waiting for command...")
            conn, addr = s.accept()
            print('Got connection from', addr)

            data = conn.recv(1024).decode("utf-8")
            command = data.split( )
            if (command[0] == "upload"): UploadCommand(command[1], partition, conn, DiskList, LoginName, d)
            if (command[0] == "download"): DownloadCommand(command[1], partition, conn, DiskList, LoginName, d)
            if (command[0] == "list"): ListCommand(command[1], partition, conn, DiskList, LoginName, d)
            if (command[0] == "delete"): DeleteCommand(command[1], partition, conn, DiskList, LoginName, d)

            # conn.send("server received you message.".encode("utf-8"))    
    except: pass
    s.close()


if __name__ == '__main__':
    Main()










# https://pypi.python.org/pypi/uhashring/0.4
# https://gist.github.com/kevinkindom/108ffd675cb9253f8f71
