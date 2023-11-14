import geopandas as gpd
from shapely.geometry import box

import pandas as pd
import numpy as np
import os

lda_filelocation = '/Users/ashrafzaman/matsim_pipelines/DataDonwloaded/Shapes/lda_000b21a_e/lda_000b21a_e.shp'
lct_filelocation = '/Users/ashrafzaman/matsim_pipelines/DataDonwloaded/Shapes/lct_000b21a_e/lct_000b21a_e.shp'
da_census_file_location = "/Users/ashrafzaman/matsim_pipelines/DataDonwloaded/2022/98-401-X2021006_Quebec_eng_CSV/98-401-X2021006_English_CSV_data_Quebec.csv"
ct_census_file_location = "/Users/ashrafzaman/matsim_pipelines/DataDonwloaded/2022/98-401-X2021007_eng_CSV/98-401-X2021007_English_CSV_data.csv"
saaq_file_location = "/Users/ashrafzaman/matsim_pipelines/DataDonwloaded/saaq/SAAQ_AD_donnees_all_2016.xlsx"


path = "output/"
# Check whether the specified path exists or not
isExist = os.path.exists(path)

if not isExist:

   # Create a new directory because it does not exist
   os.makedirs(path)
   print("output directory is created!")

da = gpd.read_file(lda_filelocation)
ca = gpd.read_file(lct_filelocation)


# The boundary shapefiles are avaialable at 
# https://www12.statcan.gc.ca/census-recensement/2021/geo/sip-pis/boundary-limites/index2021-eng.cfm?year=21

# Download the 2021 dessimination area (lda) and census (lct) tract 

da.to_crs(epsg = 32188, inplace = True)
ca.to_crs(epsg = 32188, inplace = True)
minx=232018.46167784795
miny=4998356.443671201
maxx=341483.2997932121
maxy=5097791.967859513
da_clipped = da.cx[minx:maxx,miny:maxy]
ca_clipped = ca.cx[minx:maxx,miny:maxy]

#da.plot()
#da_clipped.plot()

inter = gpd.overlay(da_clipped, ca_clipped, how='intersection')
inter.plot()
inter.rename(columns={'DGUID_1':'DGUID_DA','PRUID_1':'PRUID','LANDAREA_1':'LANDAREA_DA','LANDAREA_2':'LANDAREA_CT','DGUID_2':'DGUID_CT'},inplace=True)
inter.drop('PRUID_2',axis=1)
inter.sort_values(by=['DAUID'])
inter['geo'] = list(range(len(inter)))#this is the new da id or in popgen term geo, i.e., the smaller area
inter['region']=inter.groupby(['CTUID']).ngroup()#this is the new ct id or in popgen term region, i.e., the larger area
inter.keys()
inter_new= inter[['DAUID','CTUID','PRUID', 'geo', 'region','DGUID_DA', 'DGUID_CT',
       'CTNAME', 'LANDAREA_DA','LANDAREA_CT', 'geometry']]
inter_new.to_file('output/geoFilter.shp')
inter_new[['region','geo']].to_csv('output/region_geo.csv',index = False)

# I use SAAQ data on driving license and car ownerships to compute marginals for the population at the dissemination area level of resolution. 
# These data have been made available by Jérôme Laviolette (Catherine's team). Jérôme got the data from SAAQ via simple email request. OUASSIM 2022

#The dataset has been recovered from Sarah's Email. Ashraf, Jan 23.

inter_new.DAUID = inter_new.DAUID.astype(int)
inter_new.CTUID = inter_new.CTUID.astype(float)

def compute_age_category(age):
    if age > 80:
        result = 16
    else:
        result = age // 5 + 1
    return result

saaq_data= pd.read_excel(saaq_file_location, sheet_name="2016_csv")

saaq_data1 = saaq_data[:-1]
saaq_data1['adidu'] = saaq_data1['adidu'].astype(int)
saaq_data1

saaq_data = saaq_data[saaq_data.adidu.isin(inter.DAUID)]
saaq_data.drop(columns=['auto_elec','auto_conv', 'camleg_elec', 'camleg_conv', 'nonprec_elec','nonprec_conv', 'auto_tot', 'camleg_tot', 'nonprec_tot', 'elec_tot','conv_tot',
                        'commentaires'], inplace=True)

saaq_data.rename(columns={"permis_h":"license_sex_1", "permis_f": "license_sex_2", "permis_tot": "license", "nbadr_1permis": "hh_driving_license_1", "nbadr_2permis": "hh_driving_license_2",
                          "nbadr_3permis": "hh_driving_license_3", "nbadr_4pluspermis": "hh_driving_license_4", "tot_veh": "hh_car", "nbadr_1pau": "hh_car_1", "nbadr_2pau": "hh_car_2",
                          "nbadr_3pau": "hh_car_3", "nbadr_4pluspau": "hh_car_4"}, inplace=True)

