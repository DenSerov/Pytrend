import re
import time
import json

def mnum(mstr):
    if mstr=='Jan':return '01'
    if mstr=='Feb':return '02'
    if mstr=='Mar':return '03'
    if mstr=='Apr':return '04'
    if mstr=='May':return '05'
    if mstr=='Jun':return '06'
    if mstr=='Jul':return '07'
    if mstr=='Aug':return '08'
    if mstr=='Sep':return '09'
    if mstr=='Oct':return '10'
    if mstr=='Nov':return '11'
    if mstr=='Dec':return '12'
    return '0'

def avg(l,i):
    a=round(sum(l)/len(l),i)
    return a


def netapp_scan(fn):
    fh=open(fn,'r')
    fho=open('tmp','w')
    i=0
    j=0
    filer1n=''
    filer2n=''
    capture_filer=False
    capture_time=True
    start=True
    timelist=list()


    for line in fh:
            i+=1
            if 'FILER_TARGETS' in line:
                filer1n=line.split()[-1][1:line.split()[-1].find(',')]
                filer2n=line.split()[-1][line.split()[-1].find(',')+1:-1]
                filers=(filer1n,filer2n)
            if '=-=-=-=-=-= PERF '+filer1n+' POSTSTATS =-=-=-=-=-= sysstat.out' in line:
                j+=1
                capture_filer=True
                capture_time=True
                filern=filer1n
            if '=-=-=-=-=-= PERF '+filer2n+' POSTSTATS =-=-=-=-=-= sysstat.out' in line:
                #print(j,'Found', filer2n,'at line',i)
                capture_filer=True
                capture_time=False
                filern=filer2n
            if capture_filer:
                if line.startswith('Begin:'):
                    if capture_time:
                        words=line.split()
                        timestr=words[-3]
                        datestr=words[-1]+"/"+mnum(words[-5])+"/"+words[-4]
                        capture_time=False
                        #timelist.append(datestr+'T'+timestr)
                        if start:
                            fho.write(datestr+timestr+' '+filern+' =-=-=-=-=-= PERF '+filer1n+' POSTSTATS =-=-=-=-=-= sysstat.out\n')
                            start=False
                    #else: capture_time=True
                if not capture_time:
                    fho.write(datestr+'T'+timestr+' '+filern+' '+line)

            if line.startswith('PERFSTAT_EPOCH: ') and capture_filer:
                capture_filer=False
                capture_time=False



    fho.close()
    #print(timelist)
    return filers

def ios(w):
    out=dict([('filer',list()),\
    ('cpu_ut',list()),('chit',list()),('totio',list()),\
    ('dkbr',list()),('dkbw',list()),('dkbt',list()),('dskut',list()),\
    ('nfs',list()),('cifs',list()),('fctot',list()),('fcin',list()),('fcout',list()),\
    ('iscsiin',list()),('iscsiout',list()),('iscsitot',list()) ])

    out['filer'].append(w[1])
    out['cpu_ut'].append(w[2])
    out['totio'].append(w[6])
    out['dkbr'].append(w[9])
    out['dkbw'].append(w[10])
    out['dkbt'].append(int(w[9])+int(w[10]))

    return out

def nparse(filers,lio,l,s):
    w=l.split()
    #print(w)
    #input()
    record=dict([('time',list()),('Min', list()),('Avg', list()),('Max', list())])
#    ('cpu_ut',list()),('chit',list()),('totio',list()),\
#    ('dkbr',list()),('dkbw',list()),('dkbt',list()),('dskut',list()),\
#    ('nfs',list()),('cifs',list()),('fctot',list()),('fcin',list()),('fcout',list()),\
#    ('iscsiin',list()),('iscsiout',list()),('iscsitot',list()) ])

    if s=='Min' and w[1]==filers[0]: lio['time'].append(w[0])

#    print(l)
#    for i in range(len(w)):
#        print(i,w[i])
#    print('')

    lio[s]['filer'].append(w[1])
    lio[s]['cpu_ut'].append(int(w[2][:-1]))

    lio[s]['nfs'].append(int(w[3]))
    lio[s]['cifs'].append(int(w[4]))
    lio[s]['fctot'].append(int(w[19]))
    lio[s]['iscsitot'].append(int(w[20]))

    lio[s]['totio'].append(w[6])
    lio[s]['dkbr'].append(w[9])
    lio[s]['dkbw'].append(w[10])
    lio[s]['dkbt'].append(int(w[9])+int(w[10]))
    lio[s]['dskut'].append(int(w[17][:-1]))
    lio[s]['chit'].append(int(w[14][:-1]))

#    print(lio[s].keys())
#    print(lio[s].values())
#    input()

    return lio

def update(lio,s):

    return lio


