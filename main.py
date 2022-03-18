#!/usr/bin/env python
# coding: utf-8

# In[2]:


import os
import warnings
warnings.filterwarnings('ignore')
WORKDIR = os.getcwd()


# In[3]:


# Reading air quality sensor data obtained from CPCB platform.

from datetime import datetime
import pandas as pd

# Air quality sensor locations of the three ground stations

import geopandas as gpd
gdf = gpd.read_file(WORKDIR+'/datasets/aq_stations.geojson')

locations = gdf['name']
print(locations)

#Lockdown Start date 19th April

lockdown_date = datetime.strptime('19-04-2021', '%d-%m-%Y')
print('Lockdown Date: ',lockdown_date)

aq_sensor_data = pd.read_excel(WORKDIR+'/datasets/aqi_sensor_data.xlsx', header=0)  
aq_sensor_data['datetime'] = pd.to_datetime(aq_sensor_data['datetime'], format='%A, %d %b %Y %I:%M %p')
print('Locations Mean AQI')
for i in range(0, len(locations)):
    print(locations[i]+"="+str(aq_sensor_data[aq_sensor_data['name']==locations[i]]['aqi'].mean()))
print('\nMean AQI after full lockdown period started')
for i in range(0, len(locations)):
    print(locations[i]+"="+str(aq_sensor_data[(aq_sensor_data['name']==locations[i]) 
                                              & (aq_sensor_data['datetime']>=lockdown_date)]['aqi'].mean()))

print('\nMean AQI before full lockdown period started')
for i in range(0, len(locations)):
    print(locations[i]+"="+str(aq_sensor_data[(aq_sensor_data['name']==locations[i]) 
                                              & (aq_sensor_data['datetime']<lockdown_date)]['aqi'].mean()))


# In[4]:


# Observations from the data

# Delhi lockdown dates in 2021 from April 19 onwards
# https://www.thehindu.com/news/cities/Delhi/delhi-lockdown-extended-till-may-31/article34625962.ece

# The above collected data is for the month of April 2021 for three stations.

# The highest mean AQI is for the location of Loni, Ghaziabad region.
# The mean AQI of Mandir Marg and Loni is lower before the lockdown starts.
# The mean AQI of Chandni Chowk decreases significantly during the lockdown period.


# In[5]:


# Region of interest: Buffer of 0.02 degrees is taken around the ground sensors.
# Assumption: Near things affect more than distant things.

gdf['geometry'] = gdf['geometry']
gdf['geometry'] = gdf['geometry'].buffer(0.02)


# In[6]:


# Mobility can be one of the factors for increase in the AQI levels.
# So one of the parameters can be density of railways and roadways.
# Fetching Highways and Railways Data

hr_gpd = gpd.read_file(WORKDIR+'/datasets/highways_railways.geojson')


# In[7]:


#Computing highway and railway line density
for i in range(0, len(locations)):
    a1 = gdf.iloc[i]    
    road_density = hr_gpd['geometry'].intersection(a1['geometry']).length
    print('Road Density Values')
    print(a1['name']+'='+str(road_density.sum()))


# In[8]:


# Observations from the Road Density Values

# Mandir Marg has the maximum highway and railway density in the region.
# Loni, Ghaziabad has the least highway and railway density in the region.


# In[9]:


# Forest cover is another important indicator for AQI levels.
# Loading Forest Layer

for_gpd = gpd.read_file(WORKDIR+'/datasets/forests.geojson')
for_gpd['geometry'] = for_gpd['geometry'].buffer(0)


# In[10]:


#Computing Forest density
for i in range(0, len(locations)):
    a1 = gdf.iloc[i]
    forest_density = for_gpd['geometry'].intersection(a1['geometry']).area
    print('Forest density')
    print(a1['name']+'='+str(forest_density.sum()))


# In[11]:


# Observations from the Forest Density Analysis

# Mandir Marg has the highest forest density cover.
# Loni Ghaziabad has the least forest density cover.


# In[12]:


# Industries are another important indicator for the AQI levels.
# Density of industries is another parameter for the analysis.
# Loading Industries Layer

ind_gpd = gpd.read_file(WORKDIR+'/datasets/industrial.geojson')
ind_gpd['geometry'] = ind_gpd['geometry'].buffer(0)


# In[13]:


#Computing Industrial density
for i in range(0, len(locations)):
    a1 = gdf.iloc[i]
    print('Industry density')
    ind_density = ind_gpd['geometry'].intersection(a1['geometry']).area
    print(a1['name']+'='+str(ind_density.sum()))


# In[14]:


# Observations from the industries layer

# Mandir marg has highest density of industries among the other two regions.


# In[15]:


# Firespots data analysis
import numpy as np

firespots = gpd.read_file(WORKDIR+'/datasets/firespots.geojson')

firespots['acq_date'] = pd.to_datetime(firespots['acq_date'], format='%Y-%m-%d')


def compute_distances(reg, df1):
    dists = []
    for i, centr in df1.centroid.iteritems():
        dist = centr.distance(reg.geometry.centroid)
        dists.append(dist)        
    return np.array(dists)

