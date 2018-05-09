import socket
import hashlib
import math
import os
import subprocess
import sys
import shutil


def get_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 0))
    addr, port = s.getsockname()
    s.close()
    return port


def get_free_address():
    host = socket.gethostbyname(socket.gethostname())
    return host


def FilenameHash(filename, partition):
    h = hashlib.md5(filename.encode("utf-8")).hexdigest()
    x = bin(int(h, 16))[2:]        # convert hex to binary
    y = 128 - int(partition)
    x_partition =  x[y:]        # take last 16 digit as index
    return x_partition


def RestoreFiles(LoginName, username, filename, BackupDisk, MainDisk):
    # restore from BackupDisk 
    # download
    directory = "/tmp/filetmp/"
    if not os.path.exists(directory): 
        os.makedirs(directory)

    commandfile = open('commandfile.sh', 'w')
    os.chmod("./commandfile.sh", 0o700)
    CopyFile = "scp -B "+LoginName+"@"+BackupDisk+":/tmp/"+LoginName+"/backupfolder/"+username+"/"+filename+" "+"/tmp/filetmp/"+filename
    commandfile.write(CopyFile+'\n')
    commandfile.close()
    os.system('sh commandfile.sh')
    os.remove('commandfile.sh')
    
    # upload
    commandfile = open('commandfile.sh', 'w')
    os.chmod("./commandfile.sh", 0o700)
    CopyFile = "scp -B /tmp/filetmp/"+filename+" "+LoginName+"@"+MainDisk+":/tmp/"+LoginName+"/"+username+"/"+filename
    commandfile.write(CopyFile+'\n')
    commandfile.close()
    os.system('sh commandfile.sh')
    os.remove('commandfile.sh')

    # restore from MainDisk
    # download
    commandfile = open('commandfile.sh', 'w')
    os.chmod("./commandfile.sh", 0o700)
    CopyFile = "scp -B "+LoginName+"@"+MainDisk+":/tmp/"+LoginName+"/"+username+"/"+filename+" "+"/tmp/filetmp/"+filename
    commandfile.write(CopyFile+'\n')
    commandfile.close()
    os.system('sh commandfile.sh')
    os.remove('commandfile.sh')
    
    # upload
    commandfile = open('commandfile.sh', 'w')
    os.chmod("./commandfile.sh", 0o700)
    CopyFile = "scp -B /tmp/filetmp/"+filename+" "+LoginName+"@"+BackupDisk+":/tmp/"+LoginName+"/backupfolder/"+username+"/"+filename
    commandfile.write(CopyFile+'\n')
    commandfile.close()
    os.system('sh commandfile.sh')
    os.remove('commandfile.sh')


def DownloadUpload(LoginName, username, filename, DownloadMainDisk, UploadMainDisk):
   # download
    directory = "/tmp/filetmp/"
    if not os.path.exists(directory): 
        os.makedirs(directory)

    commandfile = open('commandfile.sh', 'w')
    os.chmod("./commandfile.sh", 0o700)
    CopyFile = "scp -B "+LoginName+"@"+DownloadMainDisk+":/tmp/"+LoginName+"/"+username+"/"+filename+" "+"/tmp/filetmp/"+filename
    commandfile.write(CopyFile+'\n')
    commandfile.close()
    os.system('sh commandfile.sh')
    os.remove('commandfile.sh')
    
    # upload
    commandfile = open('commandfile.sh', 'w')
    os.chmod("./commandfile.sh", 0o700)
    CreatFolder = "ssh -o \"StrictHostKeyChecking no\" "+LoginName+"@"+UploadMainDisk+" \"mkdir -p /tmp/"+LoginName+"/"+username+"\""
    CopyFile = "scp -B /tmp/filetmp/"+filename+" "+LoginName+"@"+UploadMainDisk+":/tmp/"+LoginName+"/"+username+"/"+filename
    commandfile.write(CreatFolder+'\n')
    commandfile.write(CopyFile+'\n')
    commandfile.close()
    os.system('sh commandfile.sh')
    os.remove('commandfile.sh')

    os.remove('/tmp/filetmp/'+filename)
    os.rmdir('/tmp/filetmp') 


