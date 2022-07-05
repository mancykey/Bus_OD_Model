import datetime

import pandas as pd
import xlwt
import openpyxl
import numpy as np
import time
import math
import operator
# import matplotlib.pyplot as plot

import sys

from scipy.spatial import distance

import coord_convert

# 时间戳转换为字符串
def _timestamp_to_time_str(int_timestamp):
    timeArray = time.localtime(int_timestamp)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return otherStyleTime

# 字符串转换为时间戳
def _time_str_to_timestamp(string_time):

    try:
        if string_time.find(r'/') >= 0 and len(string_time) >= 16:
            return int(time.mktime(time.strptime(string_time, "%Y/%m/%d %H:%M:%S")))
        elif string_time.find(r'-') >= 0 and len(string_time) >= 16:
            return int(time.mktime(time.strptime(string_time, "%Y-%m-%d %H:%M:%S")))
        elif string_time.find(r'/') >= 0 and len(string_time) <= 10:
            return int(time.mktime(time.strptime(string_time, "%Y/%m/%d")))
        elif string_time.find(r'-') >= 0 and len(string_time) <= 10:
            return int(time.mktime(time.strptime(string_time, "%Y-%m-%d")))

    # 出错
    except:
        return 0

def getOD():
    #将模型结果的数据按照上车站点、下车站点、日期来进行分类统计
    pd_transfer_data = pd.read_csv(r'.\Output\T_OD_Transfer_2021.09.01-2021.09.30.csv', low_memory=False, dtype={'code': str}, encoding='gbk')
    pd_transfer_data=pd_transfer_data.groupby(['On_Stop_ID', 'Off_Stop_ID'])['Volume'].sum().reset_index()
    print(pd_transfer_data["Volume"].sum())
    pd_OD_number_data =pd_transfer_data.copy()
    pd_Stop_xiaoqu_data = pd.read_csv(r'.\Output\出图数据\线路站点（带小区编号）.csv', low_memory=False, dtype={'code': str}, encoding='gbk')
    pd_OD_number_O_data = pd.merge( pd_OD_number_data, pd_Stop_xiaoqu_data,left_on=['On_Stop_ID'],right_on=['Stop_ID'],how='left')
    pd_OD_number_O_data = pd_OD_number_O_data.rename(columns={'Stop_Name': 'On_Stop_Name','Name': '起点_小区编号'})
    pd_OD_number_OD_data = pd.merge( pd_OD_number_O_data, pd_Stop_xiaoqu_data,left_on=['Off_Stop_ID'],right_on=['Stop_ID'],how='left')
    pd_OD_number_OD_data = pd_OD_number_OD_data.rename(columns={'Stop_Name': 'Off_Stop_Name','Name': '终点_小区编号'})
    pd_OD_number_OD_data=pd_OD_number_OD_data[['起点_小区编号', '终点_小区编号','Volume']]
    print(pd_OD_number_OD_data["Volume"].sum())
    pd_OD_number_OD_data=pd_OD_number_OD_data.groupby(['起点_小区编号', '终点_小区编号'])['Volume'].sum().reset_index()
    pd_OD_number_OD_data.to_csv(r'.\Output\出图数据\OD统计到上下车站点(到小区).csv', sep=',', header=True,
                     index=True, encoding='gbk')

