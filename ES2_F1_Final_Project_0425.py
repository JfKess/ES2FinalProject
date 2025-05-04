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
    plt.savefig(f'qualifying_times_for_{circuitname}')


def manyQ1Plots(circuitname):
    track = circuits[circuits['circuitRef'] == circuitname]
    trackID = track['circuitId'].values[0]
    trackName = track['name'].values[0] 
    get_races = races[races['circuitId'] == trackID]
    get_race_ID = get_races['raceId']
    quali = qualifying[qualifying['raceId'].isin(get_race_ID)]
    quali_q1 = quali[quali['q1'] != '\\N']
    quali_q1.loc[:, 'q1'] = quali_q1['q1'].apply(convert_to_sec)
    quali_with_date = quali_q1.merge(races[['raceId', 'date']], on='raceId', how='left')
    quali_with_date['date'] = pd.to_datetime(quali_with_date['date'])
    teams = ['Mclaren', 'Williams', 'Ferrari', 'Redbull', 'RB', 'Kick-Sauber', 'Mercedes', 'Haas', 'Aston Martin', 'Alpine']
    ids = [1, 3, 6, 9, 215, 15, 131, 210, 117, 214]
    series = pd.Series(teams, index=ids)
    fig, axes = plt.subplots(nrows=5, ncols=2, figsize=(15, 20), sharex=True)
    axes = axes.flatten()
    for i, constructor_id in enumerate(ids): #this iterates through my series keeping track of the index
        team_data = quali_with_date[quali_with_date['constructorId'] == constructor_id]
        ax = axes[i]
        ax.plot(team_data['date'], team_data['q1'], marker='o', linestyle='', label=series[constructor_id])
        ax.set_title(series[constructor_id])
        ax.set_ylabel('Q1 Time (s)')
        ax.grid(True)
    plt.xlabel('Date')
    plt.suptitle(f'Q1 Times Over Time at {trackName}', fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.97])
    plt.show()
    plt.savefig(f'{circuitname}-active_teams.png')
    
def deltagraph(circuitname): #this function will take the fastest laps year to year and graph the difference in lap time year to year
    track = circuits[circuits['circuitRef'] == circuitname]
    trackID = track['circuitId'].values[0] 
    trackName = track['name'].values[0] 
    get_races = races[races['circuitId'] == trackID]
    get_race_ID = get_races['raceId']
    quali = qualifying[qualifying['raceId'].isin(get_race_ID)] 
    quali_q1 = quali[quali['q1'] != '\\N'] #filter all DNQ
    quali_q1.loc[:, 'q1'] = quali_q1['q1'].apply(convert_to_sec) 

    quali_times = quali_q1['q1']
    
    # Get the fastest lap per race (with converted times)
    quali_with_date = quali_q1.merge(races[['raceId', 'date']], on='raceId', how='left')
    fastest_laps = quali_with_date.groupby('raceId').agg({'q1': 'min'}).reset_index()
    # Merge back the race dates from quali_with_date or races
    fastest_laps = fastest_laps.merge(races[['raceId', 'date']], on='raceId', how='left')
    # Convert to datetime
    fastest_laps['date'] = pd.to_datetime(fastest_laps['date'])
    fastest_laps = fastest_laps.sort_values('date')
    # Calculate delta
    fastest_laps['delta'] = fastest_laps['q1'].diff()
    plt.scatter(fastest_laps['date'], fastest_laps['delta'], marker='o', color='r')
#     plt.bar(fastest_laps['date'], fastest_laps['delta'], width=100, color='orange')

    plt.show()
getQ1Times('monza')
deltagraph('monza')