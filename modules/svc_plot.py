import re
import sqlite3
from pathlib import Path
import time
import plotly
#from plotly.graph_objs import Scatter, Layout

import plotly.graph_objs
def svc_read_config():
    fn=open('ioplot.cfg','r')
    for line in fh:
        if line.startswith('#') or line=='\n': continue
        line=line.rstrip()
        words=line.split(sep=',')

def svc_c_legend(c):
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

def svc_open_database(dbname):
    try:
        h=open(dbname,'r')
        h.close()
        conn = sqlite3.connect(dbname)
        cur_local = conn.cursor()
        print('Successfully connected to '+dbname)
        return cur_local
    except:
        print('Error openning database. File',dbname,'may not exist. Please check.')
        exit()
    return

def svc_column_names(cur, tname):
    try:
#        print('\nFetching collumn names from', tname)
        cur.execute('PRAGMA TABLE_INFO({})'.format(tname))
    except:
        print('Error getting information on', tabname)
        return False
    data=cur.fetchall()
    cnames=list()
#    print('Table',tname,'contains following columns:')
    for d in data:
        s=str(d[0])+':'+str(d[1])
#        print(s.ljust(15),end=' ')
        cnames.append(d[1])
    return cnames

def svc_select_table(cur):
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

#def svc_column_names(cur, tname):
#    try:
#        print('\nFetching collumn names from', tname)
#        cur.execute('PRAGMA TABLE_INFO({})'.format(tname))
#    except:
#        print('Error getting information on', tabname)
#        return False
#    data=cur.fetchall()
#    cnames=list()
#    print('Table',tname,'contains following columns:')
#    for d in data:
#        s=str(d[0])+':'+str(d[1])
#        print(s.ljust(15),end=' ')
#        cnames.append(d[1])
#        if d[0]%10==0: print('')
#    print('')
#
#    print('')
#    return cnames

def svc_get_sernums(cur,tname):
    cur.execute('SELECT DISTINCT System_SN FROM {tn}'.\
    format (tn=tname))
    data=cur.fetchall()
#    print(data, len(data))
    sernums=[0]*len(data)
#    print(sernums)
    for i in range(len(data)):
        sernums[i]=data[i][0]
    sernums.sort()
#    print('Following serial numbers were found in database:',sernums)
    return sernums

#def get_column(table_name,sernum, column_time,column_name,f_name,f_value):
#    cur.execute('SELECT {t},{cn} FROM {tn} WHERE {fn}=\"{fv}\" AND System_SN=\"{sn}\"'.\
#    format (t=column_time, cn=column_name, tn=table_name, fn=f_name, fv=f_value, sn=sernum))
#    c=cur.fetchall()
#    return c
#    c=dict([('tname',tname),('sernums',sernums),('f_name','id'),('f_value','System_Total'),\
#            ('x','TStamp'),('y1','ro'),('y2','wo'),('y3','rb'),('y4','wb'),('y5','rl'),('y6','wl')])
#    xy1y2y3y4y5y6=svc_plot.svc_get_columns(cur,c,tname,sernums)


def svc_get_columns(cur,c,tname,sernums):
#    c=dict([('tname',tname),('sernums',sernums),('f_name','id'),('f_value','System_Total'),\
#            ('x','TStamp'),('y1','ro'),('y2','wo'),('y3','rb'),('y4','wb'),('y5','rl'),('y6','wl')])
#    xy1y2y3y4y5y6=svc_plot.svc_get_columns(cur,c,tname,sernums)
    cur.execute('SELECT {x},{y1},{y2},{y3},{y4},{y5},{y6} FROM {tn} WHERE {fn}=\"{fv}\"'.\
    format (x=c['x'], y1=c['y1'], y2=c['y2'], y3=c['y3'], y4=c['y4'], y5=c['y5'], y6=c['y6'],\
    tn=c['tname'], fn=c['f_name'], fv=c['f_value']))
    data=cur.fetchall()
    r=dict([('x',list()),('y1',list()),('y2',list()),('y3',list()),('y4',list()),('y5',list()),('y6',list())])
    for i in range(len(data)):
        r['x'].append(data[i][0])
        r['y1'].append(data[i][1])
        r['y2'].append(data[i][2])
        r['y3'].append(data[i][3])
        r['y4'].append(data[i][4])
        r['y5'].append(data[i][5])
        r['y6'].append(data[i][6])
    return r