def getred():
    print(0)
    date = 1
    pd_transfer = pd.DataFrame()
    pd_all = pd.DataFrame(columns=('date', 'transfer', 'no_transfer', 'all_number'))
    lst_date = []
    lst_transfer = []
    lst_no_transfer = []
    lst_all_number = []
    for i in range(30):
        data0 = str(date).rjust(2, '0')
        pd_transfer_data = pd.read_csv(r'.\Output\T_Bus_Transaction_Off_2021.09.{}.csv'.format(data0), low_memory=False,
                                       dtype={'code': str}, encoding='gbk')
        pd_transfer_all_data = pd_transfer_data[['Off_Stop_ID', 'Transfer', 'Volume']]
        print(pd_transfer_all_data['Volume'].sum())
        pd_transfer_data = pd_transfer_all_data[(pd_transfer_all_data['Transfer'] == 1)]
        # #补充非换乘数量
        pd_no_transfer_data = pd_transfer_all_data[(pd_transfer_all_data['Transfer'] == 0)]
        a=pd_no_transfer_data['Volume'].sum()
        b=pd_transfer_data['Volume'].sum()
        lst_date.append(i)
        lst_transfer.append(b)
        lst_no_transfer.append(a-b)
        lst_all_number.append(b+a)

        pd_transfer_data = pd_transfer_data.groupby(['Off_Stop_ID']).count().reset_index()
        pd_transfer = pd.concat([pd_transfer, pd_transfer_data])
        date = date + 1
    pd_all['time'] = lst_date
    pd_all['transfer']=lst_transfer
    pd_all['no_transfer'] = lst_no_transfer
    pd_all['all_number'] = lst_all_number
    pd_all.to_csv(r'.\Output\出图数据\计算换乘系数.csv', sep=',', header=True,
                     index=True, encoding='gbk')
    pd_transfer = pd_transfer.groupby(['Off_Stop_ID'])['Volume'].sum().reset_index()
    pd_transfer.to_csv(r'.\Output\出图数据\滁州9月1-9月30换乘数据.csv', sep=',', header=True,
                       index=True, encoding='gbk')
    # step2:将换乘数据总数转换成物理站点的字段
    pd_transfer = pd.read_csv(r'.\Output\出图数据\滁州9月1-9月30换乘数据.csv', low_memory=False,
                              dtype={'code': str}, encoding='gbk')
    pd_Stop_data = pd.read_csv(r'.\Output\Stop.csv', low_memory=False, dtype={'code': str}, encoding='gbk')
    pd_Phy_Stop_data = pd.read_csv(r'.\Input\Phy_Stop.csv', low_memory=False, dtype={'code': str}, encoding='gbk')
    #
    pd_Stop_data = pd_Stop_data[['Stop_ID', 'Phy_Stop_ID']]
    pd_transfer_number_data = pd.merge(pd_transfer, pd_Stop_data, left_on=['Off_Stop_ID'], right_on=['Stop_ID'],
                                       how='left')
    pd_transfer_number_data = pd_transfer_number_data.groupby(['Phy_Stop_ID'])['Volume'].sum().reset_index()
    pd_transfer_number_data['Volume_day'] = pd_transfer_number_data['Volume'] / 30
    pd_transfer_number_data = pd.merge(pd_transfer_number_data, pd_Phy_Stop_data, left_on=['Phy_Stop_ID'],
                                       right_on=['Phy_Stop_ID'], how='left')
    pd_transfer_number_data.to_csv(r'.\Output\出图数据\滁州9月1-9月30换乘站点热力图数据.csv', sep=',', header=True,
                                   index=True, encoding='gbk')

def get_updata():
    print(0)
    date = 1
    pd_transfer = pd.DataFrame()
    for i in range(30):
        data0 = str(date).rjust(2, '0')
        pd_transfer_data = pd.read_csv(r'.\Output\T_Bus_Transaction_On_2021.09.{}.csv'.format(data0), low_memory=False,
                                       dtype={'code': str}, encoding='gbk')
        pd_transfer_all_data = pd_transfer_data[['On_Stop_ID', 'Timestamp']]
        print(pd_transfer_all_data.shape[0])
        pd_transfer_data = pd_transfer_all_data.groupby(['On_Stop_ID']).count().reset_index()
        pd_transfer = pd.concat([pd_transfer, pd_transfer_data])
        date = date + 1
    pd_transfer = pd_transfer.groupby(['On_Stop_ID'])['Timestamp'].sum().reset_index()
    pd_transfer.rename(columns={'Timestamp': 'Volume'}, inplace=True)
    pd_Stop_data = pd.read_csv(r'.\Output\Stop.csv', low_memory=False, dtype={'code': str}, encoding='gbk')
    pd_Phy_Stop_data = pd.read_csv(r'.\Input\Phy_Stop.csv', low_memory=False, dtype={'code': str}, encoding='gbk')
    #
    pd_Stop_data = pd_Stop_data[['Stop_ID', 'Phy_Stop_ID']]
    pd_transfer_number_data = pd.merge(pd_transfer, pd_Stop_data, left_on=['On_Stop_ID'], right_on=['Stop_ID'],
                                       how='left')
    pd_transfer_number_data = pd_transfer_number_data.groupby(['Phy_Stop_ID'])['Volume'].sum().reset_index()
    pd_transfer_number_data['Volume_day'] = pd_transfer_number_data['Volume'] / 30
    pd_transfer_number_data = pd.merge(pd_transfer_number_data, pd_Phy_Stop_data, left_on=['Phy_Stop_ID'],
                                       right_on=['Phy_Stop_ID'], how='left')
    pd_transfer_number_data.to_csv(r'.\Output\出图数据\滁州9月1-9月30各站点上车量站点分布数据.csv', sep=',', header=True,
                                   index=True, encoding='gbk')
