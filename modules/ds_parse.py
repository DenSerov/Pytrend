import csv
import zipfile
import time
#import pandas

def extract_csv(fname):
    print('Extracting data from',fname)
    zip=zipfile.ZipFile(fname)
    w=fname.split('.')
    stat_fname=w[0]+'/'+'dsquick_performanceStats.csv'
    f=zip.open(stat_fname)
    contents=f.read()
    names=zip.namelist()
    content_csv=contents.decode()
    fo=open('out.csv','wb')
    fo.write(contents)
    fo.close()
    time.sleep(0.2)
    print('Done.')
    return fo

def get_iops(f):
    print('Getting IOPS from',f)
    data=input('Data? ')
    return data

def get_datetime(l,datetime):
    w=l.split(',')
    w=w[0].split()
    datestr=w[1]
    timestr=w[2]
    pmstr=w[3]
    PM=False

    if pmstr=='PM"': PM=True
    w=datestr.split('/')
    if len(w[0])<2:w[0]='0'+w[0]
    if len(w[1])<2:w[1]='0'+w[1]
    date=w[2]+'/'+w[0]+'/'+w[1]
    w=timestr.split(':')
    if PM:
        w[0]=str( int(w[0])+12 )
        timestr=w[0]+':'+w[1]+':'+w[2]
    elif w[0]=='12': w[0]='00'
    if len(w[0])<2:w[0]='0'+w[0]
    timestr=w[0]+':'+w[1]+':'+w[2]
    datetime.append(date+'T'+timestr)
    return

def get_column_names(l):
    words=l.split(',')
    column_names=list()
    for w in words[1:-1]:
        column_names.append(w[1:-1])
    column_names.append(words[-1][1:-2])
    for i in range(len(column_names)):
        column_names[i]=column_names[i].rstrip()
        column_names[i]=column_names[i].lstrip()


    return column_names

def get_controller(l,col,ctrab_stat,ab):
    words=l[:-1].split(',')
    for i in range(0,len(col)-1):
        ctrab_stat[col[i]].append(float(words[i+1][1:-1]))

    try:
        i=col.index('Current MB/second')
        K=1024
    except:
        i=col.index('Current KB/second')
        K=1
    j=col.index('Current IO/second')
    k=col.index('Current IO size KB')
    if float(ctrab_stat[col[j]][-1])>0:
        ctrab_stat[col[k]].append(int(float(ctrab_stat[col[i]][-1])/float(ctrab_stat[col[j]][-1])*K))
    else:
        ctrab_stat[col[k]].append(0)

    return ctrab_stat

def get_totals(l,col,total_stat):
    words=l[:-1].split(',')

    for i in range(0,len(col)-1):
        total_stat[col[i]].append(float(words[i+1][1:-1]))
    try:
        i=col.index('Current MB/second')
        K=1024
    except:
        i=col.index('Current KB/second')
        K=1

    j=col.index('Current IO/second')
    k=col.index('Current IO size KB')
    if float(total_stat[col[j]][-1])>0:
        total_stat[col[k]].append(int(float(total_stat[col[i]][-1])/float(total_stat[col[j]][-1])*K))
    else:
        total_stat[col[k]].append(0)


    return

def get_logical_drive(l,col,ldrives):
    return

def get_yn(ab,label,stat):
    yn=dict([('label',str()), ('values',list())])
    yn['label']=ab+' '+label
    yn['values']=stat[label]
    return yn

def get_data(fn,t1,t2):
    fo=extract_csv(fn)
    fo=open(fo.name,'r')
    datetime=list()
    ldrives=list()
    total_stat={}
    ctra_stat={}
    ctrb_stat={}
    ldrv_stat={}

    for l in fo:
        if len(l)<2: continue
        if l.startswith('"Storage Subsystems'):
            col=get_column_names(l)
            col.append('Current IO size KB')
            print('Added bonus stat: "Current IO size KB". It is calculated based on IOPS and Bandwidth data.')
            for c in col:
                total_stat[c]=list()
                ctra_stat[c]=list()
                ctrb_stat[c]=list()
                ldrv_stat[c]=list()
            #print(col)
            #input()
        if l.startswith('"Date/Time:'): get_datetime(l,datetime)
        if l.startswith('"CONTROLLER IN SLOT A'): ctra_stat=get_controller(l,col,ctra_stat,'A')
        if l.startswith('"CONTROLLER IN SLOT B'): ctrb_stat=get_controller(l,col,ctrb_stat,'B')
        if l.startswith('"STORAGE SUBSYSTEM TOTALS'): get_totals(l,col,total_stat)
        if l.startswith('"Logical Drive'): get_logical_drive(l,col,ldrives)

    many=dict([('CtrA',list()),('CtrB',list()),('CtrA+B',list())])
    for label in col:
        many['CtrA'].append(get_yn('CtrA',label,ctra_stat))
        many['CtrB'].append(get_yn('CtrB',label,ctrb_stat))
        many['CtrA+B'].append(get_yn('CtrA+B',label,total_stat))

    data=dict([('x',datetime),('many',many),('column names',col)])


    return data

#    yn=dict([('label',str()), ('values',list())])
#    many.append( dict([('label','CTRA Current IO/second'),('values',ctra_stat['Current IO/second'])]) )
#    print(many)
#    input('CTRA done')
#    many.append( dict([('label','CTRB Current IO/second'),('values',ctrb_stat['Current IO/second'])]) )
#    print(many)
#    input('CTRB done')
#    many.append( dict([('label','Total Current IO/second'),('values',total_stat['Current IO/second'])]) )
#    print(many)
#    input('Total done')
#    yn['label']=''
#    yn['values']=

#data=get_data('ibmquick_5020ARB.zip',0,0)
#print(data['x'])
#input()

#for d in data['total']:
#print(data['total']['Read %'])
#input()


#for i in range(len(ctra_stat['Read %'])):
#    print(i,datetime[i],ctra_stat['Read %'][i],ctrb_stat['Read %'][i])
