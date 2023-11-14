% Ouassim Manout
% 13/05/2020
% Polytechnique Montréal

# Data

Census data needed for synthetic population is od two sorts: 

+ Households data (HH)
+ Persons data (P)

These datasets are dependent. Persons take part of Households. A HH can be of different types:

+ Census-family: persons related by mariage-like relation (mariage, civil law, etc.) and living under the same roof
+ Multiple-census families: a HH with two or more than one census family. Example of a family with parents and a married son or daughter living with his/her spouse in the parents' home.
+ Non-census-family: persons living together with no bold mariage like relations. Roomates are an example of such HH.

Both datasets are freely available [here](https://www12.statcan.gc.ca/census-recensement/2016/dp-pd/prof/details/download-telecharger/comp/page_dl-tc.cfm?Lang=E)

## Spatial resolution

Census data are made available by Statistics Canada at different spatial resolutions. The most detailed one is at the Dissemination Area (DA) level. The DA is the most detailed zoning for which census data is freely available. Other higher spatial resolutions exist: Census tracts, Census Subdivisions, Census division and Census Metropolitan Areas. For a complete view on these systems see [here](https://www12.statcan.gc.ca/census-recensement/2016/ref/dict/figures/f1_1-eng.cfm).

For synthetic population, we use two different spatial resolutions: 
+ Dissemination Areas (DAs) serve as local data. Synthetic population is located at this spatial level
+ Census Metropolitan Area (CMA), Census divisions (CDs) or Census Subdivisions (CSDs) to serve control levels at the regional level

The most detailed the control level, the best the fitting is. If CMA level is used, correction factors will be roughly applied to all zones inside

# Pipeline

+ Download the data
+ Data cleaning
+ Data processing: choose variables to keep and 
