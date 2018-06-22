import os
from datetime import date

import pandas as pd

import optopsy as op

pd.options.display.width = None

spx_struct = (
    ('quote_date', 0),
    ('close', 1)
)


def run_analysis():
    # fetch the stock quotes from our data source
    d = op.get(os.path.join(os.path.dirname(__file__), 'test_data', 'stocks', 'spx.csv'),
               start=date(2016, 1, 1),
               end=date(2016, 12, 31),
               struct=spx_struct,
               prompt=True
               )


if __name__ == '__main__':
    run_analysis()
