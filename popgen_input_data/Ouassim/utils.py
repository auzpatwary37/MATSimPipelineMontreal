import pandas as pd
import numpy as np


def round_to_integer(value, seed=0):
    np.random.seed = seed
    integer_part = int(value)
    diff = abs(value - integer_part)
    if np.random.rand() > diff:
        return integer_part
    else:
        return integer_part + 1


def transpose_df(df, keep_all=False):
    df = df.copy()
    df['variable'] = df['variable'].astype(str)
    df.index = df['variable']
    df.drop(columns=['variable'], inplace=True)
    if keep_all:
        result = df.transpose()
    else:
        result = df[['value']].transpose()
    return result


def find_nearest_zone(data, zone):
    """
    Return the codes of the four nearest dissemination areas to da_code
    """
    neighbors = list(set(data.index.get_level_values(level=0)))
    neighbors.sort()
    index = neighbors.index(zone)
    if index == 0:
        index += 2
    if index == len(neighbors) - 1:
        index -= 2
    neighbors.remove(zone)
    return neighbors[index - 2:index + 2]


def format_variable(variable):
    if variable[1] == 1:
        return [variable[0]]
    else:
        radical = variable[0] + "_"
        return [radical + str(i) for i in range(1, variable[1] + 1)]


def compute_probability_distribution(data, variable):
    variable_cat = format_variable(variable)
    return data.loc[:, variable_cat].div(data.loc[:, variable_cat].sum(axis=1), axis=0)


def compute_average_probability_distribution(data, zone_code, variable):
    """
    Compute the probability distribition of variable X using the 4 nearest zones to zone code
    :param: data: dataframe of data of length > 1
    :params: zone_code: zone geographic code. Example Dissemination area 24663119
    :params: variable: Tuple of variable name and upper bound category. Example ("hh_size", 5).
    return list of probability distribution of the same length as the given upper limit
    """
    neighbors = data.loc[find_nearest_zone(data, zone_code)]
    if isinstance(data.index, pd.MultiIndex):  # DF with multiindex
        level = 1
    else:
        level = None
    return compute_probability_distribution(neighbors, variable).mean(level=level)  # Average probability distribution over the 4 most nearest DAs    


def detect_missing_data(data, variable):
    """
    Detect zones where data are missing on the distribution of HH. These data are coded by StatCan as zeros and no NAs.
    """
    variable_cat = format_variable(variable)
    filter_missing_data = data.loc[:, variable_cat].sum(axis=1) == 0
    return list(data[filter_missing_data].index)


def estimate_number_hh(data, zone_code, pop_col='1', variable=("hh_size", 5)):
    """
    Estimate the number of HH given a total population and a probability distribution of a characteristic of HH, often HH size.
    If X is the number of HH, then the sum of persons in these X HH should equal that of persons given by StatCan (y).
    Put in another form $\sum_{i}^{5}p_i * m_i * X = y$
    Where $p_i$ is the probability of HH size $i$ and $m_i$ is the number of persons per HH. I assume here a limit of 5 persons in HH size 5 (5 persons and plus).
    """
    probability = compute_average_probability_distribution(data, zone_code, variable)
    return round_to_integer(data.loc[zone_code, pop_col] / (probability * range(1, variable[1] + 1)).sum())


def fill_in_missing_data(data, zone, variable, total_population_col="1", hh_variable=("hh_size", 5), hh=True):
    """
    Fill in missing data using the probability distribution of variable X computed from geographically nearest zones
    """
    variable_cat = format_variable(variable)
    probability = compute_average_probability_distribution(data, zone, variable)
    if hh:
        variable_cat_ref = format_variable(hh_variable)
        estimated_number_hh = data.loc[zone, variable_cat_ref].sum()
        if estimated_number_hh == 0:
            estimated_number_hh = estimate_number_hh(data, zone, total_population_col, hh_variable)
    else:
        estimated_number_hh = data.loc[zone, total_population_col]
    hh_distribution = list(probability * estimated_number_hh)
    result = [round_to_integer (x, seed=0) for x in hh_distribution]
    if sum(result) == 0:
        result[np.argmax(hh_distribution)] += estimated_number_hh
    data.loc[zone, variable_cat] = result


def fill_in_dataframe(data, variable, total_population_col="1", hh_variable=("hh_size", 5), hh=True):
    zones_with_missing_data = detect_missing_data(data, variable)
    [fill_in_missing_data(data, zone, variable, total_population_col, hh_variable, hh) for zone in zones_with_missing_data]


def check_for_data_integrity(data, variable, ref_variable=("hh_size", 5), tolerance=30):
    """
    Check if all HH characteristics produce the same total number of HH
    """
    ref_variable_cat = format_variable(ref_variable)
    variable_cat = format_variable(variable)
    abs_max_difference = abs((data.loc[:, ref_variable_cat].sum(axis=1) - data.loc[:, variable_cat].sum(axis=1))).max()
    return abs_max_difference < tolerance


def construct_list(position, size):
    result = np.zeros(size)
    result[position] = 1
    return result


def find_maximum_column(df, variable):
    """
    Return the position of the maximum of the variable
    """
    variable_cat = format_variable(variable)
    return np.argmax(np.array(df.loc[:, variable_cat]), axis=1)


def mock_probability(li, size=5):
    """
    Process list "li" to produce a dataframe of shape len(li) * size. 
    The dataframe contains zeros except position indicated in li which are filled with ones
    """
    assert max(li) < size
    return pd.DataFrame([construct_list(i, size) for i in li])


def correct_data(data, variable, ref_var=("hh_size", 5), tol=30):
    """
    The total number of HH computed using each HH characteristics should be equal. This function assures that this is
    true for each Dissemination area (DA)
    This function assumes that one characteristic of HH is a reference variable that all other variables should clone
    """
    data = data.copy()
    ref_variable_cat = format_variable(ref_var)
    variable_cat = format_variable(variable)
    if not check_for_data_integrity(data, variable, ref_var, tol):
        difference = data.loc[:, ref_variable_cat].sum(axis=1) - data.loc[:, variable_cat].sum(axis=1)
        data.loc[:, variable_cat] += compute_probability_distribution(data, variable).mul(difference, axis=0).applymap(lambda x: round_to_integer(x, seed=0))
        difference = data.loc[:, ref_variable_cat].sum(axis=1) - data.loc[:, variable_cat].sum(axis=1)
        new_probability = mock_probability(find_maximum_column(data, variable), variable[1])
        new_probability.index = data.index
        new_probability.columns = data.loc[:, variable_cat].columns
        data.loc[:, variable_cat] += new_probability.mul(difference, axis=0)
        data[data <  0] = 0
    assert (data.loc[:, variable_cat] >= 0).all().all()
    return data