#将线路站点的经纬度更新成两侧实际经纬度
def get_stop_route():
    pd_stop_data = pd.read_csv(r'.\Output\Stop.csv', low_memory=False,
                                   dtype={'code': str}, encoding='gbk')
    pd_stop_Lnglat_data = pd.read_csv(r'.\Output\出图数据\原始站点信息.csv', low_memory=False,
                                   dtype={'code': str}, encoding='gbk')
    pd_stop_Lnglat_data=pd_stop_Lnglat_data.rename(columns={"线路名.1":"Route_Name","站点":"Stop_Name"})
    pd_stop_data = pd.merge(pd_stop_data, pd_stop_Lnglat_data, on=['Route_Name','Stop_Name'],
                                        how='left')

    # 第五步：将站点坐标从wgs84转换为高德
    lst_wgs_x = []
    lst_wgs_y = []
    arr_xy = pd_stop_data[['Lng', 'Lat']].values
    for i in range(pd_stop_data.shape[0]):
        lst_wgs_x.append(coord_convert.wgs84_to_gcj02(arr_xy[i][0],arr_xy[i][1])[0])
        lst_wgs_y.append(coord_convert.wgs84_to_gcj02(arr_xy[i][0],arr_xy[i][1])[1])
    pd_stop_data['Lng'] = lst_wgs_x
    pd_stop_data['Lat'] = lst_wgs_y

    pd_stop_data1 = pd_stop_data[['Stop_ID', 'Stop_Name',"Lng","经度"]]
    pd_stop_data2 = pd_stop_data[['Stop_ID', 'Stop_Name', "Lat","纬度"]]
    pd_stop_data1=pd_stop_data1.fillna(method="pad",axis=1)
    pd_stop_data2 = pd_stop_data2.fillna(method="pad", axis=1)
    pd_stop_data12 = pd.merge(pd_stop_data1, pd_stop_data2, on=['Stop_ID','Stop_Name'],
                                        how='left')
    pd_stop_data12.to_csv(r'.\Output\出图数据\线路站点.csv', sep=',', header=True,
                                   index=True, encoding='gbk')