def netapp_iostat(filers):
    fh=open('tmp','r')
    lio=dict([\
    ('time',list()),('filer names',list()),\
    ('Min', dict([('filer',list()),\
    ('cpu_ut',list()),('chit',list()),('totio',list()),\
    ('dkbr',list()),('dkbw',list()),('dkbt',list()),('dskut',list()),\
    ('nfs',list()),('cifs',list()),('fctot',list()),('fcin',list()),('fcout',list()),\
    ('iscsiin',list()),('iscsiout',list()),('iscsitot',list()) ])),\

    ('Avg', dict([('filer',list()),\
    ('cpu_ut',list()),('chit',list()),('totio',list()),\
    ('dkbr',list()),('dkbw',list()),('dkbt',list()),('dskut',list()),\
    ('nfs',list()),('cifs',list()),('fctot',list()),('fcin',list()),('fcout',list()),\
    ('iscsiin',list()),('iscsiout',list()),('iscsitot',list()) ])),\

    ('Max', dict([('filer',list()),\
    ('cpu_ut',list()),('chit',list()),('totio',list()),\
    ('dkbr',list()),('dkbw',list()),('dkbt',list()),('dskut',list()),\
    ('nfs',list()),('cifs',list()),('fctot',list()),('fcin',list()),('fcout',list()),\
    ('iscsiin',list()),('iscsiout',list()),('iscsitot',list()) ])),\

    ('Tot', dict([('filer',list()),\
    ('cpu_ut',list()),('chit',list()),('totio',list()),\
    ('dkbr',list()),('dkbw',list()),('dkbt',list()),('dskut',list()),\
    ('nfs',list()),('cifs',list()),('fctot',list()),('fcin',list()),('fcout',list()),\
    ('iscsiin',list()),('iscsiout',list()),('iscsitot',list()) ])),\
    ])


    cap_avg=False
    cap_min=False
    cap_max=False
    lio['filer names']=filers
    for l in fh:
        w=l.split()
        if len(w)==2: continue

        if cap_min:
            cap_min=False
            lio=nparse(filers,lio,l,'Min')
        if cap_avg:
            cap_avg=False
            lio=nparse(filers,lio,l,'Avg')
        if cap_max:
            cap_max=False
            lio=nparse(filers,lio,l,'Max')

        if w[2]=='Min': cap_min=True
        if w[2]=='Avg': cap_avg=True
        if w[2]=='Max': cap_max=True


    return lio

def get_yn(data,filer_index,ylabel,stat):

    yn=dict([('label',str()), ('values',list())])
    if filer_index>=0:
        yn['label']='F'+str(filer_index)+' '+ylabel+'-'+stat
    else:
        yn['label']='System'+' '+ylabel+'-'+stat
    nintervals=len(data['time'])
    nfilers=len(data['filer names'])

    if filer_index>=0:
        for i in range(nintervals):
            yn['values'].append(data[stat][ylabel][i*nfilers+filer_index])
    elif filer_index<0:
        for i in range(nintervals):
            yn['values'].append(data[stat][ylabel][i])
    return yn

def get_x(data):
    x=data['time']
    return x

def ntap_out(filer_i,list_of_values,stats_type):
#plotmany(x,many,plot_title):
# (x1,y1,label1, y2,label2, y3, label3,plot_title):
#n=len(many)
#many: [(y0),(y1),(y2)..(yn)]
#yn: [('label',labeln) ,('values',y_list))]
    if stats_type!='Tot' and filer_i<0:
        print('Warning! Total values are valid only for all filers. You specified filer',filer_i,'and stats_type',stats_type)
        print('Produced data is garbage')
        return
    elif stats_type=='Tot' and filer_i>=0:
        print('Warning! Total values are valid only for all filers. You specified filer',filer_i,'and stats_type',stats_type)
        print('Produced data is garbage')
        return

    j=open('tmp.json').read()
    liostat=json.loads(j)
    x=get_x(liostat)
    many=list()
    for label in list_of_values:
        many.append(get_yn(liostat,filer_i,label,stats_type))
    ndict=dict([('x',x),('many',many)])
    return ndict

def auto_cycle(f_name):
    t_start=time.time()
    filers=netapp_scan(f_name)
    nfilers=len(filers)
    liostat=netapp_iostat(filers)

    for c in liostat['Avg']:
        nr_entries_per_filer=int(len(liostat['Avg'][c])/nfilers)
        for j in range(nr_entries_per_filer):
            if c=='cpu_ut': a=avg([liostat['Avg'][c][j*2],liostat['Avg'][c][j*2+1]],1)
            elif c=='chit': a=avg([liostat['Avg'][c][j*2],liostat['Avg'][c][j*2+1]],1)
            elif c=='dskut':a=avg([liostat['Avg'][c][j*2],liostat['Avg'][c][j*2+1]],1)
            elif c=='filer':a=liostat['Avg'][c][j*2][:-1]+'-total'
            else: a=int(liostat['Avg'][c][j*2])+int(liostat['Avg'][c][j*2+1])
            liostat['Tot'][c].append(a)

    print('Autocycle '+f_name+'is processed.')
    j=json.dumps(liostat)
    f=open("tmp.json","w")
    f.write(j)
    f.close()
    print('Finished scanning Autosupport in',int(time.time()-t_start),'seconds')

    print('=======================================================\n')
    print('Start time:',min(liostat['time']))
    print('End time:',max(liostat['time']))
    try:
        if arg.time1>min(liostat['time']): t1=arg.time1
        else:t1=min(liostat['time'])
    except: t1=min(liostat['time'])
    try:
        if arg.time2<max(liostat['time']): t2=arg.time2
        else:t2=max(liostat['time'])
    except: t2=max(liostat['time'])
    print('Selected interval:',t1,'to', t2,'\n')
    print('=======================================================')



    return
