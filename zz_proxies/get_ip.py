# -*- coding: utf-8 -*-
from .ShowapiRequest import ShowapiRequest
import json

def get_iplist():
    r = ShowapiRequest("http://route.showapi.com/22-1","71247","74d0687f30244dbd80c5e0972ad3a1fc" )
    # r.addFilePara("img", r"C:\Users\showa\Desktop\使用过的\4.png") #文件上传时设置
    res = r.post()
    items= json.loads(res.text)
    item= {}
    iplist=[]

    for i in items['showapi_res_body']['pagebean']['contentlist']:
        item['ip']=i['ip']
        item['port']=i['port']
        item['checktime']=i['checkTime']
        item['speed']=i['speed']
        ip = 'http://' + str(item['ip'] + ':' + str(item['port']))

        # print(ip)
        iplist.append(ip)
    return iplist