def Delete(LoginName, username, filename, DownloadMainDisk, UploadMainDisk):
    # delete
    commandfile = open('commandfile.sh', 'w')
    os.chmod("./commandfile.sh", 0o700)
    DeleteFile = "ssh -o \"StrictHostKeyChecking no\" "+LoginName+"@"+DownloadMainDisk+" \"cd /tmp/"+LoginName+"/"+username+" ; "+"rm "+filename+"\""
    commandfile.write(DeleteFile+'\n')
    commandfile.close()
    os.system('sh commandfile.sh')
    os.remove('commandfile.sh')


def DownloadUploadForBackup(LoginName, username, filename, DownloadMainDisk, UploadMainDisk):
   # download
    directory = "/tmp/filetmp/"
    if not os.path.exists(directory): 
        os.makedirs(directory)

    commandfile = open('commandfile.sh', 'w')
    os.chmod("./commandfile.sh", 0o700)
    CopyFile = "scp -B "+LoginName+"@"+DownloadMainDisk+":/tmp/"+LoginName+"/backupfolder/"+username+"/"+filename+" "+"/tmp/filetmp/"+filename
    commandfile.write(CopyFile+'\n')
    commandfile.close()
    os.system('sh commandfile.sh')
    os.remove('commandfile.sh')

    # upload
    commandfile = open('commandfile.sh', 'w')
    os.chmod("./commandfile.sh", 0o700)
    CreatFolderB = "ssh -o \"StrictHostKeyChecking no\" "+LoginName+"@"+UploadMainDisk+" \"mkdir -p /tmp/"+LoginName+"/backupfolder"+"\""    
    CreatFolder = "ssh -o \"StrictHostKeyChecking no\" "+LoginName+"@"+UploadMainDisk+" \"mkdir -p /tmp/"+LoginName+"/backupfolder/"+username+"\""
    CopyFile = "scp -B /tmp/filetmp/"+filename+" "+LoginName+"@"+UploadMainDisk+":/tmp/"+LoginName+"/backupfolder/"+username+"/"+filename
    commandfile.write(CreatFolderB+'\n')    
    commandfile.write(CreatFolder+'\n')       
    commandfile.write(CopyFile+'\n')
    commandfile.close()
    os.system('sh commandfile.sh')
    os.remove('commandfile.sh')

    os.remove('/tmp/filetmp/'+filename)
    os.rmdir('/tmp/filetmp') 


def DeleteForBackup(LoginName, username, filename, DownloadMainDisk, UploadMainDisk):
    # delete
    commandfile = open('commandfile.sh', 'w')
    os.chmod("./commandfile.sh", 0o700)
    DeleteFile = "ssh -o \"StrictHostKeyChecking no\" "+LoginName+"@"+DownloadMainDisk+" \"cd /tmp/"+LoginName+"/backupfolder/"+username+" ; "+"rm "+filename+"\""
    commandfile.write(DeleteFile+'\n')
    commandfile.close()
    os.system('sh commandfile.sh')
    os.remove('commandfile.sh')


