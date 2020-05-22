# -*- coding: utf-8 -*-
import re
import json
import os
import sys
import io
import datetime
from io import BytesIO
import random
import string

import logging

import datetime
import uuid
import base64

from functools import wraps
from flask import Flask, request, jsonify, send_file, make_response, Response,redirect,session,g,send_from_directory
from flask import url_for

from imgengine import ogr2ogr


from core import readconfig 

from core import dbconnect
dbinfo = readconfig.getdbinfo()
dbname,dbuser,dbpwd,dbhost,dbport = dbinfo

from blueprint.pricepredict import pricepredict_route
from blueprint.yieldpredict import yieldpredict_route

appinfo='Agri Engine v1 @21AT  %s'%datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#app initialization    
app = Flask(__name__) 
app.config['SECRET_KEY'] = 'SECRET_KEY'

app.register_blueprint(yieldpredict_route,url_prefix='/yield') #在应用对象上注册这个蓝图对象
app.register_blueprint(pricepredict_route,url_prefix='/price') #在应用对象上注册这个蓝图对象

@app.route('/') 
def homepage(): 
    return "%s \n Server running"%appinfo

@app.route('/version')
def version():
    info = {'Version': appinfo}
    return jsonify(info)
    #response = make_response(jsonify(info))
    #return response

#1.地块列表接口
@app.route('/fieldlist')
def flist():
    conn = dbconnect.dbconnect(dbname,dbuser,dbpwd,dbhost,dbport)
    flist = []
    query = """
              SELECT fieldname
                FROM fieldlist; 
                """
    queryresult = conn.sqlquery(query)
    print(queryresult)
    if queryresult is not None:
        for i in queryresult:
            flist.append(i[0])
        response = make_response(jsonify(flist))
        return response
    
##2.地块详情接口   
@app.route('/fieldinfo')#通过app.route装饰了fieldinfo()函数，使其成为了路由函数
def fieldinfo():
    fieldname = request.args.get('fieldname')    
    conn = dbconnect.dbconnect(dbname,dbuser,dbpwd,dbhost,dbport)
    query = """SELECT
                     region,area,croptype,harvestdate,adddate,fielduser,id
                FROM
                    fieldlist
                WHERE
                    fieldname = '%s';"""%(fieldname)
    queryresult = conn.sqlquery(query)
    print(queryresult)
    if queryresult is not None:
        fieldinfo = {}
        for i in queryresult:
            ob = {'region':i[0]}
            ob['area'] = i[1]
            ob['croptype'] = i[2]
            ob['harvestdate'] = i[3]
            ob['adddate'] = i[4]
            ob['fielduser'] = i[5]
            fieldinfo[i[6]] = ob        
    else:
        fieldinfo = {"result":"0"}
    conn.close()
    print(fieldinfo)
    response = make_response(jsonify(fieldinfo))
    return response
#3.地块对应的植被指数信息接口
@app.route('/zbinfo',methods=['GET','POST'])
def zbinf():
    dbname,dbuser,dbpwd,dbhost,dbport = dbinfo
    fieldname = request.args.get('fieldname')
    startdate = request.args.get('startdate')
    enddate = request.args.get('enddate')
    conn = dbconnect.dbconnect(dbname,dbuser,dbpwd,dbhost,dbport)
    zbinfo = []
    query = """
               SELECT ndvi 
                FROM zb_ndvi
                WHERE fieldname = '%s'
                 AND datetime  BETWEEN '%s' AND '%s' ; """%(fieldname,startdate,enddate)
    print(query)
    queryresult = conn.sqlquery(query)
    if queryresult is not None:   
        for i in queryresult:
            zbinfo.append(i[0])
    response = make_response(jsonify(zbinfo))
    return response
    
