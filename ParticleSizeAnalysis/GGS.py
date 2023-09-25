import sys
import matplotlib
from matplotlib import scale as mscale
matplotlib.use("Qt5Agg")
from RRScale import WeibullScale
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.figure import Figure
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QApplication, QPushButton, QGridLayout, QLabel, QComboBox, QSlider, QLineEdit, QMessageBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from scipy.optimize import curve_fit
import numpy as np
        
class MainWindow(QDialog):
    
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle("Modelling Particle Sizes")
        self.setGeometry(200, 100, 1440, 900)
        
        self.xComboBox = QComboBox(self)
        self.xComboBox.addItems(["GGS", "Rosin-Rammler", "Choose The Best Model"])
        self.xLabel = QLabel("&X:")
        self.xLabel.setBuddy(self.xComboBox)
        
        self.xTextBox = QLineEdit(self)
        self.xTextBoxLabel = QLabel("Enter Sieve Sizes with comma in between:")
        self.xTextBoxLabel.setBuddy(self.xTextBox)
        self.xButton = QPushButton("Enter Data", self)
        
        self.xButton.pressed.connect(self.onClickXData)
        
        self.yTextBox = QLineEdit(self)
        self.yTextBoxLabel = QLabel("Enter Cumulative Passing with comma in between:")
        self.yTextBoxLabel.setBuddy(self.yTextBox)
        self.yButton = QPushButton("Enter Data", self)
        
        self.yButton.pressed.connect(self.onClickYData)
        
        self.figure = plt.Figure()
        self.canvas = FigureCanvasQTAgg(self.figure)
        
        button = QPushButton("Plot current Attributes", self)
        button.pressed.connect(self.changeValue)
        
        grid = QGridLayout()
        grid.addWidget(self.xLabel)
        grid.addWidget(self.xComboBox)
        grid.addWidget(self.xTextBoxLabel)
        grid.addWidget(self.xTextBox)
        grid.addWidget(self.xButton)
        grid.addWidget(self.yTextBoxLabel)
        grid.addWidget(self.yTextBox)
        grid.addWidget(self.yButton)
        grid.addWidget(self.canvas)
        grid.addWidget(button)
        self.setLayout(grid)
        
    def onClickXData(self, *args):
        textBoxValuex = self.xTextBox.text()
        global x_data
        if textBoxValuex.__contains__(','):
            dataSet = QMessageBox(QMessageBox.Warning, " ", "Data set")
            x_data = np.fromstring(textBoxValuex, dtype=np.float32, sep=',')
            dataSet.exec_()
        else:
            errorMessage = QMessageBox(QMessageBox.Warning, "", "Please enter the data using commas in between values")
            errorMessage.exec_()
            
    def onClickYData(self, *args):
        textBoxValuey = self.yTextBox.text()
        global y_data
        if textBoxValuey.__contains__(','):
            dataSet = QMessageBox(QMessageBox.Warning, "Title", "Data set")
            y_data = np.fromstring(textBoxValuey, dtype=np.float32, sep=',')
            dataSet.exec_()
        else:
            errorMessage = QMessageBox(QMessageBox.Warning, "", "Please enter the data using commas in between values")
            errorMessage.exec_()
            
    def changeValue(self, *args):
                      
        self.figure.clear()
        
        if self.xComboBox.currentText() == "Choose The Best Model":
            poptGGS, pcovGGS = curve_fit(GGS, x_data, y_data)
            
            residualsGGS = y_data - GGS(x_data, *poptGGS)
            ss_res = np.sum(residualsGGS**2)
            ss_tot = np.sum((y_data-np.mean(y_data))**2)
            rSquaredGGS = 1 - (ss_res/ss_tot)
            
            y_dataRR = np.copy(y_data)
            
            with np.nditer(y_dataRR, op_flags=['readwrite']) as it:
                for x in it:
                    x[...] = 100 - x
            
            poptRR, pcovRR = curve_fit(RosinRammler, x_data, y_dataRR)
            
            residualsRR = y_dataRR - RosinRammler(x_data, *poptRR)
            ss_res = np.sum(residualsRR**2)
            ss_tot = np.sum((y_dataRR-np.mean(y_dataRR))**2)
            rSquaredRR = 1 - (ss_res/ss_tot)
            
            if rSquaredRR < rSquaredGGS:
                self.xComboBox.setCurrentText("GGS")
            else:
                self.xComboBox.setCurrentText("Rosin-Rammler")
        
        if self.xComboBox.currentText() == "GGS":
            ax = self.figure.add_subplot(111)
            
            ax.scatter(x_data, y_data, c='blue', alpha=0.95, 
                               edgecolors='none', label='data')
            
            t = "Cumulative Passing vs Sieve Size"
            ax.set(xlabel="Sieve Size", ylabel="Cumulative Passing", 
                   title = t)
            
            box = ax.get_position()
            ax.set_position([box.x0, box.y0 + box.height * 0.15, 
                             box.width * 0.9, box.height*0.9])
                
            #ax.axis([0.01, 10, 1, 110])
            ax.loglog()

            ax.grid(which='major', linestyle='-', axis='both')
            ax.grid(which='minor', linestyle='-', axis='both')

            for axis in [ax.xaxis, ax.yaxis]:
                formatter = mticker.ScalarFormatter()
                formatter.set_scientific(False)
                axis.set_major_formatter(formatter)
                ax.yaxis.set_minor_formatter(formatter)
                ax.xaxis.set_minor_formatter(formatter)

            popt, pcov = curve_fit(GGS, x_data, y_data)
            
            residuals = y_data - GGS(x_data, *popt)
            ss_res = np.sum(residuals**2)
            ss_tot = np.sum((y_data-np.mean(y_data))**2)
            rSquaredGGS = 1 - (ss_res/ss_tot)
            print(rSquaredGGS)
            print(GGS(x_data, *popt))
            
            print(MSE(y_data, GGS(x_data, *popt)))


            ax.plot(x_data, GGS(x_data, *popt), 'r-', 
                     label="Fitted curve: y = 100*(x/{0:.3f})**{1:.3f}".format(*popt))
                
            legend = ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), 
                               ncol=5)
            
            ax.add_artist(legend)
            
            self.canvas.draw()
        elif self.xComboBox.currentText() == "Rosin-Rammler":
            ax = self.figure.add_subplot(111)
            
            with np.nditer(y_data, op_flags=['readwrite']) as it:
                for x in it:
                    x[...] = 100 - x
            
            ax.scatter(x_data, y_data, c='blue', alpha=0.95, 
                               edgecolors='none', label='data')
            
            t = "Cumulative Retained vs Sieve Size"
            ax.set(xlabel="Sieve Size", ylabel="Cumulative Retained", 
                   title = t)
            
            box = ax.get_position()
            ax.set_position([box.x0, box.y0+ box.height * 0.15, 
                             box.width * 0.9, box.height*0.9])
            
            ax.axis([0.01, 10, 0.01, 99.9])
            #ax.loglog()
            mscale.register_scale(WeibullScale)
            ax.grid(which='major', linestyle='-', axis='both')
            ax.grid(which='minor', linestyle='-', axis='both')
            ax.set_yscale('rry')
            ax.set_xscale('log')
            
            formatter = mticker.ScalarFormatter()
            formatter.set_scientific(False)
            ax.xaxis.set_major_formatter(formatter)
            ax.xaxis.set_minor_formatter(formatter)
            
            popt, pcov = curve_fit(RosinRammler, x_data, y_data)
            
            
            ax.plot(x_data, RosinRammler(x_data, *popt), 'r-')
            
            residuals = y_data - RosinRammler(x_data, *popt)
            ss_res = np.sum(residuals**2)
            ss_tot = np.sum((y_data-np.mean(y_data))**2)
            rSquaredRR = 1 - (ss_res/ss_tot)
            print(rSquaredRR)
            
            print(MSE(y_data, RosinRammler(x_data, *popt)))
            
            print(RosinRammler(x_data, *popt))

            
            self.canvas.draw()
            

def myExpFunc(x, a, b):
    return a * np.power(x, b)

def GGS(x, d100, m):
    return 100 * (x/d100)**m

def findParticleSize(cumPass, a, b, c):
    return ((cumPass+abs(c))/a)**(1/b)

def RosinRammler(x, k, n):
    return 100*np.exp(-(x/k)**n)

def FitRR(x, y):
    popt, pcov = curve_fit(RosinRammler, x, y)
    k, n = popt[0], popt[1]
    return k, n

def MSE(actual, predicted):
    return np.square(np.subtract(actual, predicted)).mean()


sieveSizes_xdata = np.array([4.750, 3.350, 2.360, 1.700, 1.170, 
                             0.850, 0.600, 0.425, 0.300, 0.212, 0.149])

cumulativePassing_ydata = np.array([100.0, 97.8, 85.3, 68.8, 
                                    55.9, 44.1, 34.4, 28.7, 21.7, 18.0, 13.6])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    main = MainWindow()
    
    main.show()
    
    sys.exit(app.exec_())

