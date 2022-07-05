# -- coding: UTF-8 --
from pypinyin import lazy_pinyin#用pip安装
from lxml import etree
from urllib.request import urlopen
import pandas as pd
import requests
import difflib
import json
import numpy as np
import re
import os
import time
import urllib
import json
import math
import sys
import telnetlib
requests.adapters.DEFAULT_RETRIES = 5 # 增加重连次数
s = requests.session()
s.keep_alive = False # 关闭多余连接


# 测试ip有效性
def test_ip(ip, port):
    try:
        telnetlib.Telnet(ip, port, timeout=10)
        ip_df = ip
        port_df = port
    except:
        ip_df = ''
        port_df = ''
    return ip_df, port_df


# 切换代理IP
def get_random_ip():  # https://www.kuaidaili.com/free/,F12,Network,free,header

    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36"
    cookie = "channelid=0; sid=1607585126661398; _ga=GA1.2.1493413631.1607585504; _gid=GA1.2.854914987.1608895819; Hm_lvt_7ed65b1cc4b810e9fd37959c9bb51b31=1607585504,1607701137,1608895819; _gat=1; Hm_lpvt_7ed65b1cc4b810e9fd37959c9bb51b31=1608895892"
    headers = {"User-Agent": user_agent, "Cookie": cookie}
    url = 'https://www.kuaidaili.com/free/intr/' + str(np.random.randint(1, 5)) + '/'
    req = requests.get(url, headers=headers)
    ip_list = re.findall('<td data-title="IP">(.+?)</td>', req.text, re.S)
    port_list = re.findall('<td data-title="PORT">(.*?)</td>', req.text, re.S)
    ip_sum = []
    port_sum = []
    for i in range(len(ip_list)):
        ip_i = ip_list[i]
        port_i = port_list[i]
        ip_df, port_df = test_ip(ip_i, port_i)
        ip_sum.append(ip_df)
    ip_realist = [j for j in ip_sum if j != '']
    if len(ip_realist) > 1:
        target_ip = ip_realist[np.random.randint(1, len(ip_realist))]
        print('代理IP有效')
        print(target_ip)
    elif len(ip_realist) == 1:
        target_ip = ip_realist[0]
        print('代理IP有效')
        print(target_ip)
    else:
        print('代理IP无效')
        target_ip = '192.168.34.48'  # 本地
    proxies = {'https': target_ip}  # 高德为https协议
    return proxies