def gettongdao(data):
    # 统计不同线路物理站点的流量
    # 线路站点通道的量统计成物理站点通道的量
    date = 1
    pd_tongdao = pd.DataFrame()
    for i in range(30):
        data0 = str(date).rjust(2, '0')
        pd_tongdao_data = pd.read_csv(r'.\Output\T_Link_Ride_Assignment_2021.09.{}.csv'.format(data0), low_memory=False,
                                       dtype={'code': str}, encoding='gbk')
        pd_tongdao_data = pd_tongdao_data[['Route_ID','On_Stop_ID', 'Off_Stop_ID', 'Volume']]
        print(pd_tongdao_data.shape[0],data0)
        pd_tongdao = pd.concat([pd_tongdao, pd_tongdao_data])
        date = date + 1
    pd_Stop_data = pd.read_csv(r'.\Output\Stop.csv', low_memory=False, dtype={'code': str}, encoding='gbk')
    pd_tongdao_data=pd_tongdao.copy()
    pd_tongdao_data['Volume'] = pd_tongdao_data['Volume'] / 30
    print(pd_tongdao_data['Volume'].sum())
    pd_Stop_data = pd_Stop_data[['Stop_Name','Route_ID','Line_ID','Line_Name','Stop_ID', 'Phy_Stop_ID']]
    pd_OD_number_O_data = pd.merge(pd_tongdao_data, pd_Stop_data, left_on=['Route_ID','On_Stop_ID'], right_on=['Route_ID','Stop_ID'],
                                   how='left')
    pd_OD_number_O_data = pd_OD_number_O_data.rename(columns={'Phy_Stop_ID': 'O_Phy_Stop_ID','Route_ID': 'O_Route_ID','Line_Name': 'O_Line_Name','Stop_Name': 'O_Stop_Name'})
    pd_OD_number_OD_data = pd.merge(pd_OD_number_O_data, pd_Stop_data, left_on=['Off_Stop_ID'], right_on=['Stop_ID'],
                                    how='left')
    pd_OD_number_OD_data = pd_OD_number_OD_data.rename(columns={'Phy_Stop_ID': 'D_Phy_Stop_ID','Stop_Name': 'D_Stop_Name'})
    pd_OD_number_OD_data = pd_OD_number_OD_data.groupby(['O_Phy_Stop_ID', 'D_Phy_Stop_ID','O_Line_Name','O_Route_ID','O_Stop_Name','D_Stop_Name']).sum().reset_index()
    pd_OD_number_OD_data_1 = pd_OD_number_OD_data[
        pd_OD_number_OD_data['O_Phy_Stop_ID'] < pd_OD_number_OD_data['D_Phy_Stop_ID']]
    pd_OD_number_OD_data_2 = pd_OD_number_OD_data[
        pd_OD_number_OD_data['D_Phy_Stop_ID'] < pd_OD_number_OD_data['O_Phy_Stop_ID']]
    pd_OD_number_OD_data_2 = pd_OD_number_OD_data_2.rename(
        columns={'O_Phy_Stop_ID': 'D_Phy_Stop_ID', 'D_Phy_Stop_ID': 'O_Phy_Stop_ID','O_Stop_Name':'D_Stop_Name','D_Stop_Name':'O_Stop_Name'})
    pd_OD_number_OD_data = pd.concat([pd_OD_number_OD_data_1, pd_OD_number_OD_data_2])
    pd_OD_number_OD_data = pd_OD_number_OD_data.groupby(['O_Phy_Stop_ID', 'D_Phy_Stop_ID','O_Line_Name','O_Route_ID','O_Stop_Name','D_Stop_Name']).sum().reset_index()
    pd_OD_number_OD_data.sort_values(by=['O_Route_ID', 'O_Phy_Stop_ID', 'D_Phy_Stop_ID'], inplace=True)
    print(pd_OD_number_OD_data['Volume'].sum())
    pd_OD_number_OD_data_all = pd_OD_number_OD_data.groupby(
        ['O_Phy_Stop_ID', 'D_Phy_Stop_ID'])['Volume'].sum().reset_index()
    pd_OD_number_OD_data_line = pd_OD_number_OD_data.groupby(
        ['O_Route_ID', 'O_Line_Name', 'O_Phy_Stop_ID', 'D_Phy_Stop_ID'])['Volume'].sum().reset_index()
    pd_OD_number_OD_data_all.to_csv(r'.\Output\出图数据\通道数据（起终点是物理站点,所有线路）.csv', sep=',', header=True,
                                index=True, encoding='gbk')
    pd_OD_number_OD_data_line.to_csv(r'.\Output\出图数据\通道数据（起终点是物理站点,分线路）.csv', sep=',', header=True,
                                index=True, encoding='gbk')