#4.地块对应的天气数据接口
@app.route('/fieldweather',methods=['GET','POST'])##添加字段参数
def data():
    dbname,dbuser,dbpwd,dbhost,dbport = dbinfo
    startdate = request.args.get('startdate')
    enddate = request.args.get('enddate')
    fieldname = request.args.get('fieldname')
    conn = dbconnect.dbconnect(dbname,dbuser,dbpwd,dbhost,dbport)
    fieldweather = {}
    query = """SELECT datatime,temp_max,temp_min,rainfall,temp_acc_avg
               FROM "public".weather,"public".fieldlist
               WHERE fieldname = '%s'
	       AND weather.datatime BETWEEN '%s'AND '%s' 
	       AND weather.adc =fieldlist.adc """%(fieldname,startdate,enddate)#地块与天气的adc即区域代码需要对应
    print(query)##清楚看出查询语句的实例
    queryresult = conn.sqlquery(query)
    conn.close()
    print(queryresult)##查询的结果
    print('------------------')
    if queryresult is not None:   
        for i in queryresult:
            #ob ={'datatime':i[0]} 
            ob = {'temp_max':i[1]}
            ob['temp_min'] = i[2]
            ob['rainfall'] = i[3]
            ob['temp_acc_avg'] = i[4]
            #fieldweather[ob['datatime']] = ob ##key值的设定关系着输出结果的呈现
            fieldweather[i[0]] = ob
    else:
        fieldweather = {"result":"0"}   
    listjson = jsonify(fieldweather)
    response = make_response(listjson)
    return response

##5.农作物类型接口
@app.route('/typelist',methods=['GET','POST'])  
def typelistload():
    conn = dbconnect.dbconnect(dbname,dbuser,dbpwd,dbhost,dbport)
    typelist = []
    queryresult = conn.sqlquery("""SELECT distinct
                                        croptype 
                                    FROM
                                        fieldlist
                                    ORDER BY
                                    croptype;""")
    conn.close()
    print(queryresult)
    if queryresult is not None:
        for i in queryresult:
            typelist.append(i[0])
        listjson = jsonify(typelist)
    response = make_response(listjson)
    return response

#6.增加地块信息的接口
@app.route('/addfield',methods=['GET','POST'])  
def adddata():
    dbname,dbuser,dbpwd,dbhost,dbport = dbinfo
    conn = dbconnect.dbconnect(dbname,dbuser,dbpwd,dbhost,dbport)
    jsonstr = request.get_data()
    print('----------------------------------')
    print(jsonstr)
    print(type(jsonstr))#<class 'bytes'>
    print('------------------------------')
    print(jsonstr.decode('utf-8'))#浏览器需要根据文件指定编码如utf-8转换成 字符串 也就是html代码
    print(type(jsonstr.decode('utf-8')))#<class 'str'>
    jsondata = json.loads(jsonstr.decode('utf-8'))#转化为 字典 。
    print('--------------------------------')
    print(jsondata)
    print(type(jsondata))#<class 'dict'>
    #fid = str(uuid.uuid1()).replace('-','')
    fid = jsondata.get("id")   
    fieldname = jsondata.get("fieldname")
    area = jsondata.get("area")
    croptype = jsondata.get("croptype")
    harvestdate = jsondata.get("harvestdata")
    adddate = jsondata.get("adddate")
    region = jsondata.get("region")
    fielduser = jsondata.get("fielduser")
    excute="""
             INSERT INTO "public"."fieldlist"("id","fieldname","area","croptype","harvestdate","adddate","region","fielduser")
             VALUES('%s','%s','%s','%s','%s','%s','%s','%s')"""%(fid,fieldname,area,croptype,harvestdate,adddate,region,fielduser)

    print('******')
    queryresult = conn.sqlchange(excute)
    print(queryresult)#True
    
    if queryresult is True:
        response = make_response({'msg':'success','status':'200','result':'add one fielditem!'})  
        return response
    else:
        response = make_response("Fail add data!")  
        return response
#insert into tablename [(column1 [,column2,,...])]
#values (value1 [,value2...]);