def UploadCommand(UserFileName, partition, s, DiskList, LoginName, d, DiskPartitionArray, DPAHelper, UserFileHashSet):
    username = UserFileName.split("/")[0] 
    filename = UserFileName.split("/")[1]        # filename is the filename only
    filesize = s.recv(1024).decode("utf-8")
    l = len(DiskList)

    # filetmp is for file which uploaded to server temporarily
    directory = "/tmp/filetmp/"
    if not os.path.exists(directory): 
        os.makedirs(directory)
    
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
    UserFileHash = int(FilenameHash(UserFileName, partition), 2)        # convert binary to decimal  
    UploadMainDisk = DiskList[DiskPartitionArray[UserFileHash]]
    if (DiskPartitionArray[UserFileHash] != (l-1)): 
        UploadBackupDisk = DiskList[DiskPartitionArray[UserFileHash]+1]
    else: 
        UploadBackupDisk = DiskList[0]

    # record UserFileHash in UserFileHashSet using in AddCommand
    UserFileHashSet.add(UserFileHash)

    # record UserFileName in DPAHelper, look up file by index from UserFileHashSet
    DPAHelper[UserFileHash] = UserFileName

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

    # do the same thing for backup but under backup folder
    commandfile = open('commandfile.sh', 'w')
    os.chmod("./commandfile.sh", 0o700)
    CreatFolderB = "ssh -o \"StrictHostKeyChecking no\" "+LoginName+"@"+UploadBackupDisk+" \"mkdir -p /tmp/"+LoginName+"/backupfolder"+"\""    
    CreatFolder = "ssh -o \"StrictHostKeyChecking no\" "+LoginName+"@"+UploadBackupDisk+" \"mkdir -p /tmp/"+LoginName+"/backupfolder/"+username+"\""
    CopyFile = "scp -B /tmp/filetmp/"+filename+" "+LoginName+"@"+UploadBackupDisk+":/tmp/"+LoginName+"/backupfolder/"+username+"/"+filename
    commandfile.write(CreatFolderB+'\n')
    commandfile.write(CreatFolder+'\n')
    commandfile.write(CopyFile+'\n')
    commandfile.close()
    os.system('sh commandfile.sh')
    os.remove('commandfile.sh')
    
    # remove temporary file and folder in server
    os.remove('/tmp/filetmp/'+filename)
    os.rmdir('/tmp/filetmp')

    # d for recording files in disks using in ListCommand
    d.get(UploadMainDisk).append(LoginName+"/"+username+"/"+filename)
    d.get(UploadBackupDisk).append(LoginName+"/backupfolder/"+username+"/"+filename)

    # send result back to client
    s.send((username+"/"+filename+" was mainly saved in "+UploadMainDisk+" and saved in "+UploadBackupDisk+" for backup.").encode("utf-8"))    
    
    # display the result
    print(username+"/"+filename+" was mainly saved in "+UploadMainDisk+" and saved in "+UploadBackupDisk+" for backup.")
    
    print(d)
    print(UserFileHashSet)

    return 0


def DownloadCommand(UserFileName, partition, s, DiskList, LoginName, d, DiskPartitionArray, DPAHelper, UserFileHashSet):
    ### backup restore not yet
    username = UserFileName.split("/")[0]     
    filename = UserFileName.split("/")[1]        # filename is the filename only
    l = len(DiskList)

    # check the file is existed or not
    if UserFileName not in DPAHelper:
        s.send("The file is not exist.".encode("utf-8"))    
        return 0
    else:
        s.send("Start downloading...".encode("utf-8"))    

    # decide which disk to be main disk and backup disk
    UserFileHash = int(FilenameHash(UserFileName, partition), 2)        # convert binary to decimal
    DownloadMainDisk = DiskList[DiskPartitionArray[UserFileHash]]
    if (DiskPartitionArray[UserFileHash] != (l-1)): 
        DownloadBackupDisk = DiskList[DiskPartitionArray[UserFileHash]+1]
    else: 
        DownloadBackupDisk = DiskList[0]

    RestoreFiles(LoginName, username, filename, DownloadBackupDisk, DownloadMainDisk)

    # filetmp is for storing the temporary file which disk send to server 
    directory = "/tmp/filetmp/"
    if not os.path.exists(directory): 
        os.makedirs(directory)

    # create a script commandfile.sh to run cammand: CopyFile
    commandfile = open('commandfile.sh', 'w')
    os.chmod("./commandfile.sh", 0o700)
    CopyFile = "scp -B "+LoginName+"@"+DownloadMainDisk+":/tmp/"+LoginName+"/"+username+"/"+filename+" "+"/tmp/filetmp/"+filename
    commandfile.write(CopyFile+'\n')
    commandfile.close()
    os.system('sh commandfile.sh')
    os.remove('commandfile.sh')

    file = directory+filename
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

    os.remove('/tmp/filetmp/'+filename)
    os.rmdir('/tmp/filetmp')
    
    # display the result
    print(username+"/"+filename+" was downloaded from "+DownloadMainDisk)

    print(d)
    print(UserFileHashSet)

    return 0


