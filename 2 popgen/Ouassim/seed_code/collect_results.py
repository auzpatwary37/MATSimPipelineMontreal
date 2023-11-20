import pandas as pd
from os import listdir
from multiprocessing import Pool
from functools import reduce


def read_results(path):
    return pd.read_csv(path)


pattern = '2021-08'

if __name__ == "__main__":
    path = '/scratch/omanout/popgen_montreal_output_OD2016/data/'
    directories =  listdir(path)
    persons = [path + d + "/person_synthetic.csv" for d in directories if pattern in d]
    households = [path + d + "/housing_synthetic.csv" for d in directories if pattern in d]
    # weights = ["./" + d + "/weights.csv" for d in directories if pattern in d]

    proc = Pool(30)
    person_data = proc.map(read_results, persons)
    housing_data = proc.map(read_results, households)
    # weight_data = proc.map(read_results, weights)

    person_result = pd.concat(person_data, axis=0)
    person_result["unique_person_id"] = person_result.reset_index().index
    household_result = pd.concat(housing_data, axis=0)
    household_result["unique_housing_id"] = household_result.reset_index().index
    # weight_result = reduce(lambda x, y: x.add(y), weight_data)

    person_result.to_csv(path + "person_synthetic.csv", index=False)
    household_result.to_csv(path + "housing_synthetic.csv", index=False)
    # weight_result.to_csv("weights_16_19_20.csv", index=False)
