import time
begin_time=time.time()
import sys
sys.path.append('./modules')
import sqlite3
#import re
import datetime
import argparse
import plotly
from plotly.graph_objs import Scatter, Layout
#import plotly.graph_objs
from pathlib import Path
import os
import shutil
import h3_parse_01 as h_parse

print("This utility crunches array storage statistics and produces nice representation of their total workload.")

def printi(s,msg):
    print(s)
    input('Printed:'+msg)
    return

def printw(s,t):
    print(s)
    time.sleep(t)
    return

def none():
    return

def correct_datetime(f,dt):
#default is YYYY-MM-DD HH:MM
#dt is date/time string
#f format is anything else.
#delimiter may be -,: or /
#    w=dt.split()
#   for dlmtr in ['/','-']
#       dw=w[0].split(dlmtr)
#        if len(dw)>1: break


    return

def get_arg():

    try: parser = argparse.ArgumentParser()
    except: print("Some error happened with arguments")
    parser.add_argument("-s","--storage", help="Storage type: '3par' for HPE 3par Storeserv, 'svc' for IBM SVC/Storwize, 'ntap' for NetApp FAS, 'ds' for IBM DS3/5k")
    parser.add_argument("-f","--filename",help="Filename: specify filename to process")
    parser.add_argument("-o","--output", default='htm', help="Output format: \nchoose \'csv\' for export to CSV file and exit, or \n\'htm\' to produce nice HTML5 interactive graph")
    parser.add_argument("-t1","--time1",help="Start time: specify window start time/date in ""YYYY/MM/DD HH:MM"" format to narrow analysis. Leave blank if not required. Minimum observed time will be used.")
    parser.add_argument("-t2","--time2",help="End time: specify window end time/date in ""YYYY/MM/DD HH:MM"" format to narrow analysis. Leave blank if not required. Maximum observed time will be used.")
    parser.add_argument("-df","--dateformat",default="YYYY-MM-DD",help="You may specify custom date format for correct work of --time1 and --time2 across days boundaries. Default: YYYY-MM-DD")
    parser.add_argument("-l","--log",action="store_true", default=True,help="This option will log all output and error messages to 'error.log'. Turned on by default.")
    parser.add_argument("-sm","--slowmotion",action="store_true",default=False, help="Slow motion. Add 2 sec delays into some standard output messages. Used for debugging. Default is false.")
    try: a=parser.parse_args()
    except:
        print("\nNo arguments. You need to specify something. Use -h option for help.")
        exit()

    #print(a)
    if a.log:
        print('All stderr messages will be redirected to pytrend.err. Check it after program execution.')
        fsock = open('pytrend.err', 'a')
        #sys.stderr = fsock
#        sys.stdout = fsock
        print('Log record time:',datetime.date.today(), time.strftime("%H:%M:%S"))


    if a.filename!=None: print("Looking into this file:",a.filename)
    else:
        print('Use -h option for help.')
        exit()
    if a.storage==None:
        print("\nChoose '-s 3par', '-s svc ' or '-s ntap'. Use -h option for help.\n")
        exit()
    if a.time1!=None:
        td=a.time1.split()
        w=td[1].split(':')
        if len(w[0])==1:a.time1=td[0]+' 0'+td[1]
    if a.time2!=None:
        td=a.time2.split()
        w=td[1].split(':')
        if len(w[0])==1:a.time2=td[0]+' 0'+td[1]

    return a

def save_graph(name):
    ftmp_h=open('temp-plot.html')
    name=name.replace('/','p')
    name=name.replace('second','s')
    name=name.replace('%','ratio')
    shutil.copyfile('temp-plot.html',name)
    return

def prcntl(l,p):
    m=sorted(l)
    i=len(m)
    j=int(round(p/100*i,0))
    return m[j]

def avg(l,i):
    a=round(sum(l)/len(l),i)
    return a

def prod(l,m):
    n=list()
    for i in range(len(l)):
        n[i]=l[i]*m[i]
    return n

