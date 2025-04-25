import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib.dates as mdates

#Function to convert time from Min:Sec:MiliSecond (1:12.123) to seconds
def convert_to_sec(time):
    if time == '\\N' or pd.isna(time):  # Check for missing or invalid values
        return None
    splits = time.split(':') #this splits a string like 1:12.123 into an array like [1, 12.123]. .split basically goes "take this string and chop it into pieces at every ':'"
    mins = int(splits[0])
    secs = float(splits[1])
    return( (mins * 60) + secs )

#Get data from csv files
circuits = pd.read_csv('circuits.csv')
constructors = pd.read_csv('constructors.csv')
laptimes = pd.read_csv('lap_times.csv')
qualifying = pd.read_csv('qualifying.csv')
races = pd.read_csv('races.csv')

#clean data to get rid of stuff we do not need
def getQ1Times(circuitname):
    track = circuits[circuits['circuitRef'] == circuitname]
    trackID = track['circuitId'].values[0] #you need the values[0] because without it you get a pd series, not an integer, the line basically just takes the first value in that
    trackName = track['name'].values[0] 
    get_races = races[races['circuitId'] == trackID]
    get_race_ID = get_races['raceId']
    #grab every single qualifying result for every driver ever at monza
    quali = qualifying[qualifying['raceId'].isin(get_race_ID)] #.isin is just getting all the values that contain monza race id, read it as "is in" basically. IS this value IN this series? 
    quali_q1 = quali[quali['q1'] != '\\N'] #filter all DNQ
    quali_q1.loc[:, 'q1'] = quali_q1['q1'].apply(convert_to_sec) #.iloc here makes it so we're accurately replacing all the data, because otherwise we edit some things weirdly, and then the : there means all rows 
#.apply is a cool function in pandas I found that just goes "Apply this function to ALL the values"
    quali_times = quali_q1['q1']
#when plotting, we're gonna need to get dates
#this is to merge the data together, the line just says, merge q1 data with races, but only take raceId and date functions from races, and merge them on raceId, just to give us a quali series with all the dates to make plotting easier
    quali_with_date = quali_q1.merge(races[['raceId', 'date']], on='raceId', how='left')
#this edits the date function to a standardized pandas format, idk how it works, its magic
    quali_with_date['date'] = pd.to_datetime(quali_with_date['date'])
    # Plot qualifying times over time (using date)
    plt.figure(figsize=(10, 6))
    plt.scatter(quali_with_date['date'], quali_with_date['q1'], marker='o', color='r')

# Add labels and title
    plt.xlabel('Date')
    plt.ylabel('Qualifying Time (seconds)')
    plt.title(f'Qualifying Times Over Time - {trackName}')
    plt.gca().xaxis.set_major_locator(mdates.YearLocator(1))  # Set a tick every year
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))  # Format as year
    plt.xticks(rotation=45)  # Rotate the x-axis labels for better readability

# Show the plot
    plt.show()


getQ1Times('monza')
    
