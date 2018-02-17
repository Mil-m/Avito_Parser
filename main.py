#import urllib2
from bs4 import BeautifulSoup
#from BeautifulSoup import BeautifulSoup
import requests
from lxml import html
import re
import time

TIME_OUT = 10.0
TIME_OUT_read = 1.0

already_used = ['181.115.241.90:80', '5.2.69.143:1080', '59.127.154.78:80', '54.146.239.185:8118', '66.60.230.23:80',
                '142.165.19.133:80', '170.0.48.14:8080', '190.64.160.100:8080', '201.47.62.130:6666',
                '41.162.77.114:3128', '110.171.186.196:8080', '89.40.113.31:1189', '37.98.226.82:8080',
                '160.202.41.138:8080', '122.154.71.49:8080', '212.63.96.26:8080', '120.198.244.48:9999',
                '120.52.73.173:8080', '189.199.90.196:3128', '149.202.195.236:443', '213.168.37.86:8080',
                '12.27.33.3:8080']

user_agent = ('Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:50.0) ''Gecko/20100101 Firefox/50.0')

def get_proxy():
    global already_used
    proxy_url = 'http://www.ip-adress.com/proxy_list/'
    proxy_list = []
    #is site working
    try:
        r = requests.get(proxy_url)
        html.fromstring(r.content)
    except:
        el, r = get_proxy()
    str = html.fromstring(r.content)
    result = str.xpath("//tr[@class='odd']/td[1]/text()")
    for el in result:
        if (not (el in already_used)):
            return el, r
    #if all proxy in already_used array
    el, r = get_proxy()
    return el, r

def finding_proxy(url, cur_proxy):
    global already_used
    already_used.append(cur_proxy)
    while 1:
        proxy, r = get_proxy()
        try:
            r = requests.get(url, proxies={'https': proxy}, headers={'User-Agent':user_agent}, timeout=(TIME_OUT, TIME_OUT_read))
        except:
            r = ""
        #is response for url is correct
        if (str(r) == "<Response [200]>"):
            print "Success PROXY => ", proxy
            break
        else:
            already_used.append(proxy)
    return r

proxy, _ = get_proxy()
print "Try PROXY => ", proxy

start_url = 'https://www.avito.ru/moskva/kollektsionirovanie/monety'
url_array = [start_url]
for i in range (2, 766):
    url = start_url + "?p=" + str(i)
    url_array.append(url)
print url_array

def get_year(url, f_out_xml):
    result = []

    while 1:
        try:
            r_new = requests.get(url, proxies={'https': proxy}, headers={'User-Agent':user_agent}, timeout=(TIME_OUT, TIME_OUT_read))
        except:
            r_new = finding_proxy(url, proxy)
        if (str(r_new) == "<Response [200]>"):
            break

    soup_new = BeautifulSoup(r_new.text, 'html.parser')
    #str_res = soup_new.prettify()
    #f_out_xml.write(str_res.encode('utf-8'))

    for cl in soup_new.find_all('span'):
        cl_arr = cl.get('class')
        if ((type(cl_arr) is list) and (cl_arr[0] == 'title-info-title-text')):
            list_d = re.findall(r'\d{2}-\d{2}|\d{3}-\d{3}|\d{4}-\d{4}|\d{4}|\d{3}', str(cl))
            if (len(list_d) != 0):
                for el in list_d:
                    if (re.match('\d{4}-\d{4}', str(el))):
                        sp = el.split("-")
                        if (int(str(sp[0])) < 2018):
                            result.append(el)
                    elif (re.match('\d{4}', str(el))):
                        if (int(str(el)) < 2018):
                            result.append(el)
                    else:
                        result.append(el)

    return result

urls_arr = []

def get_years_for_page(page_url, f_out, f_out_xml):
    global urls_arr
    count_known_years = 0
    count_unknown_years = 0

    while 1:
        try:
            r = requests.get(page_url, proxies={'https': proxy}, headers={'User-Agent':user_agent}, timeout=(TIME_OUT, TIME_OUT_read))
        except:
            r = finding_proxy(page_url, proxy)
        if (str(r) == "<Response [200]>"):
            break

    soup = BeautifulSoup(r.text, 'html.parser')

    for link in soup.find_all('div'):
        link_arr = link.get('class')
        if ((type(link_arr) is list) and (link_arr[0] == 'item')):
            for cl in link.find_all('a'):
                class_arr = cl.get('class')
                if ((type(class_arr) is list) and (class_arr[0] == 'item-description-title-link')):
                    new_url = 'https://www.avito.ru' + cl.get('href')
                    if (new_url not in urls_arr):
                        year_list = get_year(new_url, f_out_xml)
                        if (len(year_list) != 0):
                            print ','.join(year_list), " => ", new_url
                            f_out.write(','.join(year_list) + " => " + new_url + "\n")
                            count_known_years += 1
                        else:
                            #print new_url
                            f_out.write(new_url + "\n")
                            count_unknown_years += 1
                        urls_arr.append(new_url)

    return count_known_years, count_unknown_years

f_name_urls = "./urls_new.txt"
f_out = open(f_name_urls, 'a')

f_name_xml = "./out.xml"
f_out_xml = open(f_name_xml, 'a')

global_count_known_years = 0
global_count_unknown_years = 0
for page_url in url_array:
    count_known_years, count_unknown_years = get_years_for_page(page_url, f_out, f_out_xml)
    global_count_known_years += count_known_years
    global_count_unknown_years += count_unknown_years
    print global_count_known_years, global_count_unknown_years, " => ", page_url

print global_count_known_years, global_count_unknown_years
f_out.write("known: " + str(global_count_known_years) + "\n")
f_out.write("unknown: " + str(global_count_unknown_years) + "\n")

f_out_xml.close()
f_out.close()