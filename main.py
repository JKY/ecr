#encoding=utf8
from extract.bayes import Naive as NaiveBayesExtractor

if __name__ == '__main__':   
    extr = NaiveBayesExtractor()
    extr.traning('./data/brand_sample.txt')
    str = u'喜家家加厚透明窗棉被衣物整理袋收纳袋'
    begin,end = extr.extract(str)
    print "品牌:%s" % str[begin:end-1].encode('utf-8')