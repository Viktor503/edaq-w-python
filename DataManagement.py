import pandas as pd
from tkinter import filedialog
from os import path


class DataManager():
    def __init__(self):
        self.df = pd.DataFrame(columns=['t','A','B','C'])

    def add_data(self,t,A,B,C):
        self.df = self.df.append({'t': t,'A': A,'B': B,'C': C},ignore_index=True)
    
    def save_data(self,savecolumns,format):
        if format == "txt":
            try:
                filename = filedialog.asksaveasfilename(initialdir=path.curdir,title="Save file",filetypes=(("Text File",".txt"),("All Files","*.*")))
                self.df.to_csv(filename,index=False,sep='\t',columns=savecolumns)
            except:
                pass
            
        elif format == "excel":
            try:
                filename = filedialog.asksaveasfilename(initialdir=path.curdir,title="Save file",filetypes=(("Text File",".xlsx"),("All Files","*.*")))
                self.df.to_excel(filename,index=False,columns=savecolumns)
            except:
                pass
            
    def clear_data(self):
        self.df = pd.DataFrame(columns=['t','A','B','C'])   
