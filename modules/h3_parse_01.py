import zipfile


def get_names_from_zip(zipfn,mask):
    print('Extracting data from',zipfn)
    name=''
    try: zip=zipfile.ZipFile(zipfn)
    except:
        print('Error opening file',zipfn)
        return name
    full_list=zip.namelist()
    for n in full_list:
        if mask in n:
            name=n
            #print(n)
    return name

#get_names_from_zip('HPE 3PAR StoreServ Performance Data Collection_rumsk1stg01.zip','statcpu','statvv')

def get_data_from_zip(zipfn,stats_type):
    name=get_names_from_zip(zipfn,stats_type)
    zip=zipfile.ZipFile(zipfn)
    f=zip.open(name)
    contents=f.read()
    content_d=contents.decode()
#    print(content_d)
    return content_d

#get_data_from_zip('HPE 3PAR StoreServ Performance Data Collection_rumsk1stg01.zip')

def cpu_3par(zipfn,time1,time2):
    time=list()
    cpu_sys=dict([(0,list()),(1,list()),(2,list()),(3,list()),(4,list()),(5,list()),(6,list()),(7,list())])
    cpu_use=dict([(0,list()),(1,list()),(2,list()),(3,list()),(4,list()),(5,list()),(6,list()),(7,list())])
    cpu_bus=dict([(0,list()),(1,list()),(2,list()),(3,list()),(4,list()),(5,list()),(6,list()),(7,list())])
    node_index=0
    nodes=list()
    data=get_data_from_zip(zipfn,'statcpu')
#    print(data)
    Lines=data.splitlines()
    for line in Lines:
            if len(line)>2 and line[2]==':':
                line=line.rstrip()
                words=line.split()
                time_last=words[1]+' '+words[0]
                time.append(time_last)
            if 'total' in line:
                line=line.rstrip()
                node_index=int(line[1])
                nodes.append(node_index)
                words=line.split()
                cpu_use[node_index].append(int(words[1]))
                cpu_sys[node_index].append(int(words[2]))
                #cpu_bus[node_index].append(int(words[1])+int(words[2]))
    print(len(Lines),'lines of data processed.')
    print('=======================================================\n')
    print('Start time:',min(time))
    print('End time:',max(time))
    try:
        if time1>min(time): t1=time1
        else:t1=min(time)
    except: t1=min(time)
    try:
        if time2<max(time): t2=time2
        else:t2=max(time)
    except: t2=max(time)
    print('Selected interval:',t1,'to', t2,'\n')
    print('=======================================================')

    fulltime=time
    i=0
    while True:
        if time[i]<t1:
            i+=1
            continue
        else:
            it1=i
            break
    i=len(time)-1
    while True:
        if time[i]>t2:
            i-=1
            continue
        else:
            it2=i
            break

    many=list() #node_index

    for i in range(node_index+1):
        d=dict([('label','CPU System Node '+str(i)),('values',cpu_sys[i][it1:it2])])
        many.append(d)
    #print(many)
    #input()
    for i in range(node_index+1):
        d=dict([('label','CPU User Node '+str(i)),('values',cpu_use[i][it1:it2])])
        many.append(d)
    #print(many)
    #input()

    data=dict([('x',list()),('many',list)])
    data['x']=time[it1:it2]
    data['many']=many

# (x1,y1,label1, y2,label2, y3, label3,plot_title):
#n=len(many)
#many: [(y0),(y1),(y2)..(yn)]
#yn: [('label',labeln) ,('values',y_list))]


    return data

cpu_3par('HPE 3PAR StoreServ Performance Data Collection_rumsk1stg01.zip',0,0)


def vv_3par(zipfn,time1,time2,stats_type):
    time=list()
    read_iops=list()
    read_mbps=list()
    read_msec=list()
    read_blok=list()
    write_iops=list()
    write_mbps=list()
    write_msec=list()
    write_blok=list()
    total_iops=list()
    total_mbps=list()
    total_msec=list()
    total_blok=list()
    data=get_data_from_zip(zipfn,'statvv')
    Lines=data.splitlines()

    for line in Lines:
            words=line.split()
            if len(line)>2 and line[2]==':':
                line=line.rstrip()
                words=line.split()
                time_last=words[1]+' '+words[0]
                time.append(time_last)
            if words!=[] and words[0].isnumeric():
                if words[1]=='r':
                    read_iops.append(int(words[2]))
                    read_mbps.append(int(words[4]))
                    read_msec.append(float(words[6]))
                    read_blok.append(float(words[8]))
                if words[1]=='w':
                    write_iops.append(int(words[2]))
                    write_mbps.append(int(words[4]))
                    write_msec.append(float(words[6]))
                    write_blok.append(float(words[8]))
                if words[1]=='t':
                    total_iops.append(int(words[2]))
                    total_mbps.append(int(words[4]))
                    total_msec.append(float(words[6]))
                    total_blok.append(float(words[8]))
    print(len(Lines),'lines of data processed.')
    print('=======================================================\n')
    print('Start time:',min(time))
    print('End time:',max(time))
    try:
        if time1>min(time): t1=time1
        else: t1=min(time)
    except: t1=min(time)
    try:
        if time2<max(time): t2=time2
        else:t2=max(time)
    except: t2=max(time)

    print('Selected interval:',t1,'to', t2,'\n')
    print('=======================================================')

    fulltime=time
    i=0
    while True:
        if time[i]<t1:
            i+=1
            continue
        else:
            it1=i
            break
    i=len(time)-1
    while True:
        if time[i]>t2:
            i-=1
            continue
        else:
            it2=i
            break

    many=list() #node_index

    if stats_type=='System IOPS':
        d=dict([('label','read_iops'),('values',read_iops[it1:it2])])
        many.append(d)
        d=dict([('label','write_iops'),('values',write_iops[it1:it2])])
        many.append(d)
        d=dict([('label','total_iops'),('values',total_iops[it1:it2])])
        many.append(d)
    elif stats_type=='System MB/sec':
        d=dict([('label','read_mbps'),('values',read_mbps[it1:it2])])
        many.append(d)
        d=dict([('label','write_mbps'),('values',write_mbps[it1:it2])])
        many.append(d)
        d=dict([('label','total_mbps'),('values',total_mbps[it1:it2])])
        many.append(d)
    elif stats_type=='System Response Time':
        d=dict([('label','read_msec'),('values',read_msec[it1:it2])])
        many.append(d)
        d=dict([('label','write_msec'),('values',write_msec[it1:it2])])
        many.append(d)
        d=dict([('label','total_msec'),('values',total_msec[it1:it2])])
        many.append(d)
    elif stats_type=='System IO Size':
        d=dict([('label','read_blok'),('values',read_blok[it1:it2])])
        many.append(d)
        d=dict([('label','write_blok'),('values',write_blok[it1:it2])])
        many.append(d)
        d=dict([('label','total_blok'),('values',total_blok[it1:it2])])
        many.append(d)

    data=dict([('x',list()),('many',list())])
    data['x']=time[it1:it2]
    data['many']=many
    #print(data['many'])

    return data

#vv_3par('HPE 3PAR StoreServ Performance Data Collection_rumsk1stg01.zip',0,0)
