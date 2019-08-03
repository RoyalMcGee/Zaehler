import io
import random
from flask import Response
from flask import Flask, render_template, request, send_file, make_response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from time import sleep
import datetime
from datetime import datetime, timedelta

app = Flask(__name__)

import sqlite3
dbfile="../tempdata.db"

# Retrieve data from database
def getFirstData():
        conn=sqlite3.connect(dbfile)
        curs=conn.cursor()
        for row in curs.execute("SELECT * FROM Strom ORDER BY trigger ASC LIMIT 1"):
                time = str(row[1])
        conn.close()
        return time

def getLastData():
        conn=sqlite3.connect(dbfile)
        curs=conn.cursor()
        for row in curs.execute("SELECT * FROM Strom ORDER BY trigger DESC LIMIT 1"):
                time = str(row[1])
                count = row[2]
        conn.close()
        return time, count

def getHistData (numSamples):
        conn=sqlite3.connect(dbfile)
        curs=conn.cursor()
        curs.execute("SELECT * FROM Strom ORDER BY trigger DESC LIMIT "+str(numSamples))
        data = curs.fetchall()
        times = []
        counts = []
        for row in reversed(data):
                times.append(row[1])
                counts.append(row[2])
        conn.close()
        return times, counts

def maxRowsTable():
        conn=sqlite3.connect(dbfile)
        curs=conn.cursor()
        for row in curs.execute("select COUNT(trigger) from Strom"):
                maxNumberRows=row[0]
        conn.close()
        return maxNumberRows

#define and initialize global variables
global numSamples
numSamples = maxRowsTable()
if (numSamples > 101):
        numSamples = 100
scale=0.00133
        
    # main route 
@app.route("/")
def index():
        time, count = getLastData()
        first = getFirstData()
        templateData = {
                'time': time,
                'count': count,
                'first': first,
                'numSamples': numSamples
        }
        return render_template('index.html', **templateData)

@app.route('/', methods=['POST'])
def my_form_post():
    global numSamples
    numSamples = int (request.form['numSamples'])
    numMaxSamples = maxRowsTable()
    if (numSamples > numMaxSamples):
        numSamples = (numMaxSamples-1)
    time, count = getLastData()
    first = getFirstData()
    templateData = {
            'time': time,
            'count': count,
            'first': first,
            'numSamples': numSamples
    }
    return render_template('index.html', **templateData)

@app.route('/plot.png')
def plot_png():
    fig = create_figure()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

def create_figure():
    fig = Figure()
    times, counts = getHistData(numSamples)
    times = [x.strip() for x in times]
    times=[datetime.strptime(elem, '%Y-%m-%d %H:%M:%S') for elem in times]
    mplData = mdates.date2num(times)
    counts = [x*scale for x in counts]
    weights = [scale for x in counts]
    
    ax0 = fig.add_subplot(2, 1, 1)
    ax0.xaxis.set_major_locator(mdates.AutoDateLocator(interval_multiples=True))
    ax0.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    titel1 = "Stromverbrauch von \n "+times[0].strftime("%d/%m/%Y, %H:%M")+" bis #" + times[len(times)-1].strftime("%d/%m/%Y, %H:%M") + " \nkumulativ"
    ax0.set_title(titel1)
    ax0.set_xlabel('Zeit')
    ax0.set_ylabel('Verbrauch in kWh')
    ax0.grid(True)
    ax0.plot(mplData,counts,linewidth=1.0, color='black')
    ax1 = fig.add_subplot(2, 1, 2)
    ax1.xaxis.set_major_locator(mdates.AutoDateLocator(interval_multiples=True))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax1.set_title('relativ')
    ax1.set_xlabel('Zeit')
    ax1.set_ylabel('Verbrauch in kWh')
    ax1.grid(True)
    ax1.hist(mplData, bins=150, weights=weights, histtype='step', color='lightblue')
    return fig

if __name__ == "__main__":
   app.run(host='192.168.0.59', port=80, debug=False)
