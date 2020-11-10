# -*- coding: utf-8 -*-
"""
Created on Sun Nov  8 19:50:30 2020

@author: Karl Angelo Soliman
"""

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

import matplotlib.pyplot as plt

def plotData(monthly, y): # 'data' should be the list of monthly expenses, 'yr' is the year of the monthly list 
    
    months = {1:'Jan' , 2:'Feb' , 3:'Mar' , 4:'Apr', 5:'May' , 6:'Jun' ,
              7:'Jul' , 8:'Aug' , 9:'Sep' , 10:'Oct' , 11:'Nov' , 12:'Dec'}

    listMonths = [months[k] for k in months]
    
    dataGraph = plt.figure()
    plt.bar(listMonths, monthly)
    plt.title(f'Monthly Expenses in {y}') ; plt.xlabel('Month') ; plt.ylabel('Amount Spent ($)')
    plt.grid(True) ; plt.xticks(rotation=45) ; plt.tight_layout()
    plt.close()
    
    return dataGraph

#%% Function - creates a stacked bar chart with yearly data

import numpy as np 
import matplotlib.pyplot as plt

def plotAll(allDF): 
    yearList = allDF['Date'].dt.year.unique().tolist() # creates a list of unique years in the df 
    yearList = [str(i) for i in yearList] # converts each year from datetime to string 
        
    months = {1:'Jan' , 2:'Feb' , 3:'Mar' , 4:'Apr', 5:'May' , 6:'Jun' ,
              7:'Jul' , 8:'Aug' , 9:'Sep' , 10:'Oct' , 11:'Nov' , 12:'Dec'}
                
    listMonths = [months[k] for k in months]
    monthlyData = [byMonth(int(y)) for y in yearList]
    monthlyData = np.array(monthlyData).sum(axis=0)
        
    fig1 = plt.figure()
    plt.bar(x=listMonths, height=monthlyData)
    plt.title('Monthly Expenses over All Years') ; plt.xlabel('Month') ; plt.ylabel('Amount Spent ($)')
    plt.grid(True) ; plt.xticks(rotation=45) ; plt.tight_layout()
    plt.close()
    
    return fig1
            
#%% Function - creates a canvas (allows figure to be inserted directly into PySimpleGUI)

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib ; matplotlib.use('TKAgg')
    
def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    
    return figure_canvas_agg

#%% Function - deletes existing canvas (prevents stacking in the window)

import matplotlib ; matplotlib.use('TKAgg')
    
def delete_figure_agg(figure_agg):
    figure_agg.get_tk_widget().forget()
    plt.close('all')
    
#%% Creates a dataframe from expenses data 

import zipfile as zp, pandas as pd # , datetime as dt

path = 'Expenses.zip' # expenses are stored by year in a zip file 
zipfile = zp.ZipFile(path, 'r')
files = zipfile.namelist()

allDF = pd.DataFrame() # creates a dataframe to hold the data from all years

for file in files:
    if file.endswith('.csv'):
        yearDF = pd.read_csv(zipfile.open(file), parse_dates=['Date']) # creates a df for each individual csv, changes data column to datetime type 
        allDF = pd.concat([allDF, yearDF], axis=0, ignore_index=True, sort=False) # adds individual csv to df containing all data

allDF['Expense'] = allDF['Expense'].replace('[$,]', '', regex=True).astype(float) # converts data in 'Expense' column from string to float 
yearList = allDF['Date'].dt.year.unique().tolist() # creates a list of unique years in the df 
yearList = [str(i) for i in yearList] # converts each year from datetime to string 

#%% PySimpleGUI

import PySimpleGUI as sg

yearList.append('All') # adds 'All' option to selection menu
options = tuple(yearList) # converts list to tuple (PySimpleGUI commands use tuples, not lists)

sg.theme('SystemDefaultForReal')

layout = [[sg.Text('Choose an Option:\t'), sg.Combo(options, size=(10,1), default_value=options[-1]), sg.Button('Analyze'), sg.Button('Reset', disabled=True)],
          [sg.Frame(title='Analysis', element_justification='c', layout=[
              [sg.Text('Currently Selected:'), sg.Text(key='Current', size=(10,1), relief='solid', background_color='white', justification='c')],
              [sg.Text('Total'), sg.Text(key='Total', relief='sunken', size=(10,1), background_color='white', justification='c'), sg.Text('Top Categories'), sg.Multiline(key='Top', size=(12,3), background_color='white', justification='c')]])],
          [sg.Frame(title='Chart', element_justification='c', layout=[[sg.Canvas(key='Canvas', size=(650,475), background_color='white')]])]]

window = sg.Window('Expenses Analysis Tool', layout, element_justification='c')
window.Finalize()

while True:  # Event Loop
    event, values = window.read()
    
    if event == sg.WIN_CLOSED:
        break
    
    if event == 'Analyze':
        window.FindElement('Analyze').update(disabled=True)
        window.FindElement('Reset').update(disabled=False)
        window.FindElement('Canvas').unhide_row()
        
        if values[0] in options[0:-1]:
            y = int(values[0])
            monthly = byMonth(y)
            total = byYear(y)
            topCat = catYear(y)
            window.FindElement('Current').update(y)
            window['Total'].update(total)
            window['Top'].update(topCat)
            fig1 = plotData(monthly, y)
            figCanvas = draw_figure(window['Canvas'].TKCanvas, fig1)
            
        else: 
            window.FindElement('Current').update('All')
            total = allDF['Expense'].sum().round(2) # total expenses over all years 
            topCat = allDF['Category'].value_counts().head(3).to_string() # top three categories over all years         
            window['Total'].update(total)
            window['Top'].update(topCat)            
            fig1 = plotAll(allDF)
            figCanvas = draw_figure(window['Canvas'].TKCanvas, fig1)   
            
    if event == 'Reset':
        window.FindElement('Analyze').update(disabled=False)
        window.FindElement('Reset').update(disabled=True)
        window['Current'].update('')
        window['Total'].update('')
        window['Top'].update('')       
        delete_figure_agg(figCanvas)
        
window.close()
