# -*- encoding: utf-8 -*-
# -*- coding: utf-8 -*-
# coding: utf-8

from selenium import webdriver
import lxml.html
import re
import traceback
import sys
import time

CHROMEDRIVER_PATH = "/usr/bin/chromedriver"
SITE_URL='https://sec-sso.click-sec.com/loginweb/'
USER_ID='hogehoge'
PASSWORD='fugafuga'

fr=open(r'/Users/okachan/github.com/market/code_list.txt')
fw=open(r'/Users/okachan/github.com/market/shikihou.txt','w')

def main():
    # GoogleChrome起動
    browser = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH)
    
    # ログイン画面にアクセス
    browser.get(SITE_URL)
    
    # ログイン処理
    uid = browser.find_element_by_id('j_username')
    password = browser.find_element_by_id('j_password')
    uid.send_keys(USER_ID)
    password.send_keys(PASSWORD)
    browser.find_element_by_name('LoginForm').click()
   
    time.sleep(5)
    # ヘッダ書き込み
    fw.write('銘柄コード,銘柄名,株価,決算月,自己資本,自己資本比率,利益剰余金,有利子負債,営業CF,現金同等物,外国人持ち株比率,投信持ち株比率,業績見通し,トピックス\n')
    
    # 証券コード毎にデータ抽出
    for line in fr.readlines():
        scraping(browser,line.rstrip())
    
    fr.close()
    fw.close()

def scraping(browser,code):
    
    # 株式選択
    browser.find_element_by_id('kabuMenu').click()
    time.sleep(3)
    
    # 銘柄コードを入力し検索
    input_code = browser.find_element_by_id('searchKey')
    input_code.send_keys(code)
    browser.find_element_by_id('meigaraSearchButton').click()
    time.sleep(3)
    
    # ////////////////////////////////////////////////// #
    # ----------------  株価データ取得  ---------------- #
    # ////////////////////////////////////////////////// #
    try:
        # 株価情報タブのHTMLソース取得
        root = lxml.html.fromstring(browser.page_source)
        
        # 株価、銘柄名
        meigara_name = root.cssselect('#meigaraNews > tbody > tr > td > span.sect01')[0].text_content()
        price = root.cssselect('#genzaine_front > tbody > tr:nth-child(2) > td.genzai > span.value')[0].text_content().replace(',','')
        
        # ////////////////////////////////////////////////// #
        # ---------------- 四季報データ取得 ---------------- #
        # ////////////////////////////////////////////////// #
        
        # 四季報(概要タブ)選択&HTMLソース取得
        browser.find_element_by_css_selector('li.zi4').click()
        time.sleep(3)
        root = lxml.html.fromstring(browser.page_source)
        
        # 決算月、特色、業績見通し、トピックス、外国人、投信持ち株比率取得
        closing = root.cssselect('#DATA_AREA > div.tab.clearfix > div.toggle_button_body.pdt5.clearfix > div:nth-child(3) > table > tbody > tr:nth-child(1) > td.col2')[0].text_content().replace(',','')
        feature = root.cssselect('#DATA_AREA > div.tab.clearfix > div.toggle_button_body.pdt5.clearfix > div:nth-child(3) > table > tbody > tr:nth-child(4) > td.col2')[0].text_content().replace(',','')
        inspect = root.cssselect('#DATA_AREA > div.tab.clearfix > div.toggle_button_body.pdt5.clearfix > div:nth-child(4) > table > tbody > tr.odd > td.col2')[0].text_content().replace(',','')
        topics = root.cssselect('#DATA_AREA > div.tab.clearfix > div.toggle_button_body.pdt5.clearfix > div:nth-child(4) > table > tbody > tr.even > td.col2')[0].text_content().replace(',','')
        fc_ratio = root.cssselect('#DATA_AREA > div.tab.clearfix > div.toggle_button_body.pdt5.clearfix > div.shikiho_kabunushi > table > tbody > tr:nth-child(12) > td > div:nth-child(1) > span:nth-child(1)')[0].text_content().replace(',','')
        fc_ratio = re.sub(r'\<.*\>\s*','',fc_ratio)
        it_ratio = root.cssselect('#DATA_AREA > div.tab.clearfix > div.toggle_button_body.pdt5.clearfix > div.shikiho_kabunushi > table > tbody > tr:nth-child(12) > td > div:nth-child(2) > span:nth-child(1)')[0].text_content().replace(',','')
        it_ratio = re.sub(r'\<.*\>\s*','',it_ratio)
        
        # 四季報(業績タブ)選択&HTMLソース再取得
        browser.find_element_by_link_text("業績").click()
        time.sleep(3)
        root = lxml.html.fromstring(browser.page_source)
        
        # 自己資本、自己資本比率、利益剰余金、有利子負債、営業CF、現金同等物取得
        jikoshihon = root.cssselect('#DATA_AREA > div.tab.clearfix > div.toggle_button_body.pdt5.clearfix > div.tab_left > div:nth-child(2) > table > tbody > tr:nth-child(3) > td.col2')[0].text_content().replace(',','')
        jikoshihon_ratio = root.cssselect('#DATA_AREA > div.tab.clearfix > div.toggle_button_body.pdt5.clearfix > div.tab_left > div:nth-child(2) > table > tbody > tr:nth-child(4) > td.col2')[0].text_content().replace(',','')
        rieki_jyouyo = root.cssselect('#DATA_AREA > div.tab.clearfix > div.toggle_button_body.pdt5.clearfix > div.tab_left > div:nth-child(2) > table > tbody > tr:nth-child(6) > td.col2')[0].text_content().replace(',','')
        yurishi_husai = root.cssselect('#DATA_AREA > div.tab.clearfix > div.toggle_button_body.pdt5.clearfix > div.tab_left > div:nth-child(2) > table > tbody > tr:nth-child(7) > td.col2')[0].text_content().replace(',','')
        eigyou_cf = re.sub(r'\((\s*\d*)\)','',root.cssselect('#DATA_AREA > div.tab.clearfix > div.toggle_button_body.pdt5.clearfix > div.tab_right > div:nth-child(2) > table > tbody > tr:nth-child(2) > td.col2')[0].text_content().replace(',',''))
        eigyou_cf = re.sub(r'\((\s*\d*)\)','',eigyou_cf)
        genkin_cf = root.cssselect('#DATA_AREA > div.tab.clearfix > div.toggle_button_body.pdt5.clearfix > div.tab_right > div:nth-child(2) > table > tbody > tr:nth-child(5) > td.col2')[0].text_content().replace(',','')
        genkin_cf = re.sub(r'\((\s*\d*)\)','',genkin_cf)
        
        price = price.strip()
        # 取得項目をCSV形式で出力
        info = '{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},{13},{14}\n'.format(code.encode('utf_8'),meigara_name.encode('utf_8'),price.encode('utf_8'),closing.encode('utf_8'),jikoshihon.encode('utf_8'),jikoshihon_ratio.encode('utf_8'),rieki_jyouyo.encode('utf_8'),yurishi_husai.encode('utf_8'),eigyou_cf.encode('utf_8'),genkin_cf.encode('utf_8'),fc_ratio.encode('utf_8'),it_ratio.encode('utf_8'),feature.encode('utf_8'),inspect.encode('utf_8'),topics.encode('utf_8'))
        fw.write(info)
    except:
        print(code)
        print(traceback.format_exc(sys.exc_info()[2]))
        pass

if __name__ == '__main__':
    main()
