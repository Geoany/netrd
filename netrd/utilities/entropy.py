"""
entropy.py
----------

Utility functions computing entropy of variables in time series data inspired
by https://blog.biolab.si/2012/06/15/computing-joint-entropy-in-python/.

author: Chia-Hung Yang
Submitted as part of the 2019 NetSI Collabathon.
"""

import numpy as np
from itertools import product


def entropy(var):
    """
    Return the Shannon entropy of a variable.

    Params
    ------
    var (np.ndarray): 1D array of observations of the variable.

    Notes
    -----
    1. $H(X) = - \sum p(X) log_2(p(X))$
    2. Data of the variable must be categorical.

    """
    return joint_entropy(var[:, np.newaxis])


def joint_entropy(data):
    """
    Return the joint entropy of all variables in the data.

    Params
    ------
    data (np.ndarray): Array of data with variables as columns and observations
                       as rows.

    Returns
    -------
    entrp (float): Joint entrpoy of the variables of interests.

    Notes
    -----
    1. $H(\{X_i\}) = - \sum p(\{X_i\}) log_2(p(\{X_i\}))
    2. The data of variables must be categorical.

    """
    m, _ = data.shape
    data = data.T  # Transpose the data for ease of looping over variables

    # Enumerate all possible joint values of the variables
    entrp = 0
    for values in product(*[set(var) for var in data]):
        # Compute the joint probability that variables have the values
        indc = np.full(m, True)  # Joint indicators
        for var, val in zip(data, values):
            indc = np.logical_and(indc, var == val)
        p = np.mean(indc)
        # Additively update the entropy
        if p > 0:
            entrp += -p * np.log2(p)

    return entrp


def conditional_entropy(data, given):
    """
    Return the conditional entropy of variables in the data conditioned on
    a given set of variables.

    Params
    ------
    data (np.ndarray): Array of data with variables of interests as columns
                       and observations as rows.

    given (np.ndarray): Array of data with the conditioned variables as
                        columns and observations as rows.

    Returns
    -------
    entrp (float): Conditional entrpoy of the variables $\{X_i\} of interests
                   conditioned on variables $\{Y_j\}$.

    Notes
    -----
    1. $H(\{X_i\}|\{Y_j\}) = - \sum p(\{X_i\}\cup\{Y_j\}) log_2(p(\{X_i\}|\{Y_j\}))
    2. The data of vairiables must be categorical.

    """
    joint = np.hstack((data, given))
    entrp = joint_entropy(joint) - joint_entropy(given)

    return entrp


def categorized_data(raw, n_bins):
    """
    Return the categorized data where an entry in the returned array is the
    index of bin of the linearly-binned raw continuous data.

    Params
    ------
    raw (np.ndarray): Array of raw continuous data.

    n_bins (int): A universal number of bins for all the variables.

    Returns
    -------
    data (np.ndarray): Array of bin indices after categorizing the raw data.

    """
    bins = linear_bins(raw, n_bins)
    data = np.ones(raw.shape, dtype=int)

    # Find the index of bins each element in the raw data array belongs to
    for (i, j), val in np.ndenumerate(raw):
        data[i, j] = np.argmax(bins[1:, j] >= val)

    return data


def linear_bins(raw, n_bins):
    """
    Return the separators of linear bins for each variable in the raw data.

    Params
    ------
    raw (np.ndarray): Array of raw continuous data.

    n_bins (int): A universal number of bins for all the variables.

    Returns
    -------
    bins (np.ndarray): Array where a column is the separators of bins for a
                       variable.

    Notes
    -----
    The bins are $B_0 = [b_0, b_1]$, $B_i = (b_i, b_i+1]$, where $b_i$s are the
    separators of bins.

    """
    _min = raw.min(axis=0)
    _max = raw.max(axis=0)
    bins = np.array([np.linspace(start, end, num=n_bins+1)
                     for start, end in zip(_min, _max)])
    bins = bins.T

    return bins