#8684公交线路及站点获取（分类爬）
def get_line(city, use_proxies=False):
    if os.path.exists(path+"\\"+city+'.csv'):
        return 1
    city_namepy=''.join(lazy_pinyin(city))[:-3]#注意这里[:-3]表示取'南京'两个字#lazy_pinyin-中文转拼音
    url='https://'+city_namepy+'.8684.cn/'
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36"
    cookie="UM_distinctid=17619904f4928c-0c34b20984aea-6373664-144000-17619904f4a3e7; guid=6db1-67b4-8b86-98a2; cna=ajsgFzwQnGsCAXoEdTB9uH2O; x5sec=7b22617365727665723b32223a223066303630303737343836343236343765343236663936633661383537633837434c2f3578663446454962472f715849774d6d532f41453d227d; isg=BEZGJZiZZYD3xzFkG_43jYlHlzzIp4ph-vRaRjBqSGlEM-pNlTercCCCC2__nYJ5; tfstk=ckT5By6NF82SFhoUzQGVTHVDyiQGaJDfi06JN30z8X6aS0dcHsA_7OihJH20kGCf.; l=eBaLPz8VODchLK2KBO5BKurza77TXCOXGrVzaNbMiInca6_P_Fi2qNQ2hGkX8dtjgtfLQEKyIQLleRCUl3UdNxDDBeA1tTf5AYp9-"
    headers={"User-Agent":user_agent,"Cookie":cookie}
    if use_proxies:
        ip=get_random_ip()
        req = requests.get(url, headers=headers, proxies=ip, timeout=20)
    else:
        req = requests.get(url, headers=headers)
    req.encoding=req.apparent_encoding
    text=req.text
    line_type=re.findall('<a href="/line(.*?)">(.*?)</a>',text,re.S)
    line_sum=pd.DataFrame()
    for j in range(len(line_type)):
        print('爬取{}{}'.format(city, line_type[j][1]))
        req1=requests.get(url+'/line'+line_type[j][0],headers=headers)
        line_list=re.findall('<a href="/x_.*?" title=.*?>(.*?)</a>',req1.text,re.S)
        line_id=re.findall('<a href="/x_(.*?)" title=.*?>.*?</a>',req1.text,re.S)#线路名称 如['1路', '2路', '3路支线', '3路', '4路']
        for a in range(len(line_id)):
            req2=requests.get(url+'/x_'+line_id[a],headers=headers)#线路名称的url
            line_dir=re.findall('<div class="trip".*?>(.*?)</div>',req2.text,re.S)#线路方向direction 如['电子产业园—凤凰湖', '凤凰湖—电子产业园']
            if len(line_dir)==2:
                line_dir_f=line_dir[0].split('—')[1]
                targetline_stop=re.findall('<a href="/z_.*?">(.*?)</a>',req2.text,re.S)
                try:
                    line_dir_f_index=targetline_stop.index(line_dir_f)
                except:
                    # sim=difflib.get_close_matches(line_dir_f,targetline_stop,1,0.1)
                    # line_dir_f_index=targetline_stop.index(sim[0])
                    try:
                        sim=difflib.get_close_matches(line_dir_f,targetline_stop,1,0.1)
                        line_dir_f_index=targetline_stop.index(sim[0])
                    except:
                        for kk in range(len(targetline_stop)):
                            if targetline_stop[kk]==targetline_stop[kk+1]:
                                line_dir_f_index = kk
                                break
                targetline_f_stop=targetline_stop[:line_dir_f_index+1]
                targetline_b_stop=targetline_stop[line_dir_f_index+1:]
                f_line=pd.DataFrame({'站点':targetline_f_stop})
                f_line['方向']=line_dir[0]
                b_line=pd.DataFrame({'站点':targetline_b_stop})
                b_line['方向']=line_dir[1]
                targetline_df=pd.concat([f_line,b_line],axis=0,ignore_index=False)
                targetline_df['线路名']=line_list[a]
                targetline_df['分类']=line_type[j][1]
                targetline_df['城市']=city

            else:
                targetline_stop=re.findall('<a href="/z_.*?">(.*?)</a>',req2.text,re.S)
                targetline_df=pd.DataFrame({'站点':targetline_stop})
                targetline_df['方向']=line_dir[0]
                targetline_df['线路名']=line_list[a]
                targetline_df['分类']=line_type[j][1]
                targetline_df['城市']=city
            line_sum=pd.concat([line_sum,targetline_df],axis=0,ignore_index=False)
    line_sum=line_sum.reset_index().rename(columns={'index':'序号'})
    line_sum=line_sum[['城市','分类','线路名','方向','序号','站点']]
    line_sum.to_csv(path+"\\"+city+'.csv',index=False,encoding='utf_8_sig')
    return line_sum


# 坐标转换
# 公交坐标信息转化
x_pi = 3.14159265358979324 * 3000.0 / 180.0
pi = 3.1415926535897932384626  # π
a = 6378245.0  # 长半轴
ee = 0.00669342162296594323  # 扁率


def gcj02towgs84(lng, lat):
    """
    GCJ02(火星坐标系)转GPS84
    :param lng:火星坐标系的经度
    :param lat:火星坐标系纬度
    :return:
    """
    if out_of_china(lng, lat):
        return lng, lat
    dlat = transformlat(lng - 105.0, lat - 35.0)
    dlng = transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return [lng * 2 - mglng, lat * 2 - mglat]


def transformlat(lng, lat):
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
          0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * pi) + 40.0 *
            math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * pi) + 320 *
            math.sin(lat * pi / 30.0)) * 2.0 / 3.0
    return ret


def transformlng(lng, lat):
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
          0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * pi) + 40.0 *
            math.sin(lng / 3.0 * pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * pi) + 300.0 *
            math.sin(lng / 30.0 * pi)) * 2.0 / 3.0
    return ret


def out_of_china(lng, lat):
    """
    判断是否在国内，不在国内不做偏移
    :param lng:
    :param lat:
    :return:
    """
    if lng < 72.004 or lng > 137.8347:
        return True
    if lat < 0.8293 or lat > 55.8271:
        return True
    return False