def ListCommand(username, partition, s, DiskList, LoginName, d, DiskPartitionArray, DPAHelper, UserFileHashSet):
    l = len(DiskList)
    print(username)
    CommandFileAll = open('CommandFileAll.sh', 'w')
    os.chmod("./CommandFileAll.sh", 0o700)

    directory = "/tmp/filetmp/"
    if not os.path.exists(directory): 
        os.makedirs(directory)
  
    # after seen username in filelist, do CommandFileAll
    # check d, example of d: {'129.210.16.83': ['kgau/a2/t.txt'], '129.210.16.84': ['kgau/a1/t.txt', 'kgau/backupfolder/a2/t.txt'], '129.210.16.85': ['kgau/backupfolder/a1/t.txt']}
    # if the MainDisk doesn't have user's file, CommandFileAll wouldn't access it
    for MainDisk in d.keys():        # example of MainDisk: '129.210.16.84'
        print(MainDisk)
        filelist = d.get(MainDisk)        # example of filelist: ['kgau/a1/t.txt', 'kgau/a2/t.txt']
        for LoginUserFile in filelist:        # example of LoginUserFile: 'kgau/a1/t.txt'
            if (LoginUserFile.find(username) != -1 and LoginUserFile.find("backupfolder") == -1):
                filename = LoginUserFile.split("/")[2]
                UserFileName = LoginUserFile.split("/")[1]+"/"+LoginUserFile.split("/")[2]
                UserFileHash = int(FilenameHash(UserFileName, partition), 2)        # convert binary to decimal

                if (DiskPartitionArray[UserFileHash] != (l-1)): 
                    BackupDisk = DiskList[DiskPartitionArray[UserFileHash]+1]
                else: 
                    BackupDisk = DiskList[0]

                RestoreFiles(LoginName, username, filename, BackupDisk, MainDisk)
                GetDiskList = "ssh -o \"StrictHostKeyChecking no\" "+LoginName+"@"+MainDisk+" \"cd /tmp/"+LoginName+"/"+username+" ; "+"ls -lrt >> ~/output"+MainDisk+".txt"+"\""
                CopyFile = "scp -B "+LoginName+"@"+MainDisk+":~/output"+MainDisk+".txt"+" "+"/tmp/filetmp/"+"output"+MainDisk+".txt"
                RemoveOutput = "ssh -o \"StrictHostKeyChecking no\" "+LoginName+"@"+MainDisk+" \"rm ~/output"+MainDisk+".txt"+"\""
                CommandFileAll.write(GetDiskList+'\n')
                CommandFileAll.write(CopyFile+'\n')
                CommandFileAll.write(RemoveOutput+'\n')

    CommandFileAll.close()
    os.system('sh CommandFileAll.sh')
    os.remove('CommandFileAll.sh')

    OutputNames = os.listdir(directory)
    with open(directory+'output.txt', 'w') as outfile:
        for oname in OutputNames:
            with open(directory+oname) as infile:
                outfile.write(infile.read())
            infile.close()
            os.remove(directory+oname)
    outfile.close()
    
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
    print("Listing is completed.")
    return 0


