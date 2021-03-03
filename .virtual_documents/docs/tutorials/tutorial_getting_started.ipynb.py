from fasting import quantify
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter


export = "https://raw.githubusercontent.com/jbpauly/fasting/main/docs/tutorials/zero_export.csv"


zero_export = pd.read_csv(export)

zero_export[-5:]


fasts_discrete = quantify.zero_fasts(export)

fasts_discrete[:5]


fasts_continuous = quantify.continuous_fasts(fasts_discrete)

fasts_continuous[:5]


fig, ax = plt.subplots(figsize=(12,6))
ax.plot(fasts_continuous)
fig.autofmt_xdate()
plt.title('Binary Fasting Log: 0 (Not Fasting), 1 (Fasting)')
plt.xlabel('Date')
plt.ylabel('Fasting Status')
ax.set_yticks([0,1])
plt.show()


consecutive_minutes = quantify.consecutive_minutes(fasts_continuous)

consecutive_minutes[:5]


fig, ax = plt.subplots(figsize=(12,6))
ax.plot(consecutive_minutes)
fig.autofmt_xdate()
plt.title('Running Consecutive Minutes of Fasting')
plt.xlabel('Date')
plt.ylabel('Minutes')
plt.show()


cumulative_hours = quantify.daily_cumulative_hours(fasts_continuous)

cumulative_hours[:5]


fig, ax = plt.subplots(figsize=(12,6))
ax.bar(cumulative_hours.index, cumulative_hours.values)
fig.autofmt_xdate()
plt.title('Cumulative Hours of Fasting per Day')
plt.xlabel('Date')
plt.ylabel('Hours')
plt.show()


max_consecutive_hours = quantify.daily_max_consecutive_hours(fasts_continuous)

max_consecutive_hours[:5]


fig, ax = plt.subplots(figsize=(12,6))
ax.bar(max_consecutive_hours.index, max_consecutive_hours.values)
fig.autofmt_xdate()
plt.title('Maximum Consecutive Hours of Fasting per Day')
plt.xlabel('Date')
plt.ylabel('Hours')
plt.show()
