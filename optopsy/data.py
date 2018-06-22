import glob
import os
import sys
from distutils.util import strtobool

import pandas as pd

from .helpers import generate_symbol

# All data feeds should have certain fields present, as defined by
# the second item of each tuple in the fields list, True means this field is required
fields = (
    ('symbol', True),
    ('option_symbol', False),
    ('quote_date', True),
    ('root', False),
    ('style', False),
    ('expiration', True),
    ('strike', True),
    ('option_type', True),
    ('volume', False),
    ('bid', True),
    ('ask', True),
    ('underlying_price', False),
    ('oi', False),
    ('iv', False),
    ('delta', False),
    ('gamma', False),
    ('theta', False),
    ('vega', False),
    ('rho', False),
    ('open', False),
    ('high', False),
    ('low', False),
    ('close', False)
)

stk_fields = (
    ('quote_date', True),
    ('open', False),
    ('high', False),
    ('low', False),
    ('close', True)
)


def _import(path, start, end, struct, skiprows, prompt, bulk=False, mode='option'):
    """
    This method will read in the data file using pandas and assign the
    normalized dataframe to the class's data variable.

    Normalization means to map columns from data source to a standard
    column name that will be used in this program.

    :file_path: the path of the file relative to the current file
    :start: date object representing the start date to include in the backtest
    :end: date object representing the end date to include in the backtest
    :struct: a list of dictionaries to describe the column index to read in the option chain data
    """

    if not bulk and os.path.isdir(path):
        raise ValueError("Invalid path, please provide a valid path to a file")
    elif bulk and not os.path.isdir(path):
        raise ValueError("Invalid path, please provide a valid directory path")
    else:
        cols = _check_structs(struct, start, end)

        if bulk:
            # for each file in path
            all_files = glob.glob(os.path.join(path, "*.csv"))
            all_files.sort()
            df = pd.concat(
                pd.read_csv(f, parse_dates=True, names=cols[0], usecols=cols[1], skiprows=skiprows)
                for f in all_files)
        else:
            df = pd.read_csv(path, parse_dates=True, names=cols[0], usecols=cols[1],
                             skiprows=skiprows)

        # TODO: We need to ensure that only one symbol of the underlying asset is returned

        if prompt:
            print(df.head())
            if user_prompt("Does this look correct?"):
                return _format(df, start, end, mode)
        elif not prompt:
            return _format(df, start, end, mode)
        else:
            sys.exit()


def get_stk(file_path, start, end, struct, skiprows=1, prompt=True):
    return _import(file_path, start, end, struct, skiprows, prompt, mode='stock')


def get(file_path, start, end, struct, skiprows=1, prompt=True):
    return _import(file_path, start, end, struct, skiprows, prompt)


def gets(dir_path, start, end, struct, skiprows=1, prompt=True):
    return _import(dir_path, start, end, struct, skiprows, prompt)


def _format(df, start, end, mode):
    """
    Format the data frame to a standard format
    :param df: dataframe to format
    :return: formatted dataframe
    """
    df['expiration'] = pd.to_datetime(df['expiration'], infer_datetime_format=True,
                                      format='%Y-%m-%d')
    df['quote_date'] = pd.to_datetime(df['quote_date'], infer_datetime_format=True,
                                      format='%Y-%m-%d')

    # convert option types to standard format 'c' or 'p'
    df['option_type'] = df['option_type'].str.lower().str[:1]

    # use quote date as index
    df.set_index('quote_date', inplace=True, drop=False)

    # rounds numbers to two decimals
    df = df.round(2)

    # if the data source did not include a option_symbol field, we will generate it
    if 'option_symbol' in df.columns:
        df = df.drop('symbol', axis=1)
        df = df.rename(columns={'option_symbol': 'symbol'})
        df['symbol'] = '.' + df['symbol']
    else:
        df['symbol'] = '.' + df.apply(
            lambda r: generate_symbol(r['symbol'], r['expiration'], r['strike'], r['option_type']),
            axis=1
        )

    return df.loc[start:end]


def _check_structs(struct, start, end):
    """
    This method will check the provided struct for this data set and make sure the
    provided fields and indices are valid
    :param start: the start date to import data
    :param end: the end date of all imported data
    :param struct: a list containing tuples that contain the column name and the index referring to
    the column number to import from
    :return:True or False
    """

    std_fields = list(zip(*fields))[0]
    req_fields = [x[0] for x in fields if x[1] is True]

    # First we check if the provided struct uses our standard list of defined column names
    for f in struct:
        if f[0] not in std_fields or f[1] < 0 or start > end:
            raise ValueError("Field names or field indices not valid!")

    cols = list(zip(*struct))

    # check if we have any duplicate indices, which would be invalid
    if len(list(set(cols[1]))) != len(cols[1]):
        raise ValueError("Duplicate indices found!")

    # Check if the struct provided contains all the required fields
    if not all(f in cols[0] for f in req_fields):
        raise ValueError("Required field names not defined!")

    return cols


def user_prompt(question):
    """
    Prompts a Yes/No questions.
    :param question: The question to ask the user
    """
    while True:
        sys.stdout.write(question + " [y/n]: ")
        user_input = input().lower()
        try:
            result = strtobool(user_input)
            return result
        except ValueError:
            sys.stdout.write("Please use y/n or yes/no.\n")