def DeleteCommand(UserFileName, partition, s, DiskList, LoginName, d, DiskPartitionArray, DPAHelper, UserFileHashSet):
    # check the file is existed or not
    if UserFileName not in DPAHelper:
        s.send("The file is not exist.".encode("utf-8"))    
        return 0
    else:
        s.send("Start deleting...".encode("utf-8"))  

    username = UserFileName.split("/")[0]     
    filename = UserFileName.split("/")[1]        # filename is the filename only
    l = len(DiskList)
    
    UserFileHash = int(FilenameHash(UserFileName, partition), 2)        # convert binary to decimal
    FileMainDisk = DiskList[DiskPartitionArray[UserFileHash]]
    if (DiskPartitionArray[UserFileHash] != (l-1)): 
        FileBackupDisk = DiskList[DiskPartitionArray[UserFileHash]+1]
    else: 
        FileBackupDisk = DiskList[0]
    print("file is mainly in: "+FileMainDisk)
    print("backup file is in: "+FileBackupDisk)

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
    DeleteFile = "ssh -o \"StrictHostKeyChecking no\" "+LoginName+"@"+FileBackupDisk+" \"cd /tmp/"+LoginName+"/backupfolder/"+username+" ; "+"rm "+filename+"\""
    commandfile.write(DeleteFile+'\n')
    commandfile.close()
    os.system('sh commandfile.sh')
    os.remove('commandfile.sh')

    # delete file record in d
    # if files under user are all deleted, delete user folder
    for disk in d.keys():        # example of disk: '129.210.16.84'
        filelist = d.get(disk)        # example of filelist: ['kgau/a1/t.txt', 'kgau/a2/t.txt']
        for LoginUserFile in filelist:        # example of LoginUserFile: 'kgau/a1/t.txt'
            if (LoginUserFile.find(username+"/"+filename) != -1):
                filelist.remove(LoginUserFile)

    # delete file record in UserFileHashSet
    UserFileHashSet.remove(UserFileHash)

    # delete file record in DPAHelper
    DPAHelper[UserFileHash] = ""
    print(UserFileHashSet)

    # send result back to client
    s.send((username+"/"+filename+" was deleted from main disk: "+FileMainDisk+" and backup disk: "+FileBackupDisk).encode("utf-8"))    
    
    # display the result
    print(username+"/"+filename+" was deleted from main disk: "+FileMainDisk+" and backup disk: "+FileBackupDisk) 

    print(d)
    print(UserFileHashSet)

    return 0