def coordinates(c):
    lng, lat = c.split(',')
    lng, lat = float(lng), float(lat)
    wlng, wlat = gcj02towgs84(lng, lat)
    return wlng, wlat


# 利用8684公交线路，借助高德API爬取公交线路对应站点名、站点坐标及沿线经纬度
# 此前采用前端抓包的方法已失效,也可用selenium及browsermobproxy爬取，绕过高德验证码检测
def get_polyst(city, line, key_value='559bdffe35eec8c8f4dae959451d705c',
               use_proxies=False):  # a5b7479db5b24fd68cedcf24f482c156,559bdffe35eec8c8f4dae959451d705c
    key = key_value
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36"
    cookie = "UM_distinctid=17619904f4928c-0c34b20984aea-6373664-144000-17619904f4a3e7; cna=ajsgFzwQnGsCAXoEdTB9uH2O; guid=ab44-351b-e977-a799; xlly_s=1; passport_login=NDM1MTE0NzIwLGFtYXBfMTM4NTQyOTU5NTBDcWlRekFsSWMsbW0yYnR4a3lhNHlhZnlpcnVrcDJmYWFwbXlsaHplbGgsMTYwODgyMzg0NSxOREJpWmprMlpXTmpOVGhrWVdJd01HWmlPV1JsWVRSak1qTTRPRFptWldJPQ%3D%3D; isg=BOLiWF_aydl9w9WF7lmJgTj0M2hEM-ZNPig-8ix7hNUA_4J5FMLtXW12LzsDb17l; l=eBSPaa8eO5gCiGc-BO5aPurza77TnIRb4sPzaNbMiInca6ah9FaWdNQ22-t6WdtjgtC3uetyIQLleRLHR3Ap9xDDBy7i_2Qr3xvO.; tfstk=cafGBVONfOJ6gbvhF5O1r80bLbedaCwwfs5FT6NFJbDl1cj97s0ILY88YyxOjsHf."
    headers = {"User-Agent": user_agent, "Cookie": cookie}
    url = 'https://restapi.amap.com/v3/bus/linename?s=rsv3&extensions=all&key=' + key + '&output=json&city={}&offset=2&keywords={}&platform=JS'.format(
        city, line)
    if use_proxies:
        ip = get_random_ip()
        response = requests.get(url, headers=headers, proxies=ip, timeout=20)
    else:
        response = requests.get(url, headers=headers)
    message_dict = json.loads(response.text)
    try:
        if message_dict['buslines']:
            if len(message_dict['buslines']) == 0:  # 有名称没数据
                print('{}线路无数据'.format(line))
            else:
                stops_sum = []
                for i in range(len(message_dict['buslines'])):
                    stops = {}
                    stops['线路名'] = message_dict['buslines'][i]['name']
                    stops['沿线经纬度'] = message_dict['buslines'][i]['polyline']
                    st_name = []
                    st_coords_x = []
                    st_coords_y = []
                    st_sequence = []
                    for st in message_dict['buslines'][i]['busstops']:
                        st_name.append(st['name'])
                        st_coords_x.append(st['location'].split(',')[0])
                        st_coords_y.append(st['location'].split(',')[1])
                        st_sequence.append(st['sequence'])

                    stops['序号'] = st_sequence
                    stops['站点'] = st_name
                    stops['经度'] = st_coords_x
                    stops['纬度'] = st_coords_y
                    stops_sum.append(stops)
                data_df = pd.DataFrame(stops_sum)
                all_data = data_df.reindex(data_df.index.repeat(data_df['序号'].str.len())).reset_index(drop=True)
                all_data = all_data.assign(序号=np.concatenate(data_df['序号'].values),
                                           站点=np.concatenate(data_df['站点'].values),
                                           经度=np.concatenate(data_df['经度'].values),
                                           纬度=np.concatenate(data_df['纬度'].values))
                #all_data = all_data[['线路名','序号','站点','经度','纬度']]
                line_data = all_data.iloc[:, :6].drop_duplicates('沿线经纬度').reset_index(drop=True)
                #line_data['线路名'] = all_data['线路名']
                st_data = all_data.drop('沿线经纬度', axis=1)
                line_data = line_data[['线路名', '沿线经纬度']]
                lin_data = np.array(line_data.iloc[:,:])
                d_data = []
                for ii in range(len(lin_data)):
                    a = lin_data[ii,0]
                    b = lin_data[ii,1]
                    bb = b.split(";")
                    for jj in bb:
                        c = []
                        c.append(a)
                        cc = jj.split(",")
                        c.extend(cc)
                        d_data.append(c)
                dd_data = pd.DataFrame(d_data)
                dd_data.columns = ['线路名', '经度', '纬度']
                print('{}已完成'.format(line))
        else:
            print('{}线路无数据'.format(line))
            line_data = pd.DataFrame()
            st_data = pd.DataFrame()
            dd_data = pd.DataFrame()
    except:
        print('{}线路无数据'.format(line))
        line_data = pd.DataFrame()
        st_data = pd.DataFrame()
        dd_data = pd.DataFrame()
    return dd_data, st_data