saaq_data.fillna(np.random.randint(1,6), inplace=True)

saaq_data = saaq_data.merge(inter, left_on="adidu", right_on="DAUID")
saaq_data[['DAUID', 'CTUID','geo','region', 'license', 'license_sex_1', 'license_sex_2']].to_csv("output/person_license_sex.csv", index=False)
saaq_data[['DAUID', 'CTUID','geo','region', 'hh_driving_license_1', 'hh_driving_license_2', 'hh_driving_license_3', 
           'hh_driving_license_4','hh_car_1', 'hh_car_2', 'hh_car_3', 'hh_car_4', 'hh_car']].to_csv("output/hh_car_license.csv", index=False)

#Read the DA census data 

# CENSUS DATA

# Source: https://www12.statcan.gc.ca/census-recensement/2021/dp-pd/prof/details/download-telecharger.cfm?Lang=E&SearchText=Quebec&DGUIDlist=2021A000224&GENDERlist=1,2,3&STATISTIClist=1&HEADERlist=0 

# Date: 10/01/2023

# Download the following files for DA and CT files and extract to generate the input data for this class 

# Canada, provinces, territories, census divisions (CDs), census subdivisions (CSDs) and dissemination areas (DAs) - Quebec only

# and 

# Census metropolitan areas (CMAs), tracted census agglomerations (CAs) and census tracts (CTs)

# cite: 
# Statistics Canada. 2022. (table). Census Profile. 2021 Census of Population. Ottawa. Released December 15, 2022.
# https://www12.statcan.gc.ca/census-recensement/2021/dp-pd/prof/details/download-telecharger.cfm?Lang=E&SearchText=Quebec&DGUIDlist=2021A000224&GENDERlist=1,2,3&STATISTIClist=1&HEADERlist=0 (accessed January 10, 2023).

# ashraf, Jan 23

## Households(HH)
# + HH size
# + HH type (not available in the OD of Montreal)
# + HH income
# + HH number of cars (not available in census data). SAAQ provides data on car fleet with no association to persons or HH

# ### Household size
# - 1 person (standard column name in the census data 52)
# - 2 persons (53)
# - 3 persons (54)
# - 4 persons (55)
# - 5 persons and more (56)

# ### Household type (Sample data do not include clear information on households types, we shall use a simple HH type based on the presence of children in the HH. The presence of kids has an impact on travel behaviour of some members of the HH)
# - Presence of children: yes
# - Presence of children: no

# ### Household income

# Different income sources are included in the census: Employment income, before/after tax income, etc. I use the HH total income (lines 261 to 280). To match this income with the sample income variable, one should check the definition of the  sample income.
 
# Household income ($)
# - \< 30,000
# - 30,000 - 59,999
# - 60,000 - 89,999
# - 90,000 - 149,999
# - \> 150,000

# Census data must be grouped to match the income brackets above

# + 261	  Under $5,000
# + 262	  $5,000 to $9,999
# + 263	  $10,000 to $14,999
# + 264	  $15,000 to $19,999
# + 265	  $20,000 to $24,999
# + 266	  $25,000 to $29,999
# + 267	  $30,000 to $34,999
# + 268	  $35,000 to $39,999
# + 269	  $40,000 to $44,999
# + 270	  $45,000 to $49,999
# + 271	  $50,000 to $59,999
# + 272	  $60,000 to $69,999
# + 273	  $70,000 to $79,999
# + 274	  $80,000 to $89,999
# + 275	  $90,000 to $99,999
# + 276	  $100,000 and over
# + 277	  $100,000 to $124,999
# + 278	  $125,000 to $149,999
# + 279	  $150,000 to $199,999
# + 280	  $200,000 and over``