def sumprod(l,m):
    s=sum(prod(l,m))
    return s

def plot3csv(x1,y1,label1, y2,label2, y3, label3,plot_title):

    words1=label1.split(',')
    words2=label2.split(',')
    if label3!='': words3=label3.split(',')
#    print(words1, words2, words3)
    header1='Value/Parameter,'+words1[0]+','+words2[0]
    if label3!='': header1=header1+','+words3[0]+'\n'
    else: header1=header1+'\n'
    header2=','+words1[1]+','+words2[1]
    if label3!='': header2=header2+','+words3[1]+'\n'
    else: header2=header2+'\n'
    header3='Maximum,'+str(max(y1))+','+str(max(y2))
    if label3!='':header3=header3+','+str(max(y3))+'\n'
    else: header3=header3+'\n'
    header4='95th percentile,'+str(prcntl(y1,95))+','+str(prcntl(y2,95))
    if label3!='':header4=header4+','+str(prcntl(y3,95))+'\n'
    else: header4=header4+'\n'
    header5='Average,'+str(avg(y1,1))+','+str(avg(y2,1))
    if label3!='':header5=header5+','+str(avg(y3,1))+'\n'
    else: header5=header5+'\n'

    header6='Start time:'+','+str(x1[0])+'\n'
    header7='End time:'+','+str(x1[-1])+'\n'

    print('Preparing CSV representation of',plot_title)
    time.sleep(0.2)

    while True:
        try:
            fcsvh=open(plot_title+'.csv','w')
            break
        except:
            try:
                print("Can not open",plot_title+".csv for write. Perhaps it is in use by another application. Close it and try again")
                input('Press ENTER to continue')
            except:
                print('\nCtrl-C is pressed. Closing application.')
                exit()


    fcsvh.write(plot_title)
    fcsvh.write('\n\n')
    fcsvh.write(header2)
    fcsvh.write(header1)
    fcsvh.write(header3)
    fcsvh.write(header4)
    fcsvh.write(header5)
    fcsvh.write(header6)
    fcsvh.write(header7)
    fcsvh.write('\n\n')
    fcsvh.write(header2)

    if label3!='': fcsvh.write('Time,'+words1[0]+','+words2[0]+','+words3[0]+'\n')
    else:fcsvh.write('Time,'+words1[0]+','+words2[0]+'\n')
    for i in range(len(x1)):
        if label3!='': fcsvh.write(str(x1[i])+','+str(y1[i])+','+str(y2[i])+','+str(y3[i])+'\n')
        else: fcsvh.write(str(x1[i])+','+str(y1[i])+','+str(y2[i])+'\n')

    fcsvh.close()
    print('Results file is  to ',plot_title+'.csv')
    return

def plotmany(x,many,plot_title):
# (x1,y1,label1, y2,label2, y3, label3,plot_title):
#n=len(many)
#many: [(y0),(y1),(y2)..(yn)]
#yn: [('label',labeln) ,('values',y_list))]
    title_long=''
    for y in many:
        #printi(y,'y')
        title_long=title_long+'<BR>'+y['label']+'| 95-percentile='+str(prcntl(y['values'],95))
        title_long=title_long+' | Average='+str(avg(y['values'],1))

    title_long='<b>'+plot_title+'</b>'+title_long

    trace=list()
    for i in range(len(many)):
        trace.append(Scatter(name=many[i]['label'], x=x,y=many[i]['values']))

    printw('Now building graphical representation of '+plot_title,delay)
    printw('Results file will be saved to '+plot_title+'.html',2)
    plotly.offline.plot({
                "data": trace,
                "layout": Layout(title=title_long)})

    try:
        #printw('Trying to save',2)
        save_graph(plot_title+'.html')
    except: printi('Failed autosaving graph to'+plot_title+'. You may try to copy it yourself. Press any key when done.','')

    return


