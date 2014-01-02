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
    extr = NaiveBayesExtractor()
    extr.traning('./data/brand_sample.txt')
    str = u'sdsdsdafa'
    lines = load_test('./data/brand_test.txt')
    sum = len(lines)
    error = 0
    for str,entry in lines:
        begin,end = extr.extract(str)
        result = str[begin:end-1]
        print "品牌:%s" % result.encode('utf-8')
        if entry != result:
            error += 1
    print "total:%d,error=%d,er=%f" % (sum,error,float(error)/sum)