if __name__ == '__main__':
    start=time.time()
    city = '滁州市'#input('需要爬取的公交线路所在城市:' )
    path = './公交线路'#input('公交线路文件存储路径:' )
    path2 = './公交沿线坐标'#input('公交沿线坐标文件存储路径:')
    if not os.path.exists(path):
        os.makedirs(path)
    if not os.path.exists(path2):
        os.makedirs(path2)
    get_line(city)
    f = open(path + "\\" + city + '.csv', encoding="utf-8")
    data = pd.read_csv(f)
    limit_requests = 2000
    city_name = data['城市'].iloc[0]
    lines = list(data['线路名'].unique())
    path_data1 = path2 + "\\" + city_name + '公交沿线坐标数据.csv'
    path_data2 = path2 + "\\" + city_name + '公交站点坐标数据.csv'
    # 公交站点及沿线坐标爬取主程序
    # 打开8684爬取的数据文件
    if not os.path.exists(os.path.join(path_data1)):
        print('从第一个线路开始')
        num = 0
        origin_line_data = pd.DataFrame()
        origin_stop_data = pd.DataFrame()
        line_list = lines
    else:
        f1 = open(path_data1, encoding="utf-8")
        f2 = open(path_data2, encoding="utf-8")
        origin_line_data = pd.read_csv(f1)
        origin_stop_data = pd.read_csv(f2)
        try:
            last_line = int(input())  # 从上次写入文件的位置(num值)继续爬取
            num = last_line
            line_list = lines[last_line + 1:]
            print('从{}继续爬取'.format(line_list[0]))
        except:
            print('已爬取完成')
            sys.exit()  # 停止
    print('|- - - - - - - - - - - - -开始爬取{}公交信息- - - - - - - - - - - -|'.format(city_name))
    all_line = pd.DataFrame()
    all_stop = pd.DataFrame()
    for line in line_list:
        line_data, stop_data = get_polyst(city_name, line)
        all_line = pd.concat([all_line, line_data], ignore_index=True)
        all_stop = pd.concat([all_stop, stop_data], ignore_index=True)
        num += 1
        if num % 50 == 0 or line == line_list[-1]:
            if len(origin_line_data) != 0 and len(origin_stop_data) != 0:
                all_line = pd.concat([origin_line_data, all_line], ignore_index=True)
                all_stop = pd.concat([origin_stop_data, all_stop], ignore_index=True)
                print('写入ing')
                all_line.to_csv(path2 + "\\" + city_name + '公交沿线坐标数据.csv', index=False, encoding='utf-8-sig')
                all_stop.to_csv(path2 + "\\" + city_name + '公交站点坐标数据.csv', index=False, encoding='utf-8-sig')
            else:
                print('写入ing')
                all_line.to_csv(path2 + "\\" + city_name + '公交沿线坐标数据.csv', index=False, encoding='utf-8-sig')
                all_stop.to_csv(path2 + "\\" + city_name + '公交站点坐标数据.csv', index=False, encoding='utf-8-sig')
        time.sleep(np.random.randint(1, 10))
        print('已运行:{} / {}次'.format(num, limit_requests))
    print('|- - - - - - - - - - - - -{}公交爬取完成- - - - - - - - - - - -|'.format(city_name))
    print((time.time() - start) / 60)