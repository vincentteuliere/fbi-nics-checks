# -*- coding: utf-8 -*-
"""
Created on Tue Oct 23 11:55:20 2018

@author: to101130
"""

import pandas as pd



def to_date(str):
    date = pd.to_datetime(str,format="%Y-%m")
    offset=date.days_in_month-1
    return date+pd.DateOffset(days=offset)

def to_int(x):
    return(int(x))

def calc_estimated_gun_sales_ponderation(df):
    
    ponderation = pd.Series()
    for col in df.iloc[:,2:].columns:
        if col.find('handgun')>=0:
             ponderation[col] = 1.1
        elif col.find('long_gun')>=0:
             ponderation[col] = 1.1             
        elif col.find('multiple')>=0:
             ponderation[col] = 2             
        else:
            ponderation[col] = 0
                    
    return ponderation
                       
def read_gun_data(xls,date_as_index=False):
    
    # This dataset is rather clean, few operations needed
    
    gun_data_df = pd.read_excel(xls,convert_float=True)
    # filling empty cells with 0
    gun_data_df=gun_data_df.fillna(0)    
    # converting to integer all float values
    gun_data_df.iloc[:,2:]=gun_data_df.iloc[:,2:].applymap(to_int)    
    
    # converting month column to pandas date & rename
    gun_data_df['month']=gun_data_df['month'].apply(to_date)
    gun_data_df=gun_data_df.rename(columns={'month':'date'})
    
    # add estimated gun sales - as suggested per NY times
    ponderation_vector = calc_estimated_gun_sales_ponderation(gun_data_df)
    gun_data_df['estimated_gun_sales']=(gun_data_df.iloc[:,2:].mul(ponderation_vector,axis=1)).sum(axis=1)
    
    if date_as_index:
        # set date as index
        gun_data_df=gun_data_df.set_index('date',drop=True)
        gun_data_df=gun_data_df.sort_index()

    return gun_data_df

import re


# parse 'Fact' to identify: 
# - start / end of the period in pd.datetime
# - unit as float
def parse_fact(fact):
    
    # parse dates (not starting per V)
    dates = re.findall('[^V]([0-9]{4})',fact)
    
    #label = fact[0:fact.find(',')]
    #label = label.replace(' ','_')
    
    if len(dates)==0:
        # some 'Fact' ahve no date
        # bit arbitrary ...
        dates=[2011,2015]
        
    # if there are 3 date found, keep last two
    if len(dates)>2:
        dates = dates[-2:]
    # start date is always first one
    start=dates[0]
    start=pd.to_datetime(start,format="%Y") 
    # end date is second one if there are two dates
    if len(dates)>1:
        end=dates[1]
    else:
        # or equal to start one
        end=start
    #in any case end of the period is end of the year
    end=pd.to_datetime(end,format="%Y")
    end += pd.DateOffset(years=1)
        
    # get units
    if fact.find('percent')>=0:
        unit = '%'
    elif fact.find('$1000')>=0:
        unit = '$1000'
    else:
        unit = 1
        
    return pd.Series([start,end,unit],index=['start','end','unit'])

# conversion to number
def to_number(x):
    
    # removing ',' and '.' (wonder how to string map ?)
    x = x.replace('$','')
    x = x.replace(',','')
    
    if x.find('%')>=0:
        x = x.replace('%','')
        x = float(x)/100.0
  
    try:
        x=float(x)
    except:        
        print 'Conversion error: ',x,'=> set to 0'
        x=0
        
    return x

def read_census_data(csv):
    
    census_data_df = pd.read_csv(csv)
    
    # drop 'Fact Note' column
    census_data_df = census_data_df.drop('Fact Note',axis=1)
    
    
    # all remaining cells are filled apart foot notes, 
    # dropna allows to remove these rows
    census_data_df = census_data_df.dropna()
    
    # PArsing 'Fact' column to add
    # - start date of the period
    # - end date of the period
    # - unit of the statistic
    census_data_df=pd.concat([census_data_df,census_data_df['Fact'].apply(parse_fact)],axis=1)

    # converting data to float values
    census_data_df.iloc[:-1,1:-3] = census_data_df.iloc[:-1,1:-3].applymap(to_number)    

    # drop FIPS Code
    census_data_df = census_data_df.iloc[:-1,:]
    
    # Seeting index as 'Fact'
    census_data_df = census_data_df.set_index('Fact')
    
    
    # Transposing
    census_data_df = census_data_df.transpose()
    
     # 
    census_data_df.iloc[:-3,:]=census_data_df.iloc[:-3,:].astype(float)
    
    return census_data_df

