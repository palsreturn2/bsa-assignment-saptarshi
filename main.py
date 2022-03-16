#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import warnings

warnings.filterwarnings('ignore')
WORKDIR = os.getcwd()

# In[2]:


# Reading air quality sensor data obtained from CPCB platform.

from datetime import datetime
import pandas as pd

# Locations where CPCB air quality sensors are present and are collecting ground truth data

locations = [
    'Mandir Marg, Delhi - DPCC',
    'Chandni Chowk, Delhi - IITM',
    'Loni, Ghaziabad - UPPCB'
]

# Lockdown Start date 19th April

lockdown_date = datetime.strptime('19-04-2021', '%d-%m-%Y')
print('Lockdown Date: ', lockdown_date)

aq_sensor_data = pd.read_excel(WORKDIR + '/datasets/aqi_sensor_data.xlsx', header=0)
aq_sensor_data['datetime'] = pd.to_datetime(aq_sensor_data['datetime'], format='%A, %d %b %Y %I:%M %p')
print('Locations Mean AQI')
for i in range(0, len(locations)):
    print(locations[i] + "=" + str(aq_sensor_data[aq_sensor_data['name'] == locations[i]]['aqi'].mean()))
print('\nMean AQI after full lockdown period started')
for i in range(0, len(locations)):
    print(locations[i] + "=" + str(aq_sensor_data[(aq_sensor_data['name'] == locations[i])
                                                  & (aq_sensor_data['datetime'] >= lockdown_date)]['aqi'].mean()))

print('\nMean AQI before full lockdown period started')
for i in range(0, len(locations)):
    print(locations[i] + "=" + str(aq_sensor_data[(aq_sensor_data['name'] == locations[i])
                                                  & (aq_sensor_data['datetime'] < lockdown_date)]['aqi'].mean()))

# In[3]:


# Observations from the data

# Delhi lockdown dates in 2021 from April 19 onwards
# https://www.thehindu.com/news/cities/Delhi/delhi-lockdown-extended-till-may-31/article34625962.ece

# The above collected data is for the month of April 2021 for three stations.

# The highest mean AQI is for the location of Loni, Ghaziabad region.
# The mean AQI of Mandir Marg and Loni is lower before the lockdown starts.
# The mean AQI of Chandni Chowk decreases significantly during the lockdown period.


# In[4]:


# Air quality sensor locations of the three ground stations

import geopandas as gpd

gdf = gpd.read_file(WORKDIR + '/datasets/aq_stations.geojson')
gdf.head()

# In[7]:


# Region of interest: Buffer of 0.02 degrees is taken around the ground sensors.
# Assumption: Near things affect more than distant things.

gdf['geometry'] = gdf['geometry']
gdf['geometry'] = gdf['geometry'].buffer(0.02)

# In[8]:


# Mobility can be one of the factors for increase in the AQI levels.
# So one of the parameters can be density of railways and roadways.
# Fetching Highways and Railways Data

hr_gpd = gpd.read_file(WORKDIR + '/datasets/highways_railways.geojson')

# In[9]:


# Computing highway and railway line density
for i in range(0, len(locations)):
    a1 = gdf.iloc[i]
    road_density = hr_gpd['geometry'].intersection(a1['geometry']).length
    print('Road Density Values')
    print(a1['name'] + '=' + str(road_density.sum()))

# In[10]:


# Observations from the Road Density Values

# Mandir Marg has the maximum highway and railway density in the region.
# Loni, Ghaziabad has the least highway and railway density in the region.


# In[11]:


# Forest cover is another important indicator for AQI levels.
# Loading Forest Layer

for_gpd = gpd.read_file(WORKDIR + '/datasets/forests.geojson')
for_gpd['geometry'] = for_gpd['geometry'].buffer(0)

# In[12]:


# Computing Forest density
for i in range(0, len(locations)):
    a1 = gdf.iloc[i]
    forest_density = for_gpd['geometry'].intersection(a1['geometry']).area
    print('Forest density')
    print(a1['name'] + '=' + str(forest_density.sum()))

# In[13]:


# Observations from the Forest Density Analysis

# Mandir Marg has the highest forest density cover.
# Loni Ghaziabad has the least forest density cover.


# In[14]:


# Industries are another important indicator for the AQI levels.
# Density of industries is another parameter for the analysis.
# Loading Industries Layer

ind_gpd = gpd.read_file(WORKDIR + '/datasets/industrial.geojson')
ind_gpd['geometry'] = ind_gpd['geometry'].buffer(0)

# In[15]:


# Computing Industrial density
for i in range(0, len(locations)):
    a1 = gdf.iloc[i]
    print('Industry density')
    ind_density = ind_gpd['geometry'].intersection(a1['geometry']).area
    print(a1['name'] + '=' + str(ind_density.sum()))

# In[16]:


# Observations from the industries layer

# Mandir marg has highest density of industries among the other two regions.


# In[17]:


# Loading aerosol data and the distance arrays

from osgeo import gdal_array
import numpy as np

dataset = pd.DataFrame()

aerosolArray = np.array(gdal_array.LoadFile(WORKDIR + '/datasets/aerosol_layer.tif'))
dataset['aerosol'] = np.ndarray.flatten(aerosolArray)

dist_forest = np.array(gdal_array.LoadFile(WORKDIR + '/datasets/dist_from_forests.tif'))
dataset['dforest'] = np.ndarray.flatten(dist_forest)

dist_highways = np.array(gdal_array.LoadFile(WORKDIR + '/datasets/dist_from_highways.tif'))
dataset['dhighways'] = np.ndarray.flatten(dist_highways)

dist_industries = np.array(gdal_array.LoadFile(WORKDIR + '/datasets/dist_from_industries.tif'))
dataset['dindustries'] = np.ndarray.flatten(dist_industries)

dataset = dataset[dataset['aerosol'] > aerosolArray.min()]

# Finding Correlation between the proximity from different features and aerosol levels.

print('Aerosol-Proximity from Forests: ', dataset['aerosol'].corr(dataset['dforest'], method='pearson'))
print('Aerosol-Proximity from Highways: ', dataset['aerosol'].corr(dataset['dhighways'], method='pearson'))
print('Aerosol-Proximity from Industries: ', dataset['aerosol'].corr(dataset['dindustries'], method='pearson'))

# In[18]:


# Observations

# The pearson correlation between aerosol and distance from forests is the highest. This
# indicates that there is a positive and stronger linear relationship between aerosol 
# levels and proximity of forests than with industries and highways.


# In[19]:


# Summary of Observations from the analysis

# The highest mean AQI is for the location of Loni, Ghaziabad region.
# The mean AQI of Mandir Marg and Loni is lower before the lockdown starts.
# The mean AQI of Chandni Chowk decreases significantly during the lockdown period.

# Mandir Marg has the maximum highway and railway density in the region.
# Loni, Ghaziabad has the least highway and railway density in the region.

# Mandir Marg has the highest forest density cover.
# Loni Ghaziabad has the least forest density cover.

# Mandir marg has highest density of industries among the other two regions.

# The pearson correlation between aerosol and distance from forests is the highest. This
# indicates that there is a positive and stronger linear relationship between aerosol 
# levels and proximity of forests than with industries and highways.

# Conclusions

# The decrease in mean AQI in Chandni Chowk is possibly because of the presence of forest
# and absence of industry together.


# In[ ]:
