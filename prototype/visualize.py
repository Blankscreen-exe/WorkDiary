import csv
from datetime import datetime
import plotly.graph_objects as go
import numpy as np
import os

# Read data from CSV
tasks = []
with open(os.path.join('logs','work_log_all.csv'), 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        row['Date'] = datetime.strptime(row['Date'], '%d-%m-%Y').date()
        row['Time'] = datetime.strptime(row['Time'], '%H:%M:%S').time()
        tasks.append(row)

# Compute number of tasks per day
tasks_per_day = {}
for task in tasks:
    if task['Date'] not in tasks_per_day:
        tasks_per_day[task['Date']] = 0
    tasks_per_day[task['Date']] += 1

# Create line plot of tasks per day
fig1 = go.Figure()
fig1.add_trace(go.Scatter(x=list(tasks_per_day.keys()), y=list(tasks_per_day.values()), mode='lines+markers'))
fig1.update_layout(title='Tasks per day', xaxis_title='Date', yaxis_title='Number of tasks')

# Compute number of tasks per month
tasks_per_month = {}
for task in tasks:
    month = task['Date'].replace(day=1)
    if month not in tasks_per_month:
        tasks_per_month[month] = 0
    tasks_per_month[month] += 1

# Create line plot of tasks per month
fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=list(tasks_per_month.keys()), y=list(tasks_per_month.values()), mode='lines+markers'))
fig2.update_layout(title='Tasks per month', xaxis_title='Month', yaxis_title='Number of tasks')

# Compute standard deviation and variance of tasks with respect to time
times = [datetime.combine(task['Date'], task['Time']) for task in tasks]
time_diffs = np.diff(times).astype('timedelta64[h]').astype(float)
std_time = np.std(time_diffs)
var_time = np.var(time_diffs)

# Create bar plot of standard deviation and variance
fig3 = go.Figure()
fig3.add_trace(go.Bar(x=['Standard deviation', 'Variance'], y=[std_time, var_time]))
fig3.update_layout(title='Time deviation', xaxis_title='Metric', yaxis_title='Time difference (seconds)')

# Display plots in a single window
fig1.show()
fig2.show()
fig3.show()