iter_csv = pd.read_csv(da_census_file_location, iterator=True, chunksize=2631,encoding='latin-1')
df_hh_da = pd.DataFrame(columns=['DIUID','geo','hh_size1','hh_size2','hh_size3','hh_size4','hh_size5','hh_type1','hh_type2','hh_income1','hh_income2','hh_income3','hh_income4','hh_income5','total_hh'])
df_per_da = pd.DataFrame(columns = ['DIUID','geo','age1','age2','age3','age4','age5','age6','age7','age8','age9','age10','age11',
'age12','age13','age14','age15','age16','sex_male','sex_female','occupation_full_time','occupation_part_time','occupation_unemployed','occupation_not_applicable','workplace_from_home','workplace_outside','workplace_not_applicable','total_person'])
for chunk_or in iter_csv:
    chunk = chunk_or.copy()
    chunk = chunk[chunk.ALT_GEO_CODE.astype(int).isin(inter_new.DAUID)]
    if len(chunk)!=0:
        a = []
        b = []
        chunk = chunk.set_index('CHARACTERISTIC_ID',inplace=False)
        DIUID = chunk['ALT_GEO_CODE'][1]
        a.append(DIUID)#add duid
        b.append(DIUID)
        geo_id = inter_new[inter_new.DAUID==DIUID].reset_index().loc[0]['geo']
        a.append(geo_id)#add geoId
        b.append(geo_id)
        a.extend(list(chunk.iloc[51:55+1]['C1_COUNT_TOTAL']))#add household size 1-5 51-55
        a.append(chunk.iloc[101]['C1_COUNT_TOTAL']+chunk.iloc[104]['C1_COUNT_TOTAL'])#add hh without kids 101 and 104
        a.append(chunk.iloc[103]['C1_COUNT_TOTAL']+chunk.iloc[105]['C1_COUNT_TOTAL'])#add hh with kids 103 and 105
        
        a.append(sum(chunk[261:266+1]['C1_COUNT_TOTAL']))#hh income less than 30000 row 261-266
        a.append(sum(chunk.iloc[267:271+1]['C1_COUNT_TOTAL']))#hh income 30000-60000 row 267-271
        a.append(sum(chunk.iloc[272:274+1]['C1_COUNT_TOTAL']))#hh income 60000-90000 row 272-274
        a.append(sum(chunk.iloc[275:278+1]['C1_COUNT_TOTAL'])-chunk.iloc[276]['C1_COUNT_TOTAL'])#hh income 90000-150000 row 275-278 but row 276 must be deducted
        a.append(sum(chunk.iloc[279:280+1]['C1_COUNT_TOTAL']))#hh income 90000-150000 row 279-280
        a.append(chunk.iloc[50]['C1_COUNT_TOTAL'])#Keeping the total count of hh as well
        #print(a)
        df_hh_da.loc[len(df_hh_da)] = a
        #print(df_hh_da)
        #age for population

        b.extend(list(chunk.iloc[10:12+1]['C1_COUNT_TOTAL']))#age 5-14
        b.extend(list(chunk.iloc[14:23+1]['C1_COUNT_TOTAL']))#age15-64
        b.extend(list(chunk.iloc[25:26+1]['C1_COUNT_TOTAL']))#age65-74
        b.append(sum(chunk.iloc[27:29+1]['C1_COUNT_TOTAL']))#age 75 and above
        #sex for population
        b.append(chunk.iloc[1]['C2_COUNT_MEN+'])#number of men
        b.append(chunk.iloc[1]['C3_COUNT_WOMEN+'])#number of women
        #occupation for population
        b.append(chunk.iloc[2234]['C1_COUNT_TOTAL'])#Full time work
        b.append(chunk.iloc[2235]['C1_COUNT_TOTAL'])#part time work

        b.append(chunk.iloc[2232]['C1_COUNT_TOTAL'])#did not work
        b.append(chunk.iloc[2238]['C1_COUNT_TOTAL'])#not applicable

        #workplace for population
        b.append(chunk.iloc[2594]['C1_COUNT_TOTAL'])#from home
        b.append(chunk.iloc[2596]['C1_COUNT_TOTAL']+chunk.iloc[2597]['C1_COUNT_TOTAL'])#outside home
        b.append(chunk.iloc[2595]['C1_COUNT_TOTAL'])#not applicable
        b.append(chunk.iloc[1]['C1_COUNT_TOTAL'])#kept the total population for normalization
        df_per_da.loc[len(df_per_da)] = b

df_per_da = df_per_da.merge(saaq_data[['geo','license']],on='geo',how='outer')
len(saaq_data['region'].unique())

df_new = df_hh_da.drop(['DIUID'],axis=1)
df_new.geo = df_new.geo.astype(int)
df_new.to_csv('output/hh_geo_marginal.csv', index = False)


df_new = df_per_da.drop(['DIUID'],axis=1)

df_new.geo = df_new.geo.astype(int)
df_new.to_csv('output/pp_geo_marginal.csv', index = False)

#CT levle hh data read

