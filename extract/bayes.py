#encoding=utf8
import codecs
from copy import deepcopy

class Naive(object):
    
    def __init__(self,debug = True):
        self.debug = debug
        
    def traning(self,samples):
        self.tab = self.calc_init(samples)
        if self.debug:
            self.debug_print(self.tab)
        self.begin = self._count(samples,self.tab,start=1)
        if self.debug:
            self.debug_print(self.begin)
        self.end = self._count(samples,self.tab,start=0)
        if self.debug:
            self.debug_print(self.end)
        
        
    def extract(self,str):
        if self.begin and self.end:
            a,aprob = self.argmax_pi_a(self.begin,str)
            b,bprob = self.argmax_pi_a(self.end,str)
            if self.debug:
                print "begin:%d (%f), end:%d (%f) *** %s" % (a,aprob,b,bprob,str)
            return (a,b)
        else:
            raise Exception("has not yet trained")    
       
         
    def calc_init(self,path):
        symbols = {}
        symbols['^'] = [0,0,0]
        tmp = codecs.open(path,'r','utf-8')
        n = 0
        for line in tmp.readlines():
            arr = line.strip().split(">>>")
            # skip unlabeled data
            if len(arr) != 2:
                continue
            desc  = arr[0].strip()
            n += 1
            for c in desc:
                if c not in symbols:
                    symbols[c] = [0,0,0]
        symbols['$'] = [0,0,0]
        tmp.close()
        return {
                "summary":{
                    "samples":n
                 },
                "symbol":{
                    "total":0,
                    "map":symbols
                 }
               }

    def debug_print(self,tab):
        print "summary:samples=%d,chars=%d" % (tab['summary']['samples'],tab['symbol']['total'])
        print "------------------------------------"
        for k,sym in tab['symbol']['map'].items():
            print "%s=%r" % (k.encode('utf-8'),sym)
            
    #    
    def _count(self,path,samples,start=1):
        symbols = deepcopy(samples)
        f = codecs.open(path,'r','utf-8')
        for line in f.readlines():
            arr = line.strip().split(">>>")
            # skip unlabeled data
            if len(arr) != 2:
                continue
            desc  = arr[0].strip()
            entry = arr[1].strip()
            symbols['symbol']['total'] += len(desc) + 2
            i = -1
            for sym,v in symbols['symbol']['map'].items():
                if sym == '^':
                    i = 0
                elif sym == '$':
                    i = len(desc)+1
                else:
                    tmp = desc.find(sym)
                    i = tmp+1 if tmp!=-1 else -1
                target = desc[ i: i+len(entry)] if start==1 else desc[ i-len(entry)-1:i-1]
                if i > -1:
                    symbols['symbol']['map'][sym][2] += 1
                    if target == entry:
                       symbols['symbol']['map'][sym][0] += 1
                    else:
                       symbols['symbol']['map'][sym][1] += 1
        f.close()
        return symbols
    
    
    def pi(self,samples):
        n = 0
        total = samples['summary']['samples']
        for k,v in samples['symbol']['map'].items():
            n += v[0]
        return float(n)/total
        
    # prob of the given char        
    def pa(self,samples,ch):
        total = samples['summary']['samples']
        tmp = samples['symbol']['map'][ch]
        value = float(tmp[2])/total
        if value == 0:
            print "pa is 0: %s" % ch
        return value

    # prob of the given position
    def pa_i(self,samples,ch):
        _sum = samples['summary']['samples'] #每一个样本只有一个"开始位置" >> total = len(samples)
        if _sum == 0:
            return 0
        return float(samples['symbol']['map'][ch][0])/_sum
   
    # prob of position i which on a given char 
    def pi_a(self,samples,ch):
        _pi = self.pi(samples)
        if _pi == 0:
            return 0
        _pa = self.pa(samples,ch)
        _pa_i = self.pa_i(samples,ch)
        value = _pa_i *  _pi / _pa
        if self.debug:
            print "pi_a = %.3f (ch=%s,pa_i=%.3f,pa=%.3f,pi=%.3f)" % (value,ch.encode('utf-8'),_pa_i,_pa,_pi)
        return value
    
    # 
    def argmax_pi_a(self,samples,line):
        maxp = 0
        i = 0
        line = line.strip()
        # header
        tmp = self.pi_a(samples,'^')
        if tmp > maxp:
            maxp = tmp
            i = 0
        # middle
        m = 0
        for c in line:
            m += 1
            if c not in samples['symbol']['map']:
                print "skip:%s" % c
                continue
            tmp = self.pi_a(samples,c)
            if tmp > maxp:
                maxp = tmp
                i = m
        # tail
        tmp = self.pi_a(samples,'$')
        if tmp > maxp:
            maxp = tmp
            i = len(line)
        return (i,maxp)