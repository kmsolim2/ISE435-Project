# -*- coding: utf-8 -*-
"""
Created on Sun Nov  8 19:50:30 2020

@author: Karl Angelo Soliman
"""

## Creating a dataframe from expenses data 

import zipfile as zp
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import numpy as np

path = 'Expenses.zip' # expenses are stored by year in a zip file 
zipfile = zp.ZipFile(path, 'r')
files = zipfile.namelist()

allDF = pd.DataFrame() # creates a dataframe for the data from all years

for file in files:
    if file.endswith('.csv'):
        yearDF = pd.read_csv(zipfile.open(file), parse_dates=['Date']) # creates a df for each individual csv, changes data column to datetime type 
        allDF = pd.concat([allDF, yearDF], axis=0, ignore_index=True, sort=False) # adds individual csv to df containing all data

allDF['Expense'] = allDF['Expense'].replace('[$,]', '', regex=True).astype(float) # converts data in 'Expense' column from string to float 

## Creates individual dataframes for each year 

year2017 = allDF[allDF['Date'].dt.year == 2017]
year2018 = allDF[allDF['Date'].dt.year == 2018] 
year2019 = allDF[allDF['Date'].dt.year == 2019] 
year2020 = allDF[allDF['Date'].dt.year == 2020] 

## Separates data by month

months = {1:'Jan',
          2:'Feb',
          3:'Mar',
          4:'Apr',
          5:'May',
          6:'Jun',
          7:'Jul',
          8:'Aug',
          9:'Sep',
          10:'Oct',
          11:'Nov',
          12:'Dec'}

listMonths = [months[k] for k in months]

monthly2017 = []
monthly2018 = []
monthly2019 = []
monthly2020 = []

# Calculates monthly expenses for each year 

for k in months :
    monthlyDF = year2017[year2017['Date'].dt.month == k]
    monthly2017.append(monthlyDF['Expense'].sum().round(2))
    
    monthlyDF = year2018[year2018['Date'].dt.month == k]
    monthly2018.append(monthlyDF['Expense'].sum().round(2))
    
    monthlyDF = year2019[year2019['Date'].dt.month == k]
    monthly2019.append(monthlyDF['Expense'].sum().round(2))
    
    monthlyDF = year2020[year2020['Date'].dt.month == k]
    monthly2020.append(monthlyDF['Expense'].sum().round(2))    

# Calculates total expenses  and yearly expenses

total = allDF['Expense'].sum().round(2) # total expenses over all years 
print('Total :', total)

total2017 = year2017['Expense'].sum().round(2) # finds the total expenses for a given year
total2018 = year2018['Expense'].sum().round(2)
total2019 = year2019['Expense'].sum().round(2)
total2020 = year2020['Expense'].sum().round(2)

yrTotal = [total2017, total2018, total2019, total2020]
yr = [2017, 2018, 2019, 2020]

for y, t in zip(yr, yrTotal):
    print(f'{y} : {t}')

## Finds top 3 categories

topCats = allDF['Category'].value_counts().head(3)
print(topCats)

## Graph yearly data

fig1 = plt.figure(1)
plt.bar(listMonths, monthly2017)
plt.title('Expenses (2017)')
plt.xlabel('Month')
plt.ylabel('Amount Spent ($)')
plt.grid(True)
plt.xticks(rotation=45)

fig2 = plt.figure(2)
plt.bar(listMonths, monthly2018, color='orange')
plt.title('Expenses (2018)')
plt.xlabel('Month')
plt.ylabel('Amount Spent ($)')
plt.grid(True)
plt.xticks(rotation=45)

fig3 = plt.figure(3)
plt.bar(listMonths, monthly2019, color='green')
plt.title('Expenses (2019)')
plt.xlabel('Month')
plt.ylabel('Amount Spent ($)')
plt.grid(True)
plt.xticks(rotation=45)

fig4 = plt.figure(4)
plt.bar(listMonths, monthly2020, color='red')
plt.title('Expenses (2020)')
plt.xlabel('Month')
plt.ylabel('Amount Spent ($)')
plt.grid(True)
plt.xticks(rotation=45)

fig5 = plt.figure(5) # creates a stacked bar chart
plt.bar(listMonths, monthly2017)
plt.bar(listMonths, monthly2018, bottom=monthly2017) 
plt.bar(listMonths, monthly2019, bottom=[i + j for i, j in zip(monthly2017, monthly2018)]) # combines data frome 2017 and 2018
plt.bar(listMonths, monthly2020, bottom=[i + j + k for i, j, k in zip(monthly2017, monthly2018, monthly2019)]) # combines data from 2017, 2018, and 2019
plt.title('Expenses (All Years)')
plt.xlabel('Month')
plt.ylabel('Amount Spent ($)')
plt.grid(True)
plt.xticks(rotation=45)
plt.legend([2017, 2018, 2019, 2020])

            