iter_csv = pd.read_csv(ct_census_file_location, iterator=True, chunksize=2631,encoding='latin-1')
df_hh_ct = pd.DataFrame(columns=['CTUID','region','hh_size1','hh_size2','hh_size3','hh_size4','hh_size5','hh_type1','hh_type2','hh_income1','hh_income2','hh_income3','hh_income4','hh_income5'])
df_per_ct = pd.DataFrame(columns = ['CTUID','region','age1','age2','age3','age4','age5','age6','age7','age8','age9','age10','age11',
'age12','age13','age14','age15','age16','sex_male','sex_female','occupation_full_time','occupation_part_time','occupation_unemployed','occupation_not_applicable','workplace_from_home','workplace_outside','workplace_not_applicable','total_person'])

for chunk_or in iter_csv:
    chunk = chunk_or.copy()
    if len(chunk[chunk.ALT_GEO_CODE.astype(float).isin(inter_new.CTUID.astype(float))])!=0:
        a=[]
        b=[]
        chunk = chunk.set_index('CHARACTERISTIC_ID',inplace=False)
        CTUID = chunk['ALT_GEO_CODE'][1].astype(float)
        a.append(CTUID)#add duid
        b.append(CTUID)
        region_id = inter_new[inter_new.CTUID.astype(float).isin(chunk.ALT_GEO_CODE.astype(float))].reset_index().loc[0]['region']
        a.append(region_id)#add geoId
        b.append(region_id)
        a.extend(list(chunk.iloc[51:55+1]['C1_COUNT_TOTAL']))#add household size 1-5 51-55
        a.append(chunk.iloc[101]['C1_COUNT_TOTAL']+chunk.iloc[104]['C1_COUNT_TOTAL'])#add hh without kids 101 and 104
        a.append(chunk.iloc[103]['C1_COUNT_TOTAL']+chunk.iloc[105]['C1_COUNT_TOTAL'])#add hh with kids 103 and 105
        
        a.append(sum(chunk[261:266+1]['C1_COUNT_TOTAL']))#hh income less than 30000 row 261-266
        a.append(sum(chunk.iloc[267:271+1]['C1_COUNT_TOTAL']))#hh income 30000-60000 row 267-271
        a.append(sum(chunk.iloc[272:274+1]['C1_COUNT_TOTAL']))#hh income 60000-90000 row 272-274
        a.append(sum(chunk.iloc[275:278+1]['C1_COUNT_TOTAL'])-chunk.iloc[276]['C1_COUNT_TOTAL'])#hh income 90000-150000 row 275-278 but row 276 must be deducted
        a.append(sum(chunk.iloc[279:280+1]['C1_COUNT_TOTAL']))#hh income 90000-150000 row 279-280
        #print(a)
        df_hh_ct.loc[len(df_hh_ct)] = a
        
        b.extend(list(chunk.iloc[10:12+1]['C1_COUNT_TOTAL']))#age 5-14
        b.extend(list(chunk.iloc[14:23+1]['C1_COUNT_TOTAL']))#age15-64
        b.extend(list(chunk.iloc[25:26+1]['C1_COUNT_TOTAL']))#age65-74
        b.append(sum(chunk.iloc[27:29+1]['C1_COUNT_TOTAL']))#age 75 and above
        #sex for population
        b.append(chunk.iloc[1]['C2_COUNT_MEN+'])#number of men
        b.append(chunk.iloc[1]['C3_COUNT_WOMEN+'])#number of women
        #occupation for population
        b.append(chunk.iloc[2234]['C1_COUNT_TOTAL'])#Full time work
        b.append(chunk.iloc[2235]['C1_COUNT_TOTAL'])#part time work

        b.append(chunk.iloc[2232]['C1_COUNT_TOTAL'])#did not work
        b.append(chunk.iloc[2238]['C1_COUNT_TOTAL'])#not applicable

        #workplace for population
        b.append(chunk.iloc[2594]['C1_COUNT_TOTAL'])#from home
        b.append(chunk.iloc[2596]['C1_COUNT_TOTAL']+chunk.iloc[2597]['C1_COUNT_TOTAL'])#outside home
        b.append(chunk.iloc[2595]['C1_COUNT_TOTAL'])#not applicable
        b.append(chunk.iloc[1]['C1_COUNT_TOTAL'])#kept the total population for normalization
        
        df_per_ct.loc[len(df_per_ct)] = b
        #print(df_hh_da)

df_new = df_hh_ct.drop(['CTUID'],axis=1)
df_new.region = df_new.region.astype(int)
df_new.to_csv('output/hh_region_marginal.csv', index = False)

df_per_ct = df_per_ct.merge(saaq_data[['region','license']].groupby('region').sum(),on='region',how='outer')
df_new = df_per_ct.drop(['CTUID'],axis=1)

df_new.region = df_new.region.astype(float)
df_new.to_csv('output/pp_region_marginal.csv', index = False)