def plot3(x1,y1,label1, y2,label2, y3, label3,plot_title):
#    label1=label1+' '+str(prcntl(y1,99))
#    label2=label2+' '+str(prcntl(y2,99))
#    label3=label3+' '+str(prcntl(y3,99))

    trace1=Scatter(name=label1, x=x1,y=y1)
    trace2=Scatter(name=label2, x=x1,y=y2)
    if label3!='': trace3=Scatter(name=label3, x=x1,y=y3)

    words1=label1.split(',')
    words2=label2.split(',')
    if label3!='': words3=label3.split(',')
#    print(words1, words2, words3)
    title_long='<BR>'+words1[0]+' 95-percentile='+str(prcntl(y1,95))+' '+words1[1]
    title_long=title_long+' | Average='+str(avg(y1,1))+' '+words1[1]
    title_long=title_long+'<BR>'+words2[0]+' 95-percentile='+str(prcntl(y2,95))+' '+words2[1]
    title_long=title_long+' | Average='+str(avg(y2,1))+' '+words2[1]
    if label3!='': title_long=title_long+'<BR>'+words3[0]+' 95-percentile='+str(prcntl(y3,95))+' '+words3[1]
    if label3!='': title_long=title_long+' | Average='+str(avg(y3,1))+' '+words3[1]
    title_long='<b>'+plot_title+'</b>'+title_long

    printw('Now building graphical representation of '+plot_title,delay)
    printw('Results file is saved to '+plot_title+'.html',delay)
    #printw('Launching browser to show results!',delay)

    if label3!='': plotly.offline.plot({
                "data": [trace1,trace2,trace3],
                "layout": Layout(title=title_long)})
    else: plotly.offline.plot({
                "data": [trace1,trace2],
                "layout": Layout(title=title_long)})

    save_graph(plot_title+'.html')

    return



def cpu_3par(fh):
    time=list()
    cpu_sys=dict([(0,list()),(1,list()),(2,list()),(3,list()),(4,list()),(5,list()),(6,list()),(7,list())])
    cpu_use=dict([(0,list()),(1,list()),(2,list()),(3,list()),(4,list()),(5,list()),(6,list()),(7,list())])
    cpu_bus=dict([(0,list()),(1,list()),(2,list()),(3,list()),(4,list()),(5,list()),(6,list()),(7,list())])
    node_index=0
    nodes=list()
    for line in fh:
            if len(line)>2 and line[2]==':':
                #print(line,end='')
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
                cpu_bus[node_index].append(int(words[1])+int(words[2]))
    print('=======================================================\n')
    print('Start time:',min(time))
    print('End time:',max(time))
    try:
        if arg.time1>min(time): t1=arg.time1
        else:t1=min(time)
    except: t1=min(time)
    try:
        if arg.time2<max(time): t2=arg.time2
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

    for i in range(max(nodes)+1):
        if arg.output=='csv':
            plot3csv(time[it1:it2],cpu_use[i][it1:it2],'CPU User, %', cpu_sys[i][it1:it2],'CPU System, %', cpu_bus[i][it1:it2], 'CPU Busy, %','3par CPU Utilization, Node '+str(i))

        elif arg.output=='htm':
               plot3(time[it1:it2],cpu_use[i][it1:it2],'CPU User, %', cpu_sys[i][it1:it2],'CPU System, %', cpu_bus[i][it1:it2], 'CPU Busy, %','3par CPU Utilization, Node '+str(i))

    if arg.output=='csv':
        plot3csv(time[it1:it2],cpu_bus[0][it1:it2],'CPU Busy, Node 0, %', cpu_bus[1][it1:it2],'CPU Busy, Node 1, %',[0]*len(time),'','3par CPU Busy, Nodes')
