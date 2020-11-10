# -*- coding: utf-8 -*-
"""
Created on Sun Nov  8 19:50:30 2020

@author: Karl Angelo Soliman
"""

#%% Creates a dataframe from expenses data 

import zipfile as zp, pandas as pd, matplotlib.pyplot as plt, datetime as dt

path = 'Expenses.zip' # expenses are stored by year in a zip file 
zipfile = zp.ZipFile(path, 'r')
files = zipfile.namelist()

allDF = pd.DataFrame() # creates a dataframe to hold the data from all years

for file in files:
    if file.endswith('.csv'):
        yearDF = pd.read_csv(zipfile.open(file), parse_dates=['Date']) # creates a df for each individual csv, changes data column to datetime type 
        allDF = pd.concat([allDF, yearDF], axis=0, ignore_index=True, sort=False) # adds individual csv to df containing all data

allDF['Expense'] = allDF['Expense'].replace('[$,]', '', regex=True).astype(float) # converts data in 'Expense' column from string to float 

#%% Function - finds the monthly expenses for a given year 

def byMonth(y): # 'yr' is the year to be analyzed
    
    months = {1:'Jan' , 2:'Feb' , 3:'Mar' , 4:'Apr', 5:'May' , 6:'Jun' ,
              7:'Jul' , 8:'Aug' , 9:'Sep' , 10:'Oct' , 11:'Nov' , 12:'Dec'}
    
    yearly = allDF[allDF['Date'].dt.year == y]
    monthly = []
    
    for k in months:
        monthlyDF = yearly[yearly['Date'].dt.month == k]
        monthly.append(monthlyDF['Expense'].sum().round(2))
    
    return monthly

#%% Function - finds the monthly expenses for a given year 

def byYear(y): # 'yr' is the year to be analyzed
    yearly = allDF[allDF['Date'].dt.year == y]
    total = yearly['Expense'].sum().round(2)
    
    return total

#%% Function - finds the monthly expenses for a given year 

def catYear(y): # 'yr' is the year to be analyzed
    yearly = allDF[allDF['Date'].dt.year == y]
    topCats = yearly['Category'].value_counts().head(3)
    
    return topCats.to_string()

#%% Function - graphs the monthly data for a given year 

def plotData(monthly, y): # 'data' should be the list of monthly expenses, 'yr' is the year of the monthly list

    months = {1:'Jan' , 2:'Feb' , 3:'Mar' , 4:'Apr', 5:'May' , 6:'Jun' ,
              7:'Jul' , 8:'Aug' , 9:'Sep' , 10:'Oct' , 11:'Nov' , 12:'Dec'}

    listMonths = [months[k] for k in months]
    
    dataGraph = plt.figure()
    plt.bar(listMonths, monthly)
    plt.title(f'Expenses ({y})')
    plt.xlabel('Month')
    plt.ylabel('Amount Spent ($)')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.show()
    
    return dataGraph

#%% PySimpleGUI

options = ('2017', '2018', '2019', '2020', 'All')

import PySimpleGUI as sg

sg.theme('SystemDefaultForReal')

layout = [[sg.Text('Choose an Option:\t'), sg.Combo(options, size=(10,1)), sg.Button('Analyze'), sg.Button('Cancel')],
          [sg.Text('Total'), sg.Text(key='Total', relief='sunken', size=(10,1), background_color='white'), sg.Text('Top Categories'), sg.Multiline(key='Top', size=(12,3), background_color='white')]]

window = sg.Window('Expenses Analysis Tool', layout)

while True:  # Event Loop
    event, values = window.read()
    print(event, values)
    if event == sg.WIN_CLOSED or event == 'Cancel':
        break
    if event == 'Analyze' and event != '':
        if values[0] in ['2017', '2018', '2019', '2020']:
            y = int(values[0])
            
            monthly = byMonth(y)
            total = byYear(y)
            topCat = catYear(y)
            
            window['Total'].update(total)
            window['Top'].update(topCat)
            
            fig1 = plotData(monthly, y)
            
        else: 
            total = allDF['Expense'].sum().round(2) # total expenses over all years 
            topCat = allDF['Category'].value_counts().head(3)
            
            window['Total'].update(total)
            window['Top'].update(topCat)
            
            ################ GRAPHING #################\
                
            months = {1:'Jan' , 2:'Feb' , 3:'Mar' , 4:'Apr', 5:'May' , 6:'Jun' ,
                      7:'Jul' , 8:'Aug' , 9:'Sep' , 10:'Oct' , 11:'Nov' , 12:'Dec'}
            
            listMonths = [months[k] for k in months]
            
            monthly2017 = byMonth(int('2017'))
            monthly2018 = byMonth(int('2018'))
            monthly2019 = byMonth(int('2019'))
            monthly2020 = byMonth(int('2020'))
            
            plt.figure()
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
            
window.close()