def AddCommand(NewDisk, partition, s, DiskList, LoginName, d, DiskPartitionArray, DPAHelper, UserFileHashSet, ipNo):
    DiskList.append(NewDisk)
    d[NewDisk] = []
    l = len(DiskList)
    ipNo[NewDisk] = len(ipNo)
    l2 = len(ipNo)
    # add new disk record to DiskPartitionArray
    for j in range(l2):
        count = 0
        for i in range(len(DiskPartitionArray)):
            if DiskPartitionArray[i] == j and count < 2**(int(partition))/l-1:
                
                # move backup files from DiskList[0] to DiskList[l-1]
                if i in UserFileHashSet and j == (l-2):
                    username = DPAHelper[i].split("/")[0] 
                    filename = DPAHelper[i].split("/")[1]
                    DownloadUploadForBackup(LoginName, username, filename, DiskList[0], DiskList[l-1])
                    DeleteForBackup(LoginName, username, filename, DiskList[0], DiskList[l-1])

                    d.get(DiskList[l-1]).append(LoginName+"/backupfolder/"+username+"/"+filename)
                    filelist = d.get(DiskList[0])
                    for LoginUserFile in filelist:
                        if (LoginUserFile.find("/backupfolder/"+username+"/"+filename) != -1):
                            filelist.remove(LoginUserFile)
                count += 1
            elif DiskPartitionArray[i] == j:
                DiskPartitionArray[i] = ipNo.get(NewDisk)

                # if i in set should change file's ip address
                if i in UserFileHashSet:
                    username = DPAHelper[i].split("/")[0] 
                    filename = DPAHelper[i].split("/")[1]
                    DownloadMainDisk = DiskList[j]
                    UploadMainDisk = DiskList[ipNo.get(NewDisk)]
                    if (j != (l-2)): 
                        DownloadBackupDisk = DiskList[j+1]
                    else: 
                        DownloadBackupDisk = DiskList[0]
                    UploadBackupDisk = DiskList[0]

                    # do download and upload and delete
                    DownloadUpload(LoginName, username, filename, DownloadMainDisk, UploadMainDisk)
                    Delete(LoginName, username, filename, DownloadMainDisk, UploadMainDisk)

                    # do download and upload and delete for backup files
                    DownloadUploadForBackup(LoginName, username, filename, DownloadBackupDisk, UploadBackupDisk)
                    DeleteForBackup(LoginName, username, filename, DownloadBackupDisk, UploadBackupDisk)

                    # change the record in d
                    d.get(UploadMainDisk).append(LoginName+"/"+username+"/"+filename)
                    filelist = d.get(DownloadMainDisk)
                    for LoginUserFile in filelist:
                        if (LoginUserFile.find(username+"/"+filename) != -1):
                            filelist.remove(LoginUserFile)

                    d.get(UploadBackupDisk).append(LoginName+"/backupfolder/"+username+"/"+filename)
                    filelist = d.get(DownloadBackupDisk)
                    for LoginUserFile in filelist:
                        if (LoginUserFile.find("/backupfolder/"+username+"/"+filename) != -1):
                            filelist.remove(LoginUserFile)
                count +=1           

    print(d)
    print(UserFileHashSet)
    print(DiskPartitionArray)

    # send result back to client
    result = str(d)
    s.send(("All files are now in disks:"+result).encode("utf-8"))    


    return 0


def RemoveCommand(OldDisk, partition, s, DiskList, LoginName, d, DiskPartitionArray, DPAHelper, UserFileHashSet, ipNo):
    OldDiskPartitionArray = []
    OldDiskPartitionArray.extend(DiskPartitionArray)

    # check if OldDisk is exist
    if OldDisk in DiskList:
        OldDiskNo = DiskList.index(OldDisk)
    else: 
        return 0

    l = len(DiskList)
    l2 = len(ipNo)

    # remove old disk record in DiskPartitionArray
    for j in range(l2):
        count = 0
        # count existed 0,0,0,0...
        for i in range(len(DiskPartitionArray)):
            if DiskPartitionArray[i] == j:
                count += 1
        for k in range(len(DiskPartitionArray)):
            if DiskPartitionArray[k] == OldDiskNo and count < 2**(int(partition))/(l-1):
                DiskPartitionArray[k] = ipNo.get(DiskList[j])
                count += 1
    
    for h in range(len(DiskPartitionArray)):
        if OldDiskPartitionArray[h] == OldDiskNo-1 and h in UserFileHashSet:
            username = DPAHelper[h].split("/")[0] 
            filename = DPAHelper[h].split("/")[1]

            DownloadUploadForBackup(LoginName, username, filename, OldDisk, DiskList[OldDiskNo+1])
            DeleteForBackup(LoginName, username, filename, OldDisk, DiskList[OldDiskNo+1])
            d.get(DiskList[OldDiskNo+1]).append(LoginName+"/backupfolder/"+username+"/"+filename)

        # if k in set should change file's ip address
        if OldDiskPartitionArray[h] == OldDiskNo and h in UserFileHashSet:
            username = DPAHelper[h].split("/")[0] 
            filename = DPAHelper[h].split("/")[1]

            DownloadMainDisk = OldDisk
            UploadMainDisk = DiskList[DiskPartitionArray[h]]
            if DiskPartitionArray[h] != (l-1): 
                DownloadBackupDisk = DiskList[OldDiskNo+1]
            else: 
                DownloadBackupDisk = DiskList[0]
            if DiskPartitionArray[h] != OldDiskNo-1:
                UploadBackupDisk = DiskList[DiskPartitionArray[h]+1]
            else:
                UploadBackupDisk = DiskList[DiskPartitionArray[h]+2]

            # do download and upload and delete
            if  UploadMainDisk != DownloadMainDisk:
                DownloadUpload(LoginName, username, filename, DownloadMainDisk, UploadMainDisk)
                Delete(LoginName, username, filename, DownloadMainDisk, UploadMainDisk)
            
            # do download and upload and delete for backup files
            if UploadBackupDisk != DownloadBackupDisk:
                DownloadUploadForBackup(LoginName, username, filename, DownloadBackupDisk, UploadBackupDisk)
                DeleteForBackup(LoginName, username, filename, DownloadBackupDisk, UploadBackupDisk)

            # change the record in d
            if  UploadMainDisk != DownloadMainDisk:
                d.get(UploadMainDisk).append(LoginName+"/"+username+"/"+filename)
            if UploadBackupDisk != DownloadBackupDisk:
                d.get(UploadBackupDisk).append(LoginName+"/backupfolder/"+username+"/"+filename)

    
    DiskList.remove(OldDisk)
    del d[OldDisk]

    print(d)   
    print(UserFileHashSet)
    print(DiskPartitionArray)

    # send result back to client
    result = str(d)
    s.send(("All files are now in disks:"+result).encode("utf-8"))

    return 0


