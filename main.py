import pandas as pd
import csv
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon
import numpy as np
import prepare
from wordcloud import WordCloud
from PIL import Image

plt.rcParams['figure.dpi'] = 300


def read_tab_delimited_file_pandas(file_path):
    """
    Reads data from a tab-delimited text file using pandas.

    Args:
        file_path (str): The path to the tab-delimited text file.

    Returns:
        pandas.DataFrame: A pandas DataFrame containing the data, or None if an error occurs.
    """
    data = []
    try:
        with open(file_path, 'r') as file:
            tab_reader = csv.reader(file, delimiter='\t')
            for row in tab_reader:
                data.append(row)
    except FileNotFoundError:
        print(f"Error: File not found at path: {file_path}")
        return None
    except Exception as e:
         print(f"An error occurred: {e}")
         return None
    return data

# read file into dataframe
file_path = 'incident_gas_transmission_gathering_jan2010_present.txt'
data = read_tab_delimited_file_pandas(file_path)        
df = pd.DataFrame(data[1:], columns=data[0])
# create geospatial data from Latitude and Longitude
df['Latitude'] = df['LOCATION_LATITUDE'].astype(float)
df['Longitude'] = df['LOCATION_LONGITUDE'].astype(float)
geometry = [Point(xy) for xy in zip(df['Longitude'], df['Latitude'])]
crs = {'init':'epsg:4326'}
geo_df = gpd.GeoDataFrame(df, #specify our data
                          crs=crs, #specify our coordinate reference system
                          geometry=geometry) #specify the geometry list we created

# scale fatality data for visual purposes
geo_df['FATAL_SCALED'] = np.where(geo_df['FATAL'] == '0', '.1', geo_df['FATAL'])

# read shape file of U.S.
us_map = gpd.read_file('cb_2023_us_state_500k.shp')

# plot shp file and incident data on the same plot
fig, ax = plt.subplots(figsize=(15,15))
us_map.plot(ax=ax, alpha=0.2, edgecolor='k')
fatal = geo_df[geo_df['FATAL'].astype(float) > 0.0]
non_fatal = geo_df[geo_df['FATAL'] == '0']
non_fatal.plot(ax=ax, markersize=non_fatal['FATAL_SCALED'].astype(float)*100, color='blue', marker='o', label='Non-Fatality', alpha=0.6)
fatal.plot(ax=ax, markersize=fatal['FATAL_SCALED'].astype(float)*100, color='red', marker='o', label='Fatality', alpha=0.6)

# format plot
plt.ylim([20, 55])
plt.xlim([-130, -65])
plt.axis('off')
# Font properties dictionary
font = {'family': 'sans-serif',
        'color':  'black', # Color name or hex code
        'weight': 'bold', # e.g., 'normal', 'bold', 'light'
        'size': 24, # Font size in points
        'style': 'normal' # e.g., 'normal', 'italic', 'oblique'
        }
plt.title('Pipeline Incidents (2010-2024)', fontsize=24, fontdict=font)

# word cloud of incident causes
df['CAUSE_DETAILS'] = df['CAUSE_DETAILS'].str.replace(' ', '')
cause_text = (df['ONSHORE_STATE_ABBREVIATION'].str.cat(sep=' '))
usa_mask = np.array(Image.open('us_mask.jpg'))
wc = WordCloud(background_color = '#FFFFFF', mask = usa_mask, contour_width = 1,
     contour_color = 'black', colormap = 'bone').generate(cause_text)
plt.axis('off')
plt.imshow(wc)



