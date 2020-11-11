# -*- coding: utf-8 -*-
"""
Created on Sun Nov  8 19:50:30 2020

@author: Karl Angelo Soliman
"""
#%% Packages Used 

import zipfile as zp
import pandas as pd
import numpy as np 
import PySimpleGUI as sg

import matplotlib 
matplotlib.use('TKAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg 
import matplotlib.pyplot as plt 

#%% Functions

def createAllDF(path): # unzips file, reads all .csv files, and creates a dataframe of all the data (input: filepath)
    zipfile = zp.ZipFile(path, 'r')
    files = zipfile.namelist()
    
    allDF = pd.DataFrame() # creates a dataframe to hold the data from all years
    
    for file in files:
        if file.endswith('.csv'):
            yearDF = pd.read_csv(zipfile.open(file), parse_dates=['Date']) # creates a df for each individual csv, changes data column to datetime type 
            allDF = pd.concat([allDF, yearDF], axis=0, ignore_index=True, sort=False) # adds individual csv to df containing all data
    return allDF

def createOptions(allDF): # finds the unique years within the dataframe to create a list of options for selection
    allDF['Expense'] = allDF['Expense'].replace('[$,]', '', regex=True).astype(float) # converts data in 'Expense' column from string to float 
    yearList = allDF['Date'].dt.year.unique().tolist() # creates a list of unique years in the df 
    yearList = [str(i) for i in yearList] # converts each year from datetime to string 
    yearList.insert(0, 'All') # adds 'All' option to selection menu
    options = tuple(yearList) # converts list to tuple (PySimpleGUI commands use tuples, not lists)
    return options

def byMonth(allDF, y): # finds the monthly expenses for a given year (input: dataframe, specific year)
    
    months = {1:'Jan' , 2:'Feb' , 3:'Mar' , 4:'Apr', 5:'May' , 6:'Jun' ,
              7:'Jul' , 8:'Aug' , 9:'Sep' , 10:'Oct' , 11:'Nov' , 12:'Dec'}
    
    yearly = allDF[allDF['Date'].dt.year == y]
    monthly = []
    
    for k in months:
        monthlyDF = yearly[yearly['Date'].dt.month == k]
        monthly.append(monthlyDF['Expense'].sum().round(2))
    return monthly

def byYear(allDF, y): # finds the total expenses for a given year (input: dataframe containing all data..., specific year)
    yearly = allDF[allDF['Date'].dt.year == y]
    total = yearly['Expense'].sum().round(2)
    total = '${:,.2f}'.format(total)
    return total

def catYear(allDF, y): # finds the top three categories for a given year (inputs: dataframe containing all data..., specific year)
    yearly = allDF[allDF['Date'].dt.year == y]
    topCats = yearly['Category'].value_counts().head(3)
    return topCats.to_string()

def plotData(monthly, y): # creates a bar chart of the monthly data for a given year (inputs: monthly expenses for a year, specific year)
    months = {1:'Jan' , 2:'Feb' , 3:'Mar' , 4:'Apr', 5:'May' , 6:'Jun' ,
              7:'Jul' , 8:'Aug' , 9:'Sep' , 10:'Oct' , 11:'Nov' , 12:'Dec'}

    listMonths = [months[k] for k in months]
    
    dataGraph = plt.figure()
    plt.bar(listMonths, monthly, color='orange')
    plt.plot(monthly, color='blue') # overlays line graph of data
    plt.title(f'Monthly Expenses in {y}') ; plt.xlabel('Month') ; plt.ylabel('Amount Spent ($)')
    plt.ylim([0, 300]) # implements a constant y-axis scale for easier comparison between years; change if monthly expenses exceed limit 
    plt.grid(True) ; plt.xticks(rotation=45) ; plt.tight_layout()
    plt.close()
    return dataGraph

def plotAll(allDF): # creates a stacked bar chart of the monthly data for all years (input: dataframe containing data from all years)
    yearList = allDF['Date'].dt.year.unique().tolist() # creates a list of unique years in the df 
    yearList = [str(i) for i in yearList] # converts each year from datetime to string 
        
    months = {1:'Jan' , 2:'Feb' , 3:'Mar' , 4:'Apr', 5:'May' , 6:'Jun' ,
              7:'Jul' , 8:'Aug' , 9:'Sep' , 10:'Oct' , 11:'Nov' , 12:'Dec'}
                
    listMonths = [months[k] for k in months]
    
    monthlyData = [byMonth(allDF, int(y)) for y in yearList] # stores list of monthly expenses for each year in a list containing data for all years
    monthlyData = np.array(monthlyData).sum(axis=0) # adds the expenses of each month to find expenses of each month for all years 
        
    fig1 = plt.figure()
    plt.bar(x=listMonths, height=monthlyData, color='orange')
    plt.plot(monthlyData, color='blue') # overlays line graph of data
    plt.title('Monthly Expenses over All Years') ; plt.xlabel('Month') ; plt.ylabel('Amount Spent ($)')
    plt.grid(True) ; plt.xticks(rotation=45) ; plt.tight_layout()
    plt.close()
    return fig1
    
def draw_figure(canvas, figure): # creates a canvas of a graph/chart through tkinter (allows figure to be inserted directly into PySimpleGUI)
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg

def delete_figure_agg(figure_agg): # deletes existing canvas (prevents stacking of charts in the window for subsequent analyses)
    figure_agg.get_tk_widget().forget()
    plt.close('all')

#%% PySimpleGUI

sg.theme('SystemDefaultForReal') # sets GUI theme to Windows default colors 

layout = [[sg.Frame(title='Selection', element_justification='l', layout=[
              [sg.Text('File:'), sg.Input(key='File', size=(29,1)), sg.FileBrowse(key='Browse'), sg.Button('OK')],
              [sg.Text('Choose an Option:\t'), sg.Combo(key='Options', values='', size=(12,1), disabled=True), sg.Button('Analyze', disabled=True), sg.Button('Reset', disabled=True)]])],
          [sg.Frame(title='Output', element_justification='c', layout=[
              [sg.Text('Data Analyzed:'), sg.Text(key='Current', size=(10,1), relief='solid', background_color='white', justification='c')],
              [sg.Text('Total:'), sg.Text(key='Total', relief='sunken', size=(10,1), background_color='white', justification='c'), sg.Text('Top Categories:'), sg.Multiline(key='Top', size=(12,3), background_color='white', justification='c')]])],
          [sg.Frame(title='Chart', element_justification='c', layout=[[sg.Canvas(key='Canvas', size=(650,475), background_color='white')]])]]

window = sg.Window('Expenses Analysis Tool', layout, element_justification='c')
window.Finalize()

while True:  # Event Loop
    event, values = window.read() # stores user inputs from window
    
    if event == sg.WIN_CLOSED: # closes the window when 'x' is pressed
        break
    
    if event == 'OK':
        allDF = createAllDF(values['File']) # calls function to open selected file and create a df containing all data
        options = createOptions(allDF) # calls function to create a list of available options for the combobox 
        window.FindElement('Options').update(values=options) # adds options to the combobox 
        window.FindElement('Options').update(set_to_index=0) # selects default option ('All' years)
        window.FindElement('Options').update(disabled=False) # enables user to make a selection from the combobox 
        window.FindElement('Analyze').update(disabled=False) # enables 'Analyze' button
        
    if event == 'Analyze': # if user presses the 'Analyze' button...
        window.FindElement('Analyze').update(disabled=True) # disables the 'Analyze' button until the window is reset
        window.FindElement('Reset').update(disabled=False) # enables the 'Reset' button 
        window.FindElement('Browse').update(disabled=True) # disables 'OK' button/new file selection until the window is reset
        window.FindElement('OK').update(disabled=True) # disables 'OK' button/new file selection until the window is reset
        
        if values['Options'] in options[1:]: # if user selects a year from the combobox...
            y = int(values['Options']) # gets the value of the year selected 
            monthly = byMonth(allDF, y) # calls function to find monthly data for that year
            total = byYear(allDF, y) # calls function to find total expenses for that year
            topCat = catYear(allDF, y) # calls function to find the top 3 categories for that year
            window.FindElement('Current').update(y) # displays year selected 
            window['Total'].update(total) # displays total expenses
            window['Top'].update(topCat) # displays top 3 categories
            fig1 = plotData(monthly, y) # calls function to plot monthly data for that year 
            figCanvas = draw_figure(window['Canvas'].TKCanvas, fig1) # calls function to add plot to the canvas 
            
        else: # if user selects 'All' from the combobox...
            total = allDF['Expense'].sum().round(2) # finds the total expenses over all years 
            total = '${:,.2f}'.format(total) # formats total into currency ($##,###.##)
            topCat = allDF['Category'].value_counts().head(3).to_string() # top three categories over all years         
            window.FindElement('Current').update(values['Options']) # displays current selection 
            window['Total'].update(total) # displays total expenses
            window['Top'].update(topCat) # displays top 3 categories
            fig1 = plotAll(allDF) # calls function to monthly data for all years
            figCanvas = draw_figure(window['Canvas'].TKCanvas, fig1) # calls function to add plot to the canvas   
            
    if event == 'Reset': # if user presses 'Reset' button...
        window.FindElement('Options').update(set_to_index=0)
        window.FindElement('Analyze').update(disabled=False) # re-enables 'Analyze' button
        window.FindElement('OK').update(disabled=False) # re-enables 'OK' button/new file selection
        window.FindElement('Browse').update(disabled=False) # disables 'OK' button/new file selection until the window is reset
        window.FindElement('OK').update(disabled=False) # disables 'OK' button/new file selection until the window is reset
        window['Current'].update('') # clears current selection display
        window['Total'].update('') # clears total expenses display
        window['Top'].update('') # clears top 3 categories display 
        delete_figure_agg(figCanvas) # calls function to clear canvas
        
window.close() # closes GUI