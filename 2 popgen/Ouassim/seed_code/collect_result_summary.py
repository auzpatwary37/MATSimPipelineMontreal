import pandas as pd
from os import listdir
from multiprocessing import Pool
from functools import reduce


def read_results(path):
    return pd.read_csv(path, skiprows=[1, 2])


pattern = '2020'

if __name__ == "__main__":
    directories =  listdir('./')
    persons = ["./" + d + "/summary_geo.csv" for d in directories if pattern in d]
    proc = Pool(8)
    person_data = proc.map(read_results, persons)

    person_result = pd.concat(person_data, axis=0)

    person_result.to_csv("summary_geo.csv", index=False)
