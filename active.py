import sys
import os
from flask import Blueprint
from flask import Flask, request, jsonify, send_file, make_response, Response,redirect,session,g
from functools import wraps
import uuid
from app.core import readconfig 
import json

from flask import Flask
import pymysql
from flask_sqlalchemy import SQLAlchemy
from flask import url_for
from app.bin import db
from app.schema.model import Fieldlist
from app.schema.model import Active
from app.schema.model import Activetype
from app.schema.model import UserActive
from app.schema.model import Activelevel

from flask_migrate import Migrate #引入数据库迁移框架模块
from flask_sqlalchemy import SQLAlchemy #ORM框架
from sqlalchemy import or_,not_,and_
from sqlalchemy.sql import 
#######################33333333

active_route = Blueprint('active',__name__)
@active_route.route('/')
def activeinfo():
    return "active home"

@active_route.route('/atype')
def atype(): #返回活动类型
    queryresult = db.session.query(Activetype.atype).group_by(Activetype.atype).order_by(Activetype.atype).all()
    atype  = []
    for i in queryresult if queryresult is not None else[]:
        atype.append(i[0])
    print(atype)

    response = make_response(jsonify(atype))
    return response

@active_route.route('/aitems')
def aitems(): #返回活动具体项目
    queryresult = db.session.query(Activetype.atype,Activetype.items).group_by(Activetype.atype,Activetype.items).order_by(Activetype.atype).all()
    print(queryresult)
    aitems  = []
    for i in queryresult if queryresult is not None else[]:
        aitems.append(i[1])
    print(aitems)
    response = make_response(jsonify(aitems))
    return response



@active_route.route('/getuseractives',methods = ['GET','POST'])
def getuseractives():#时间轴显示用户拥有地块的农作物活动类型
    userid = request.args.get('uid')
    if userid != None or userid != 'undefined':
        queryresult = db.session.query(UserActive.user_atype).filter_by(id='%s'%(userid)).all()
        print(queryresult) #[('8,9,3,15,16,18',)]
        if queryresult is not None:
            idcontent = queryresult[0][0]
        else:
            idcontent = ""
        print(idcontent) # 8,9,3,15,16,18
        idlist = idcontent.split(',') #通过指定分隔符对字符串进行切片,返回分割后的字符串列表。 ['8', '9', '3', '15', '16', '18']
        print(idlist)
        queryresult1 = db.session.query(Activetype.operate_time,Activetype.atype,Activetype.items).filter(Activetype.id.in_(idlist)).all()
        print(queryresult1)
  
        if queryresult1 is not None:
            activelist = {}
            for i in queryresult1:
                ob = {'operate_time':i[0]}
                ob['atype'] = i[1]
                ob['items'] = i[2]
                activelist[ob['operate_time']]= ob
        else:
            activelist = {"result":"0"}
    else:
        activelist = {'status':'-1','errmsg':'please input right user'}
    response = make_response(jsonify(activelist))
    return response    



@active_route.route('/activelevel',methods = ['GET','POST'])
def activelevel():#返回用户所拥有地块的活动等级
    userid = request.args.get('uid')
    if userid != None or userid != 'undefined':
    
        queryresult = db.session.query(Activelevel.fieldname,Activelevel.pesticides,Activelevel.manure,
                         Activelevel.seed,Activelevel.agr_plastic,Activelevel.agr_tools,Activelevel.irrigation,Activelevel.fertilizer,Activelevel.field_manage,
                         Activelevel.livestreaming,Activelevel.flood,Activelevel.gale,Activelevel.drought,Activelevel.hail,Activelevel.sand_storm,
                         Activelevel.insect_damage,Activelevel.earthquake,Activelevel.debris_flow,Activelevel.landslide
                         ).filter_by(userid= userid).all()
        print(queryresult)
        activelevel = {}
        for i in queryresult:
            ob = {'fieldname':i[0]}
            ob['pesticides']=i[1]
            ob['manure']=i[2]
            ob['seed']=i[3]
            ob['agr_plastic']=i[4]
            ob['agr_tools']=i[5]
            ob['irrigation']=i[6]
            ob['fertilizer']=i[7]
            ob['field_manage']=i[8]
            ob['livestreaming']=i[9]
            ob['flood']=i[10]
            ob['gale']=i[11]
            ob['drought']=i[12]
            ob['hail']=i[13]
            ob['sand_storm']=i[14]
            ob['insect_damage']=i[15]
            ob['earthquake']=i[16]
            ob['debris_flow']=i[17]
            ob['landslide']=i[18]
            activelevel[ob['fieldname']] = ob

    else:
        activelevel = {'status':'-1','errmsg':'please input right user'}
    response = make_response(jsonify(activelevel))
    return response    

@active_route.route('/grade',methods = ['GET','POST'])
def grade():#对某用户所拥有地块的活动等级评分进行求和
    userid = request.args.get('uid')
    if userid != None or userid != 'undefined':

        queryresult1 = db.session.query(func.sum(Activelevel.pesticides),func.sum(Activelevel.manure),
                         func.sum(Activelevel.seed),func.sum(Activelevel.agr_plastic),func.sum(Activelevel.agr_tools),func.sum(Activelevel.irrigation),func.sum(Activelevel.fertilizer),func.sum(Activelevel.field_manage),
                         func.sum(Activelevel.livestreaming),func.sum(Activelevel.flood),func.sum(Activelevel.gale),func.sum(Activelevel.drought),func.sum(Activelevel.hail),func.sum(Activelevel.sand_storm),
                         func.sum(Activelevel.insect_damage),func.sum(Activelevel.earthquake),func.sum(Activelevel.debris_flow),func.sum(Activelevel.landslide)
                         ).filter_by(userid= userid).all()
        
        print(queryresult1)
        queryresult2 = db.session.query(Activelevel.username).filter_by(userid= userid).first()
        print(queryresult2)
        print(queryresult2[0])
        
        ob = {'username':queryresult2[0]}

        activegrade = {}
        for i in queryresult1:
            ob['pesticides']=i[0]
            ob['manure']=i[1]
            ob['seed']=i[2]
            ob['agr_plastic']=i[3]
            ob['agr_tools']=i[4]
            ob['irrigation']=i[5]
            ob['fertilizer']=i[6]
            ob['field_manage']=i[7]
            ob['livestreaming']=i[8]
            ob['flood']=i[9]
            ob['gale']=i[10]
            ob['drought']=i[11]
            ob['hail']=i[12]
            ob['sand_storm']=i[13]
            ob['insect_damage']=i[14]
            ob['earthquake']=i[15]
            ob['debris_flow']=i[16]
            ob['landslide']=i[17]
            activegrade[ob['username']] = ob
    
    else:
        activegrade = {'status':'-1','errmsg':'please input right user'}
    response = make_response(jsonify(activegrade))
    return response   