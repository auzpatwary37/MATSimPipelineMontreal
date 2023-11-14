import pandas as pd
import numpy as np

import pyproj
import shapely
import geopandas as gpd

def compute_age_category(age):
    if age > 80:
        result = 16
    else:
        result = age // 5 + 1
    return result

saaq_data= pd.read_excel('SAAQ_AD_donnees_all_2016.xlsx', sheet_name="2016_csv")
saaq_data = saaq_data[:-1]
saaq_data['adidu'] = saaq_data['adidu'].astype(int)