def statistic_peak_segment_speed5(date):
    # 用GPS瞬时速度统计高平峰小时平均车速
    date0 = 1
    pd_changzhou_data=pd.DataFrame()
    for i in range(30):
        date1=str(date0).rjust(2,'0')
        pd_GPS_data = pd.read_csv(r'.\Input\T_Bus_Gps_2021.09.{}.csv'.format(date1), low_memory=False, dtype={'code': str},
                                       encoding='gbk')
        pd_GPS_data['消费日期'] = pd_GPS_data['DateTime'].str.split(' ',expand=True)[0]
        pd_GPS_data['消费时间'] = pd_GPS_data['DateTime'].str.split(' ',expand=True)[1].str.split(':',expand=True)[0]
        pd_GPS_data.drop(pd_GPS_data[(pd_GPS_data['消费时间']=='0')].index, inplace=True)
        # l = ['1', '2', '3', '4', '5', '23', '24']
        L_zaogaofeng=['07']
        L_wangaofeng = ['17']
        L_pinfeng = ['06','08', '09', '10', '11', '12', '13', '14', '15', '16', '18', '19', '20', '21', '22']
        pd_GPS_data.loc[pd_GPS_data['消费时间'].isin(L_zaogaofeng), '峰段'] = '早高峰(7：00-9：00)'
        pd_GPS_data.loc[pd_GPS_data['消费时间'].isin(L_wangaofeng), '峰段'] = '晚高峰(17：00-18：00)'
        pd_GPS_data.loc[pd_GPS_data['消费时间'].isin(L_pinfeng), '峰段'] = '平峰(6：00-23：00除早晚高峰时间)'
        # pd_GPS_data.drop(pd_GPS_data[(pd_GPS_data['消费时间'].isin(l))].index, inplace=True)
        pd_GPS_data = pd_GPS_data[(pd_GPS_data['Speed']>10) &(pd_GPS_data['Speed']<60) ]
        pd_GPS_data = pd_GPS_data.groupby(['消费日期', '峰段'])['Speed'].mean().reset_index()
        pd_changzhou_data=pd.concat([pd_changzhou_data,pd_GPS_data])
        date0 = date0+1
    means = pd.pivot_table(pd_changzhou_data, index="消费日期", values='Speed', columns="峰段")
    means.to_csv(r'.\Output\出图数据\pd_GPS_speed_30days峰段.csv', sep=',', header=True,
                 index=True, encoding='gbk')

def get_special_station():
    print(0)
    date = 1
    pd_transfer = pd.DataFrame()
    for i in range(30):
        data0 = str(date).rjust(2, '0')
        pd_transfer_data = pd.read_csv(r'.\Output\T_Bus_Transaction_On_2021.09.{}.csv'.format(data0), low_memory=False,
                                       dtype={'code': str}, encoding='gbk')
        pd_transfer_all_data = pd_transfer_data[['On_Stop_ID', 'Timestamp']]
        print(pd_transfer_all_data.shape[0])
        pd_transfer_all_data['DateTime'] = pd_transfer_all_data['Timestamp'].apply(_timestamp_to_time_str)
        pd_transfer = pd.concat([pd_transfer, pd_transfer_all_data])
        date = date + 1
    pd_transfer ['hour']= pd_transfer['DateTime'].str[11:13]
    pd_Stop_data = pd.read_csv(r'.\Output\Stop.csv', low_memory=False, dtype={'code': str}, encoding='gbk')
    pd_Stop_data = pd_Stop_data[['Stop_ID', 'Phy_Stop_ID']]
    pd_transfer_number_data = pd.merge(pd_transfer, pd_Stop_data, left_on=['On_Stop_ID'], right_on=['Stop_ID'],
                                       how='left')
    pd_transfer_number_data["流量"] = 1
    pd_transfer_number_data=pd_transfer_number_data[['hour', 'Phy_Stop_ID','流量']]
    pd_transfer_number_data = pd_transfer_number_data.groupby(['Phy_Stop_ID', 'hour'])['流量'].sum().reset_index()
    print(pd_transfer_number_data["流量"].sum())
    means = pd.pivot_table(pd_transfer_number_data, index="Phy_Stop_ID", values="流量", columns="hour")
    means.to_csv(r'.\Output\出图数据\滁州9月1-9月30各站点24h客流分布数据.csv', sep=',', header=True,
                                   index=True, encoding='gbk')

def main():
    """
    绘图数据 ：OD、热力图、通道图
    """
    # getOD()#计算OD数据
    getred()#计算热力图数据（含换乘系数）
    # get_updata()#计算公交站点客流量分布
    # get_stop_route()#将线路站点的经纬度更新成两侧实际经纬度

    gettongdao('PyCharm')  # 计算各条线路相邻物理站点间的客流量、通道数据
    # get_special_station()   # 计算重点站点的24h客流分布
    """
    统计各峰段的运行速度
    """
    # statistic_peak_segment_speed5(1)
if __name__ == '__main__':
    main()