#    if arg.output=='htm':
#           plot3(time[it1:it2],cpu_bus[0][it1:it2],'CPU Busy, Node 0, %', cpu_bus[1][it1:it2],'CPU Busy, Node 1, %',[0]*len(time),'','3par CPU Busy, Nodes')

    many=list() #node_index

    for i in range(node_index+1):
        d=dict([('label','CPU Busy Node '+str(i)),('values',cpu_bus[i][it1:it2])])
        many.append(d)
    plotmany(time[it1:it2],many,'3Par CPU Busy per Node')

    many=list() #node_index
    for i in range(node_index+1):
        d=dict([('label','CPU System Node '+str(i)),('values',cpu_sys[i][it1:it2])])
        many.append(d)
    plotmany(time[it1:it2],many,'3Par CPU System per Node')

    many=list() #node_index
    for i in range(node_index+1):
        d=dict([('label','CPU User Node '+str(i)),('values',cpu_use[i][it1:it2])])
        many.append(d)
    plotmany(time[it1:it2],many,'3Par CPU User per Node')


# (x1,y1,label1, y2,label2, y3, label3,plot_title):
#n=len(many)
#many: [(y0),(y1),(y2)..(yn)]
#yn: [('label',labeln) ,('values',y_list))]


    return

def vv_3par(fh):
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

    for line in fh:
            words=line.split()
            if len(line)>2 and line[2]==':':
                #print(line,end='')
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

    print('=======================================================\n')
    print('Start time:',min(time))
    print('End time:',max(time))
    try:
        if arg.time1>min(time): t1=arg.time1
        else: t1=min(time)
    except: t1=min(time)
    try:
        if arg.time2<max(time): t2=arg.time2
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
#    print(len(time))
#    print(len(total_iops))
#    print(total_iops[:99])
    if arg.output=='csv':
        plot3csv(time[it1:it2],total_iops[it1:it2],'System Throughput,IOPS', read_iops[it1:it2],'Reads, IOPS', write_iops[it1:it2], 'Writes, IOPS','3par_System_IOPS')
        plot3csv(time[it1:it2],total_mbps[it1:it2],'System Bandwidth,KBPS', read_mbps[it1:it2],'BW Read, KBPS', write_mbps[it1:it2], 'BW Write, KBPS','3par_System_KBPS')
        plot3csv(time[it1:it2],total_msec[it1:it2],'System Service Time,msec', read_msec[it1:it2],'RT Read, msec', write_msec[it1:it2], 'RT Write, msec','3par_System_Service_Time')
        plot3csv(time[it1:it2],total_blok[it1:it2],' Size Xfer,KB', read_blok[it1:it2],'Size Read, KB', write_blok[it1:it2], 'Size Write, KB','3par_System_Block_Size')
    elif arg.output=='htm':
        plot3(time[it1:it2],total_iops[it1:it2],'System Throughput,IOPS', read_iops[it1:it2],'Reads, IOPS', write_iops[it1:it2], 'Writes, IOPS','3par_System_IOPS')
        plot3(time[it1:it2],total_mbps[it1:it2],'System Bandwidth,KBPS', read_mbps[it1:it2],'BW Read, KBPS', write_mbps[it1:it2], 'BW Write, KBPS','3par_System_KBPS')
        plot3(time[it1:it2],total_msec[it1:it2],'System Service Time,msec', read_msec[it1:it2],'RT Read, msec', write_msec[it1:it2], 'RT Write, msec','3par_System_Service_Time')
        plot3(time[it1:it2],total_blok[it1:it2],' Size Xfer,KB', read_blok[it1:it2],'Size Read, KB', write_blok[it1:it2], 'Size Write, KB','3par_System_Block_Size')
    else:
        print(' Nothing is produced. Please specify ''-o csv'' or ''-o htm'' for output type')




    return

