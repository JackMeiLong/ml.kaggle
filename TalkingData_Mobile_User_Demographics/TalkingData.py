# coding=utf8
"""
Created on Tue Jul 12 11:53:08 2016

@author: meil
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder
from sklearn.feature_extraction import FeatureHasher
from sklearn.preprocessing import LabelEncoder

events = pd.read_csv("events.csv", dtype = {"device_id": np.str}, 
                     infer_datetime_format = True, parse_dates = ["timestamp"])
app_events = pd.read_csv("app_events.csv", usecols = [0, 2, 3],
                            dtype = {"is_active": np.float16, "is_installed": np.float16})

# get hour and drop timestamp
events["hour"] = events["timestamp"].apply(lambda x: x.hour).astype(np.int8)
events.drop("timestamp", axis = 1, inplace = True)

# merge data w/o train or test
events = events.merge(app_events, how = "left", on = "event_id")
#del app_events
events.drop("event_id", axis = 1, inplace = True)

# prep brands
phone = pd.read_csv("phone_brand_device_model.csv", dtype={"device_id": np.str},
                    usecols = [0, 1, 2])
#feat = FeatureHasher(n_features=12, input_type="string")
#
#feat1 = feat.transform(phone["phone_brand"] + " " + phone["device_model"])

events = events.merge(pd.concat([phone["device_id"], phone["phone_brand"],phone["device_model"]], axis = 1),
                     how = "left", on = "device_id")
#del phone, feat, feat1

print("pre-merging and hashing finished.")

# train steps
train = pd.read_csv("gender_age_train.csv", dtype = {"device_id": np.str},\
                    usecols = [0, 3])
t2 = train.copy()
train.drop("group", axis = 1, inplace = True)
train = train.merge(events, how = "left", on = "device_id")
train.fillna(-1, inplace = True)

tt=pd.concat([train.phone_brand,phone.device_model],axis=1)
phone_brand=train.phone_brand
device_model=train.device_model

#ttp=phone_brand.map(lambda x:{tt.columns[0]:x})
#ttd=device_model.map(lambda x:{tt.columns[1]:x})
#ttm=pd.concat([ttp,ttd],axis=1)
#tta=ttm.values
#ttl=[]
#
#
#for te in tta:
#    te[0].update(te[1])
#    ttl.append(te[0])


train = train.groupby("device_id").mean().reset_index()
train = train.merge(t2, how ="left", on = "device_id")

label = train["group"].copy()
le=LabelEncoder()
lable=le.fit_transform(label)

train.drop(["group", "device_id"], axis = 1, inplace = True)

print("train data merged and prepared")
print("-----------------------------------")

print 'Starting to prepare testdata'
test=pd.read_csv('gender_age_test.csv',dtype={'device_id':np.str})

test=test.merge(events,how='left',on='device_id')
test.fillna(-1,inplace=True)

test=test.groupby('device_id').mean().reset_index()
#test.drop(['device_id'],axis=1,inplace=True)
print 'test data prepared'

