import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

# Load data
ntl_data = pd.read_csv('ntl_data.csv')
population_density_data = pd.read_csv('population_density_data.csv')
census_data = pd.read_csv('census_data.csv')
existing_aadhaar_center_data = pd.read_csv('existing_aadhaar_center_data.csv')

# Merge data
data = pd.merge(ntl_data, population_density_data, on='district')
data = pd.merge(data, census_data, on='district')
data = pd.merge(data, existing_aadhaar_center_data, on='district')

# Create rural-urban settlement map
rural_urban_map = gpd.GeoDataFrame(data, geometry=[Point(xy) for xy in zip(data['longitude'], data['latitude'])])
rural_urban_map.crs = {'init': 'epsg:4326'}

# Create Aadhaar center density map
aadhaar_center_density_map = gpd.GeoDataFrame(existing_aadhaar_center_data, geometry=[Point(xy) for xy in zip(existing_aadhaar_center_data['longitude'], existing_aadhaar_center_data['latitude'])])
aadhaar_center_density_map.crs = {'init': 'epsg:4326'}

# Define urban area algorithm
def urban_area_algorithm(data):
    # Calculate distance to nearest Aadhaar center
    data['distance_to_nearest_aadhaar_center'] = data.apply(lambda row: aadhaar_center_density_map.distance(row['geometry']).min(), axis=1)
    
    # Calculate population density
    data['population_density'] = data['population'] / data['area']
    
    # Calculate NTL index
    data['ntl_index'] = data['ntl'] / data['population']
    
    # Calculate score
    data['score'] = data['population_density'] * data['ntl_index'] * data['distance_to_nearest_aadhaar_center']
    
    return data

# Define rural area algorithm
def rural_area_algorithm(data):
    # Calculate distance to nearest Aadhaar center
    data['distance_to_nearest_aadhaar_center'] = data.apply(lambda row: aadhaar_center_density_map.distance(row['geometry']).min(), axis=1)
    
    # Calculate score
    data['score'] = data['distance_to_nearest_aadhaar_center']
    
    return data

# Apply algorithms
urban_data = urban_area_algorithm(data[data['rural_urban'] == 'urban'])
rural_data = rural_area_algorithm(data[data['rural_urban'] == 'rural'])

# Visualize results
plt.figure(figsize=(10, 10))
plt.scatter(urban_data['longitude'], urban_data['latitude'], c=urban_data['score'], cmap='Reds')
plt.scatter(rural_data['longitude'], rural_data['latitude'], c=rural_data['score'], cmap='Blues')
plt.show()

# Save results
urban_data.to_csv('urban_results.csv', index=False)
rural_data.to_csv('rural_results.csv', index=False)
