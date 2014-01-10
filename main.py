#encoding=utf8
from extract.bayes import Naive as NaiveBayesExtractor
import codecs

def load_test(path):
    lines = []
    f = codecs.open(path,'r','utf-8')
    for line in f.readlines():
        arr = line.strip().split(">>>")
        # skip unlabeled data
        if len(arr) != 2:
            continue
        desc  = arr[0].strip()
        entry = arr[1].strip()
        lines.append((desc,entry))
    f.close()
    return lines
           

if __name__ == '__main__': 
    '''  
    s = u"阿札AZA女包2013新款复古镂空撞色拼接刺绣邮差手提斜挎女包 9871 爱丁堡蓝"
    extr = NaiveBayesExtractor()
    extr.traning("./data/brand_sample.txt")
    begin,end = extr.extract(s)
    result = s[begin:end]
    print "品牌:%s" % result.encode("utf-8")
    exit()       
    ''' 

    
    extr = NaiveBayesExtractor(debug=False,begin_tab = "./data/begin.txt",end_tab = "./data/end.txt")
    extr.traning("./data/brand_sample.txt")
    lines = load_test("./data/brand_test.txt")
    
    str = u'阿札AZA女包2013新款复古镂空撞色拼接刺绣邮差手提斜挎女包 9871 爱丁堡蓝'
    begin,end = extr.extract(str)
    result = str[begin:end]
    print "[%d,%d]" % (begin,end)
    print "品牌:%s <<< %s" % (result.encode('utf-8'),str.encode('utf-8'))
    exit()
            
    sum = len(lines)
    error = 0
    error_f = codecs.open("./data/err.txt","w","utf-8")
    for str,entry in lines:
        begin,end = extr.extract(str)
        result = str[begin:end]
        print "品牌:%s <<< %s" % (result.encode('utf-8'),str.encode('utf-8'))
        if entry != result:
            error += 1
        #    print "ERROR:%s vs %s, *** %s" % (entry,result,str)
            error_f.write(str + " *** " + entry + " --- " +  result + "\n")
    error_f.close()
    print "total:%d,error=%d,er=%f" % (sum,error,float(error)/sum)
    