def Main():
    script = sys.argv[0]
    partition = sys.argv[1]
    DiskList = sys.argv[2:]
    l = len(DiskList)

    LoginName = os.getlogin()
    host = get_free_address()
    port = get_free_port()

    # d for recording files in disks
    d = {}
    for i in DiskList:
        d[i] = []

    ipNo = {}
    for i in range(len(DiskList)):
        ipNo[DiskList[i]] = i

    # DiskPartitionArray for recording the relation between partition no. and disk
    # DPAHelper record filename of UserFileHash
    DiskPartitionArray = [0] * (2 ** int(partition))
    DPAHelper = [""] * (2 ** int(partition))

    for PartitionNumber in range(len(DiskPartitionArray)):
        for i in range(l):
            if (PartitionNumber >= 2**(int(partition))*i/l and PartitionNumber < 2**(int(partition))*(i+1)/l): 
                DiskPartitionArray[PartitionNumber] = i  

    # UserFileHashSet for recording what files we have
    UserFileHashSet = set()

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
            if (command[0] == "upload"): UploadCommand(command[1], partition, conn, DiskList, LoginName, d, DiskPartitionArray, DPAHelper, UserFileHashSet)
            if (command[0] == "download"): DownloadCommand(command[1], partition, conn, DiskList, LoginName, d, DiskPartitionArray, DPAHelper, UserFileHashSet)
            if (command[0] == "list"): ListCommand(command[1], partition, conn, DiskList, LoginName, d, DiskPartitionArray, DPAHelper, UserFileHashSet)
            if (command[0] == "delete"): DeleteCommand(command[1], partition, conn, DiskList, LoginName, d, DiskPartitionArray, DPAHelper, UserFileHashSet)
            if (command[0] == "add"): AddCommand(command[1], partition, conn, DiskList, LoginName, d, DiskPartitionArray, DPAHelper, UserFileHashSet, ipNo)
            if (command[0] == "remove"): RemoveCommand(command[1], partition, conn, DiskList, LoginName, d, DiskPartitionArray, DPAHelper, UserFileHashSet, ipNo)

            # conn.send("server received you message.".encode("utf-8"))    
    except: 
        pass
    s.close()

    try: 
        shutil.rmtree("/tmp/filetmp/")
    except: 
        pass


if __name__ == '__main__':
    Main()