print('During Lockdown Stages')
firespots_lockdown = firespots[firespots['acq_date']>lockdown_date]
print('Total number of firespots: ', firespots_lockdown['acq_date'].count())
print('Min Distance of fires from '+locations[0]+': '+str(compute_distances(gdf.iloc[0], firespots_lockdown).min()))
print('Min Distance of fires from '+locations[1]+': '+str(compute_distances(gdf.iloc[1], firespots_lockdown).min()))
print('Min Distance of fires from '+locations[2]+': '+str(compute_distances(gdf.iloc[2], firespots_lockdown).min()))
print('During no lockdown Stages')
firespots_nolockdown = firespots[firespots['acq_date']<lockdown_date]
print('Total number of firespots: ', firespots_nolockdown['acq_date'].count())
print('Min Distance of fires from '+locations[0]+': '+str(compute_distances(gdf.iloc[0], firespots_nolockdown).min()))
print('Min Distance of fires from '+locations[1]+': '+str(compute_distances(gdf.iloc[1], firespots_nolockdown).min()))
print('Min Distance of fires from '+locations[2]+': '+str(compute_distances(gdf.iloc[2], firespots_nolockdown).min()))


# In[16]:


# Observations:

# Firespots are near to Chandni Chowk, Delhi - IITM station than others.
# Number of firespots during the lockdown is more than during no lockdown.


# In[17]:


# Loading aerosol data and the distance arrays

from osgeo import gdal_array
import numpy as np

dataset = pd.DataFrame()

aerosolArray = np.array(gdal_array.LoadFile(WORKDIR+'/datasets/aerosol_layer0401.tif'))
dataset['aerosol01'] = np.ndarray.flatten(aerosolArray)
cloudCover01 =  0.03 # Metadata: Land Cloud cover collected from the Landsat Website

aerosolArray = np.array(gdal_array.LoadFile(WORKDIR+'/datasets/aerosol_layer0424.tif'))
dataset['aerosol24'] = np.ndarray.flatten(aerosolArray)
cloudCover24 = 41.56 # Metadata: Land Cloud cover collected from the Landsat Website

dist_forest = np.array(gdal_array.LoadFile(WORKDIR+'/datasets/dist_from_forests.tif'))
dataset['dforest'] = np.ndarray.flatten(dist_forest)

dist_highways = np.array(gdal_array.LoadFile(WORKDIR+'/datasets/dist_from_highways.tif'))
dataset['dhighways'] = np.ndarray.flatten(dist_highways)

dist_industries = np.array(gdal_array.LoadFile(WORKDIR+'/datasets/dist_from_industries.tif'))
dataset['dindustries'] = np.ndarray.flatten(dist_industries)

dataset = dataset[dataset['aerosol01']>aerosolArray.min()]
dataset = dataset[dataset['aerosol24']>aerosolArray.min()]

# Comparing the aerosol levels
# Finding Correlation between the proximity from different features and aerosol levels.
print('\nAerosol Levels before lockdown')
print('Mean aerosol level: ', dataset['aerosol01'].mean())
print('Aerosol-Proximity from Forests: ',dataset['aerosol01'].corr(dataset['dforest'], method='pearson'))
print('Aerosol-Proximity from Highways: ',dataset['aerosol01'].corr(dataset['dhighways'], method='pearson'))
print('Aerosol-Proximity from Industries: ',dataset['aerosol01'].corr(dataset['dindustries'], method='pearson'))
print('\nAerosol Levels after lockdown')
print('Mean aerosol level: ', dataset['aerosol24'].mean())
print('Aerosol-Proximity from Forests: ',dataset['aerosol24'].corr(dataset['dforest'], method='pearson'))
print('Aerosol-Proximity from Highways: ',dataset['aerosol24'].corr(dataset['dhighways'], method='pearson'))
print('Aerosol-Proximity from Industries: ',dataset['aerosol24'].corr(dataset['dindustries'], method='pearson'))


# In[18]:


# Observations

# Mean aerosol levels are higher during the lockdown period.
# The cloud cover during the period of lockdown is higher than during no lockdown. 
# The pearson correlation between aerosol and proximity from forests is higher during no lockdown.
# The pearson correlation between aerosol and proximity from highways is negative during no lockdown.
# The pearson correlation between aerosol and proximity from highways is positive and higher during lockdown.


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

# Firespots are near to Chandni Chowk, Delhi - IITM station than others.
# Number of firespots during the lockdown is more than during no lockdown.

# Mean aerosol levels are higher during the lockdown period.
# The cloud cover during the period of lockdown is higher than during no lockdown. 
# The pearson correlation between aerosol and proximity from forests is higher during no lockdown.
# The pearson correlation between aerosol and proximity from highways is negative during no lockdown.
# The pearson correlation between aerosol and proximity from highways is positive and higher during lockdown.

# Conclusions

# With increase in the number of fire occurrences, the Mean aerosol levels can rise.
# With increase in distance from forest cover, the aerosol levels also increase.
# Even when there is limited mobility, the aerosol levels can be higher because of nearby fires and absence of forest cover.


# In[ ]:




