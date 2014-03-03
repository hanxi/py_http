#!/usr/bin/python
# coding: UTF-8

#encoding=utf-8
'''
Created on 2012-11-7

@author: Steven
http://www.lifeba.org
基于BaseHTTPServer的http server实现，包括get，post方法，get参数接收，post参数接收。
'''
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import os,io,shutil  
import urllib,time
import getopt,string
import re

class MyRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.process(2)

    def do_POST(self):
        self.process(1)

    def process(self,type):

        content =""
        if type==1:#post方法，接收post参数
            datas = self.rfile.read(int(self.headers['content-length']))
            datas = urllib.unquote(datas).decode("utf-8", 'ignore')#指定编码方式
            datas = transDicts(datas)#将参数转换为字典
            if datas.has_key('data'):
                content = "data:"+datas['data']+"\r\n"

        query = urllib.splitquery(self.path)
        action = query[0]
        queryParams = {}

        if '?' in self.path:
            if query[1]:#接收get参数
                for qp in query[1].split('&'):
                    kv = qp.split('=')
                    queryParams[kv[0]] = urllib.unquote(kv[1]).decode("utf-8", 'ignore')
                    #print "queryParams:" + kv[0]+"==="+ queryParams[kv[0]]
                    #content+= kv[0]+':'+queryParams[kv[0]]+"\r\n"

        content_type,f = page(action,queryParams)
        self.send_response(200)
        self.send_header("Content-type", content_type)
        #self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        shutil.copyfileobj(f,self.wfile)

# end MyRequestHandler

#
def page(action,queryParams):
    print "action="+action
    data_type = "luadata_cehua_naruto"  # 具体哪份数据
    if queryParams.has_key('data_type'):
        data_type = queryParams['data_type']

    #指定返回编码
    enc="UTF-8"
    content = ""
    content = content.encode(enc)
    content_type = "text/plain"
    f = None
    if action=="/": #主页index.html
        f = open('index.html')
        f.seek(0)
        content_type = "text/html"

    elif action=="/data_lua.zip": #下载资源
#/data_lua.zip?data_type=luadata_cehua_naruto
        filename = "data/data_lua_"+data_type+".zip"

        # 发送 filelist.txt
        print filename
        f = open(filename)
        f.seek(0)
        content_type = "application/octet-stream"

    elif action=="/package": # 打包
#/package?data_type=luadata_cehua_naruto
        # svn up 更新代码,并获取版本号
        cmd = "svn up data/"+data_type
        print "cmd>"+cmd
        p = os.popen(cmd)
        x = p.read()
        m = re.search("[1-9]\d*",x)
        content += m.group()
        file_object = open(data_type+'version', 'w')
        file_object.write(content)
        file_object.close()

        # 删除之前的包
        cmd = "rm -rf data/data_luaa_"+data_type+".zip"
        print "cmd>"+cmd
        os.system(cmd)

        # 打包
        cmd = "zip -q -j data/data_lua_"+data_type+".zip" + " data/"+data_type + "/*.lua"
        print "cmd>"+cmd
        os.system(cmd)

        f = io.BytesIO()
        f.write(content)
        f.seek(0)

    elif action=="/getversion": # 获取下载文件列表
#/getversion?data_type=luadata_cehua_naruto
        f = open(data_type+'version')
        f.seek(0)
    else:
        content += "404"
        f = io.BytesIO()
        f.write(content)
        f.seek(0)

    # end if antion

    return content_type,f

# end MyRequestHandler

def transDicts(params):
    dicts={}
    if len(params)==0:
        return
    params = params.split('&')
    for param in params:
        dicts[param.split('=')[0]]=param.split('=')[1]
    return dicts
       
if __name__=='__main__':
    
    try:
        server = HTTPServer(('', 8081), MyRequestHandler)
        print 'started httpserver...'
        server.serve_forever()

    except KeyboardInterrupt:
        server.socket.close()
    
    pass

