# -*- coding: utf-8 -*-
# @auther zhouhq
# create time 2020-05-15 17:47:38
import sys
import os
from core import dbconnect
from flask import Blueprint
from flask import Flask, request, jsonify, send_file, make_response, Response,redirect,session,g
from functools import wraps
import uuid


from math import sqrt
from numpy import concatenate
import matplotlib
import pandas as pd
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import tensorflow as tf
from pandas import read_csv
from pandas import DataFrame
import numpy as np
from pandas import concat
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import LSTM
from tensorflow.keras.models import load_model
from tensorflow import keras

#create route view
yieldpredict_route = Blueprint('yieldpredict', __name__) 


# 加载模型，传入自定义度量函数
model = load_model('m2.h5')

@yieldpredict_route.route('/yieldpre',methods = ['GET','POST'])
def predict():
    #initialize the data dictionary that will be returned from the view
    result = {"success": 'False'}

    if (request.args!= None):  
      listx = []
      x1 = request.args.get('x1')
      x2 = request.args.get('x2')
      x3 = request.args.get('x3')
      x4 = request.args.get('x4')
      x5 = request.args.get('x5')
      x6 = request.args.get('x6')
      x7 = request.args.get('x7')
      x8 = request.args.get('x8')
      listx = [x1,x2,x3,x4,x5,x6,x7,x8] 
      print(listx) ##['66666.00', '120028.21', '5603.42', '100356', '100', '21100', '118', '8400.66']
      data = np.array(listx)
      print(data) #['66666.00' '120028.21' '5603.42' '100356' '100' '21100' '118' '8400.66']
      print(data.shape) #(8,)
      print(data[2])  #5603.42
      data = data.reshape(-1,1) 
      print(data) ##二维数组
      print(data.shape) #(8, 1)
      df = pd.DataFrame(data)
      print(df)
      values = df.values     #将 df转为ndarray :结果与data.reshape(-1,1)的结果相同
      print(values) 
      print(values.shape) #(8, 1)
      values = values.astype('float64')
      print(values) #转为float64型
      print(values.shape) #（8,1）
      print('---------------------------')  
      scaler = MinMaxScaler(feature_range=(0, 1))
      scaled = scaler.fit_transform(values)
      print(scaled) ###数据归一化后的结果，仍是（8,1）的二维数组  
      #reframed = series_to_supervised(scaled, 1, 1)
      #print(reframed)
      #reframed.drop(reframed.columns[[9,10,11,12,13,14,15]], axis=1, inplace=True)   
      #print(reframed)  
      test_X = scaled
      test_X = test_X.reshape(1,-1)
      print(test_X) #转为（1,8） [[5.55048725e-01 1.00000000e+00 4.58892866e-02 8.35966784e-01
                               # 0.00000000e+00 1.75104756e-01 1.50089791e-04 6.92135737e-02]]
      test_X = test_X.reshape((test_X.shape[0], 1, test_X.shape[1])) ##将二维数组变为三维数组，即（1,8）变为（1,1,8）
      #[[[5.55048725e-01 1.00000000e+00 4.58892866e-02 8.35966784e-01
      # 0.00000000e+00 1.75104756e-01 1.50089791e-04 6.92135737e-02]]]
      print(test_X)
      print(test_X.shape) #(1, 1, 8)  
      yhat = model.predict(test_X)
      print(yhat) #[[0.38705617]] 
          ##预测结果的反归一化呈现
      test_X = test_X.reshape((test_X.shape[0], test_X.shape[2])) #将三维数组变为二维数组  (1,1,8) 变为 (1,8)
      print(test_X)
      inv_yhat = concatenate((yhat, test_X[:, 1:]), axis=1) ## yhat 替换test_x的第一列 ，与test_x整合 
      print(inv_yhat)
      #[[3.87056172e-01 1.00000000e+00 4.58892866e-02 8.35966784e-01
   #    0.00000000e+00 1.75104756e-01 1.50089791e-04 6.92135737e-02]]
      inv_yhat = scaler.inverse_transform(inv_yhat) # #将归一化后的结果逆转：计算误差之前需要把预测数据转换成同一个单位
      print(inv_yhat)
      #[[4.65189539e+04 1.20028210e+05 5.60342000e+03 1.00356000e+05
       # 1.00000000e+02 2.11000000e+04 1.18000000e+02 8.40066000e+03]]

      inv_yhat = inv_yhat[:,0]
      print(inv_yhat) #[46518.95386471]
      raw = inv_yhat.size
      print(raw) #1
      inv_yhat = inv_yhat[-raw:]
      print(inv_yhat) #[46518.95386471]

      result["prediction"] = str(inv_yhat[0])
      result["success"] = True
      # 返回Json格式的响应
      return jsonify(result)
    #    {
    #     "prediction": "31644.7662244308",
    #     "success": true
     #    }