def vdisks_svc(c,xy1y2y3y4y5y6):

    total_iops=list()
    total_mbps=list()
    total_msec=list()
    time=xy1y2y3y4y5y6['x']
    read_iops=xy1y2y3y4y5y6['y1']
    write_iops=xy1y2y3y4y5y6['y2']
    for i in range(len(read_iops)):
        total_iops.append(read_iops[i]+write_iops[i])
    read_mbps=xy1y2y3y4y5y6['y3']
    write_mbps=xy1y2y3y4y5y6['y4']
    for i in range(len(read_mbps)):
        total_mbps.append(read_mbps[i]+write_mbps[i])
    read_msec=xy1y2y3y4y5y6['y5']
    write_msec=xy1y2y3y4y5y6['y6']
    for i in range(len(read_msec)):
        total_msec.append(\
        (read_iops[i]*read_msec[i]+write_iops[i]*write_msec[i])/\
        (read_iops[i]+write_iops[i]))
    read_blok=list()
    write_blok=list()
    total_blok=list()

    for i in range(len(read_iops)):
        read_blok.append(int(read_mbps[i]/read_iops[i]))
        write_blok.append(int(write_mbps[i]/write_iops[i]))
        total_blok.append(int(total_mbps[i]/total_iops[i]))


    print('=======================================================\n')
    print('Start time:',min(time))
    print('End time:',max(time))
    try:
        if arg.time1>min(time): t1=arg.time1
        else: t1=min(time)
    except: t1=min(time)
    try:
        if arg.time2<max(time): t2=arg.time2
        else:t2=max(time)
    except: t2=max(time)

    print('Selected interval:',t1,'to', t2,'\n')
    print('=======================================================')

    fulltime=time
    i=0
    while True:
        if str(time[i])<str(t1):
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

    if arg.output=='csv':
        plot3csv(time[it1:it2],total_iops[it1:it2],'Total, IOPS', read_iops[it1:it2],'Reads, IOPS', write_iops[it1:it2], 'Writes, IOPS','SVC-Storwize_System_IOPS')
        plot3csv(time[it1:it2],total_mbps[it1:it2],'Total, KBPS', read_mbps[it1:it2],'BW Read, KBPS', write_mbps[it1:it2], 'BW Write, KBPS','SVC-Storwize_System_KBPS')
        plot3csv(time[it1:it2],total_msec[it1:it2],'Average, msec', read_msec[it1:it2],'Read, msec', write_msec[it1:it2], 'Write, msec','SVC-Storwize_Latency')
        plot3csv(time[it1:it2],total_blok[it1:it2],'Xfer, KB', read_blok[it1:it2],'Read, KB', write_blok[it1:it2], 'Write, KB','SVC-Storwize_System_Block_Size')
    elif arg.output=='htm':
        plot3(time[it1:it2],total_iops[it1:it2],'Total, IOPS', read_iops[it1:it2],'Reads, IOPS', write_iops[it1:it2], 'Writes, IOPS','SVC-Storwize__System_IOPS')
        plot3(time[it1:it2],total_mbps[it1:it2],'Total, KBPS', read_mbps[it1:it2],'Read, KBPS', write_mbps[it1:it2], 'Write, KBPS','SVC-Storwize_System_KBPS')
        plot3(time[it1:it2],total_msec[it1:it2],'Average, msec', read_msec[it1:it2],'Read, msec', write_msec[it1:it2], 'Write, msec','SVC-Storwize_Latency')
        plot3(time[it1:it2],total_blok[it1:it2],'Xfer, KB', read_blok[it1:it2],'Read, KB', write_blok[it1:it2], 'Write, KB','SVC-Storwize_System_Block_Size')
    else:
        print(' Nothing is produced. Please specify ''-o csv'' or ''-o htm'' for output type')
    return

def close_and_clean():
    try: os.remove('temp-plot.html')
    except: pass
    try: os.remove('out.csv')
    except: pass
    try: os.remove('tmp')
    except: pass
    try: os.remove('tmp.json')
    except: pass

    return

