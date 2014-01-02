#encoding=utf8
import codecs
from copy import deepcopy

# 使用朴素贝叶斯算法在商品名称中提取品牌,
# 定理参见: http://zh.wikipedia.org/wiki/贝叶斯定理
# 思路:
#    将品牌名看作是有由<起点a,终点b>组成
#    使用样本生成字典, 分别计算给定字符串中每一个样本字符后面是起点,终点的概率, 取使概率最大的那个字符
#    通过a,b截取品牌名
class Naive(object):
    
    def __init__(self,debug = True):
        self.debug = debug
        
    # "起点"统计, "终点"统计
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
        
    # 根据训练样本提取给定字符串的商品名    
    def extract(self,str):
        if self.begin and self.end:
            a,aprob = self.argmax_pi_a(self.begin,str)
            b,bprob = self.argmax_pi_a(self.end,str)
            if self.debug:
                print "begin:%d (%f), end:%d (%f) *** %s" % (a,aprob,b,bprob,str)
            return (a,b)
        else:
            raise Exception("has not yet trained")    
       
    # 初始化计数表     
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
            
    # 调试输出 统计表
    def debug_print(self,tab):
        print "summary:samples=%d,chars=%d" % (tab['summary']['samples'],tab['symbol']['total'])
        print "------------------------------------"
        for k,sym in tab['symbol']['map'].items():
            print "%s=%r" % (k.encode('utf-8'),sym)
            
    # 统计样本中字符前(后) 出现(品牌名), 不出现(品牌) 的次数  
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
    
    # 出现品牌名的概率
    # 实际应用中这个不需要, 每个分母都同除这个参数, 具体值不影响结果
    def pi(self,samples):
        n = 0
        total = samples['summary']['samples']
        for k,v in samples['symbol']['map'].items():
            n += v[0]
        return float(n)/total
        
    # 出现给定字符的概率        
    def pa(self,samples,ch):
        total = samples['summary']['samples']
        tmp = samples['symbol']['map'][ch]
        value = float(tmp[2])/total
        if value == 0:
            print "pa is 0: %s" % ch
        return value

    # 出现品牌名并且包含给定字符的概率
    def pa_i(self,samples,ch):
        _sum = samples['summary']['samples'] #每一个样本只有一个"开始位置" >> total = len(samples)
        if _sum == 0:
            return 0
        return float(samples['symbol']['map'][ch][0])/_sum
   
    # 给定字符出现品牌名的概率 
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
    
    # 计算使pi_a最大的字符
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