#********6.2 在weather表中添加数据
@app.route('/weather',methods=['GET','POST'])  
def addwdata():
    dbname,dbuser,dbpwd,dbhost,dbport = dbinfo
    conn = dbconnect.dbconnect(dbname,dbuser,dbpwd,dbhost,dbport)
    jsonstr = request.get_data()##request对象：获取客户端post请求的参数值
    jsondata = json.loads(jsonstr.decode('utf-8'))
    wid = jsondata.get("id_num")   
    datatime = jsondata.get("datatime")
    temp_max = jsondata.get("temp_max")
    temp_min = jsondata.get("temp_min")
    rainfall = jsondata.get("rainfall")
    temp_acc_avg = jsondata.get("temp_acc_avg")

    excute="""
             INSERT INTO "public"."weather"("id_num","datatime","temp_max","temp_min","rainfall","temp_acc_avg")
             VALUES('%s','%s','%s','%s','%s','%s')"""%(wid,datatime,temp_max,temp_min,rainfall,temp_acc_avg)

    queryresult = conn.sqlchange(excute)
    print(queryresult) ####True
    
    if queryresult is True:
        response = make_response("Add new weatheritem!")  
        return response
    else:
        response = make_response("Failed add weatheritem!")  
        return response
       
#7.删除某个地块信息的接口
@app.route('/delfield',methods=['GET','POST'])
def delfid():
    taskname = request.args.get('fieldname')#reuqest对象：获取客户端get请求的参数值
    print(taskname)
    conn = dbconnect.dbconnect(dbname,dbuser,dbpwd,dbhost,dbport)
    query = """ SELECT
                      *
                FROM
                    fieldlist
                WHERE
                    fieldname = '%s'; 
                  """%(taskname)
    queryresult = conn.sqlquery(query)
    print(queryresult)
    if queryresult is not None:#删除语句之前需先判定待删除的记录是否真实存在
        conn = dbconnect.dbconnect(dbname,dbuser,dbpwd,dbhost,dbport)
        excute = """
                              delete from "public"."fieldlist"
                              WHERE fieldname= '%s';"""%(taskname)
        print(excute)                            
        deleteresult = conn.sqlchange(excute)
        print(deleteresult)
        conn.close()
        if deleteresult is True:
            result = {'msg':'success','status':'200','result':'delete one fielditem!'}
        else:
            result = {'status':'-1','errmsg':'Failed delete one item!'}  
    else:
        result = {'status':'-1','errmsg':'please input right fieldname'}       
    response = make_response(jsonify(result))
    return response  
#delete from tablename
#where expr;

#8.改变地块信息的接口
@app.route('/fieldchange',methods=['GET','POST'])
def fieldupdate():
    taskname = request.args.get('fieldname')
    region = request.args.get('region')
    print(taskname)
    conn = dbconnect.dbconnect(dbname,dbuser,dbpwd,dbhost,dbport)
    query = """
               SELECT
                       *
                FROM
                    fieldlist
                WHERE
                    fieldname = '%s';"""%(taskname)
    queryresult = conn.sqlquery(query)
    if queryresult is not None:
        excute = """
                    update "public"."fieldlist"
                    SET "region" = '%s'
                    WHERE fieldname= '%s';"""%(region,taskname)
        print(excute)                      
        changeresult = conn.sqlchange(excute)
        print(changeresult)
        if changeresult is True:
            result = {'msg':'success','status':'200','result':'update one item!'}
        else:
            result =  {'status':'-1','errmsg':'Failed update one item!'}  
    else:
        result = {'status':'-1','errmsg':'please input right fieldname'}
    response = make_response(jsonify(result))
    return response
#update tablename
#set col_name1=expr1 [,col_name2=expr2...]
#[where expr];

#9.地块名称与农作物类型的匹配接口
@app.route('/fieldname')
def fieldtype():
    conn = dbconnect.dbconnect(dbname,dbuser,dbpwd,dbhost,dbport)
    croptype = {}
    query = """SELECT
                    croptype,array_agg(fieldname)
                FROM
                    fieldlist
                GROUP BY
                    croptype;"""
    queryresult = conn.sqlquery(query)
    conn.close()
    print(queryresult)
    if queryresult is not None:
        for i in queryresult:
            croptype[i[0]] = i[1]
        listjson = jsonify(croptype)
        print(listjson)
    response = make_response(listjson)
    return response




if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5040', debug=True) #实例化对象.run表示运行启动flask应用，已经写好的一个flask文件就是一个应用，即把自身当成应用，然后启动。