#############################################################################
#############################################################################
#                  >>>>>>>>START IS HERE<<<<<<<<<                           #
#############################################################################
#############################################################################
#try:
global delay
time1=0
time2=0
arg=get_arg() #parse command line arguments to get file name
if arg.slowmotion: delay=2
else: delay=0
if arg.storage=='3par':
    printw("3Par module is loaded.",delay)
    printw('Trying to determine stats type.',delay)
    fn=arg.filename
    if arg.time1!=None:
        time1=arg.time1
    if arg.time2!=None:
        time2=arg.time2

    data=h_parse.cpu_3par(fn,time1,time2)
    plotmany(data['x'],data['many'],'CPU Utilization')

    data=h_parse.vv_3par(fn,time1,time2,'System IOPS')
    plotmany(data['x'],data['many'],'System IOPS')

    data=h_parse.vv_3par(fn,time1,time2,'System MB/sec')
    plotmany(data['x'],data['many'],'System MB/Sec')

    data=h_parse.vv_3par(fn,time1,time2,'System IO Size')
    plotmany(data['x'],data['many'],'System IO Size')

    data=h_parse.vv_3par(fn,time1,time2,'System Response Time')
    plotmany(data['x'],data['many'],'System Response Time')

elif arg.storage=='svc':
    try:
        import svc_plot# as iparse
        printw("SVC module is loaded.",delay)
    except:
        printw("SVC module loading error.",delay)
        exit()
    dbname=arg.filename
    printw('Opening '+dbname,delay)
    cur=svc_plot.svc_open_database(dbname)
    #tname=svc_plot.svc_select_table(cur)
    tname='VDisks_new'
    sernums=svc_plot.svc_get_sernums(cur,tname)
    cnames=svc_plot.svc_column_names(cur,tname)
    c=dict([('tname',tname),('sernums',sernums),('f_name','id'),('f_value','System_Total'),\
            ('x','TStamp'),('y1','ro'),('y2','wo'),('y3','rb'),('y4','wb'),('y5','rl'),('y6','wl')])
    xy1y2y3y4y5y6=svc_plot.svc_get_columns(cur,c,tname,sernums)
    vdisks_svc(c,xy1y2y3y4y5y6)

elif arg.storage=='ntap':
    try:
        import netapp_parse_v2 as nparse
        printw("Nparse module is loaded.",delay)
    except:
        print("Nparse module loading error.")
    printw('Opening NetApp autosupport file '+arg.filename,delay)
    nparse.auto_cycle(arg.filename)
    printw('Plotting ',delay)
    data=dict([('x',list()),('many',list())])
    data1=nparse.ntap_out(0,['cifs','nfs','fctot','iscsitot'],'Max')
    data2=nparse.ntap_out(0,['cifs','nfs','fctot','iscsitot'],'Avg')
    data['x']=data1['x']
    data['many']=data1['many']+data2['many']
    plotmany(data['x'],data['many'],'System Protocol IOPS')
    time.sleep(delay)
elif arg.storage=='ds':
    try:
        import ds_parse as lparse
    except:
        print("DS-Series midrange module loading error.")
        exit()
    printw("DS-Series midrange module is loaded.",delay)

    printw("Processing",delay)

    t1=arg.time1
    t2=arg.time2

    data=dict([('x',list()),('many',list())])
    ds_data=lparse.get_data(arg.filename,t1,t2)
    column_names=ds_data['column names']

    data['x']=ds_data['x']
    for i in range(len(column_names)):
        data['many']=list()
        if ('Maximum' in column_names[i]) or ('Total' in column_names[i]): continue
        for ctr in ['CtrA','CtrB','CtrA+B']:
            data['many'].append(ds_data['many'][ctr][i])
        if len(data['many'])>0: plotmany(data['x'],data['many'],column_names[i])

elif arg.storage=='dmx':
    try:
        import ttp_parse as eparse
        printw("TTP module is loaded.",delay)
    except:
        print("TTP module loading error.")
        exit()
elif arg.storage=='ora':
    try:
        import ora_parse as oparse
        printw("Oracle module is loaded.",delay)
    except:
        print("Oracle module loading error.")
        exit()
else: print ('Unknown storage type ','"'+arg.storage+'".','Only 3par/svc/ntap/ds options are supported')

close_and_clean()

end_time=time.time()
run_time=int(round(end_time-begin_time))
if run_time>30: print('Arghh. It took ',run_time,' seconds to finish processing. I am so tired.')
else: print('It took only',run_time,'seconds to finish processing.')
#except: printw('Error in main. Use -l option to log report\n',0.1)
