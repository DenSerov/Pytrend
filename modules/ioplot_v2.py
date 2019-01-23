import re
import sqlite3
from pathlib import Path
import time
import plotly
from plotly.graph_objs import Scatter, Layout
import plotly.graph_objs

def read_config():
    fn=open('ioplot.cfg','r')
    for line in fh:
        if line.startswith('#') or line=='\n': continue
        line=line.rstrip()
        words=line.split(sep=',')

def c_legend(c):
    st=str(c)
    if c=='ro': st='Read, IOPS'
    elif c=='wo': st='Write, IOPS'
    elif c=='rb': st='Read, MB/sec'
    elif c=='wb': st='Write, MB/sec'
    elif c=='rl': st='Read RT, msec'
    elif c=='wl': st='Write RT, msec'
    elif c=='rq': st='Read, queue'
    elif c=='wq': st='Write, queue'

    return st

def open_database(dbname):
    k=0
    while True:
        try:
            conn = sqlite3.connect(dbname+'.sqlite')
            cur_local = conn.cursor()
            print('Successfully connected to '+dbname+'.sqlite.')
            return cur_local
        except:
            print('Error openning database. Exit.')
            exit()
    return

def column_names(cur, tname):
    try:
        print('\nFetching collumn names from', tname)
        cur.execute('PRAGMA TABLE_INFO({})'.format(tname))
    except:
        print('Error getting information on', tabname)
        return False
    data=cur.fetchall()
    cnames=list()
    print('Table',tname,'contains following columns:')
    for d in data:
        s=str(d[0])+':'+str(d[1])
        print(s.ljust(15),end=' ')
        cnames.append(d[1])
        if d[0]%10==0: print('')
    print('')

#    for d in data:
#         print(str(d[1]).ljust(len(d[1])+1),end=' ')
    print('')
    return cnames

def select_table(cur):
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    print('Database contains following tables:')
    tnames=cur.fetchall()
    for i in range(len(tnames)):
            print(i+1,'-',tnames[i][0])
    k=0
    print(tnames)
    while True:
        print('Select data to scan (',1,'-',i+1,'):',sep='',end='')
        try: j=int(input())
        except: j=0
        if j==0:
            k+=1
            print('Must be number > 0. Attempt',k)
            if k<3: continue
            else: exit()
        try:
            print('You have selected',tnames[j-1][0]+'.')
            break
        except:
            print('Out of range. Try again.')
            continue
    return tnames[j-1][0]

def column_names(cur, tname):
    try:
        print('\nFetching collumn names from', tname)
        cur.execute('PRAGMA TABLE_INFO({})'.format(tname))
    except:
        print('Error getting information on', tabname)
        return False
    data=cur.fetchall()
    cnames=list()
    print('Table',tname,'contains following columns:')
    for d in data:
        s=str(d[0])+':'+str(d[1])
        print(s.ljust(15),end=' ')
        cnames.append(d[1])
        if d[0]%10==0: print('')
    print('')

    print('')
    return cnames

def get_sernums(tname):
    cur.execute('SELECT DISTINCT System_SN FROM {tn}'.\
    format (tn=tname))
    data=cur.fetchall()
#    print(data, len(data))
    sernums=[0]*len(data)
#    print(sernums)
    for i in range(len(data)):
        sernums[i]=data[i][0]
    sernums.sort()
    print('Following serial numbers were found in database:',sernums)
    return sernums

#def get_column(table_name,sernum, column_time,column_name,f_name,f_value):
#    cur.execute('SELECT {t},{cn} FROM {tn} WHERE {fn}=\"{fv}\" AND System_SN=\"{sn}\"'.\
#    format (t=column_time, cn=column_name, tn=table_name, fn=f_name, fv=f_value, sn=sernum))
#    c=cur.fetchall()
#    return c

def get_column(table_name,column_time,column_name,f_name,f_value):
    for sn in sernums:
        cur.execute('SELECT {t},{cn} FROM {tn} WHERE {fn}=\"{fv}\"'.\
        format (t=column_time, cn=column_name, tn=table_name, fn=f_name, fv=f_value))
        data=cur.fetchall()
    return data

#dbname=input('Enter Database name (.sqlite):')
dbname='Storwize'
cur=open_database(dbname)

while True:
    tname=select_table(cur)
    cnames=column_names(cur,tname)
    sernums=get_sernums(tname)
    while True:
        cname=input('Select column #1 to plot or leave blank to choose another table :')
        if cname=='': break
        #f_name=input('Select filter name: ')
        #f_value=input('Select filter value: ')
        f_name='id'
        f_value='System_Total'
        xy=get_column(tname,"TStamp",cname,f_name,f_value)
        axis_x=list()
        axis_y=list()
        for a in xy:
            axis_x.append(a[0])
            axis_y.append(a[1])
        #xy=get_column(tname,sernums[0],"TStamp_sec",cname,f_name,f_value)
        trace1=plotly.graph_objs.Bar(name=c_legend(cname), x=axis_x,y=axis_y)
        print(trace1)

        cname=input('Select column #2 to plot or leave blank to choose another table :')
        if cname=='': break
        #f_name=input('Select filter name: ')
        #f_value=input('Select filter value: ')
        f_name='id'
        f_value='System_Total'
        xy=get_column(tname,"TStamp",cname,f_name,f_value)
        axis_x=list()
        axis_y=list()
        for a in xy:
            axis_x.append(a[0])
            axis_y.append(a[1])
        #xy=get_column(tname,sernums[0],"TStamp_sec",cname,f_name,f_value)
        trace2=Scatter(name=c_legend(cname), x=axis_x,y=axis_y)

        plotly.offline.plot({
            "data": [trace1,trace2],
            "layout": Layout(title='System Total, s/n:'+sernums[0][:-2]+', '+tname[:-4])})
