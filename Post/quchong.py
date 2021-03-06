#coding:utf-8

import pandas as pd
from check_404 import check_404
import os
from util.code_convert import encode_wrap
import time
from selenium import webdriver

from tomorrow import threads
@threads(5)
def quchong_youku(filename):
    try:

        driver = webdriver.Firefox()

        df = pd.read_excel(filename)
        df['Status'] = '跟进中'
        for ix, row in df.iterrows():
            df.ix[ix, 'Status'] = '跟进中' if check_404(row['Href'], driver) else '已删除'
            status =encode_wrap( '排查:{}/{}'.format(ix+1, len(df)))
            print status
            time.sleep(1)

        df.to_excel(filename.replace('.xlsx','')+'(checked).xlsx', index=False)
        driver.quit()
        print 'success'
    except Exception,e:
        print 'Error:', e

def run_quchong():
    dir = 'D:\Data\QuChong\\'

    filenames = []
    for name in os.listdir(dir):
        if os.path.isfile(os.path.join(dir, name)):
            filename = os.path.join(dir,name)
            print filename
            if name.endswith('.xlsx') and 'checked' not in name:
                filenames.append(filename)
                # quchong_youku(filename)

    [quchong_youku(filename) for filename in filenames]

def test():
    url = 'http://www.tudou.com/programs/view/Mtl90fPo8e8/'
    is404 = check_404(url)
    print is404

if __name__ == "__main__":
    # run_quchong()
    test()