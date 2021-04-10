#  MIT License
#
#  Copyright (c) 2021 MrMatOrg
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

import os
from datetime import datetime, timedelta
from typing import Optional, Union, Dict

import pandas as pd


class Timeseries:
    _datafile: str
    _df: pd.DataFrame = pd.DataFrame(data=[], index=pd.DatetimeIndex(name='ts', data=[]))

    def __init__(self, datafile: Optional[str] = None):
        self._datafile = datafile
        if os.path.exists(datafile):
            self._df = pd.read_json(datafile)

    @property
    def datafile(self) -> str:
        return self._datafile

    @property
    def df(self) -> pd.DataFrame:
        return self._df

    def update(self, ts: Union[datetime, pd.Timestamp] = None, data=Dict) -> None:
        if ts is None:
            ts = pd.Timestamp(datetime.utcnow(), unit='s')
        elif type(ts) == datetime:
            ts = pd.Timestamp(ts, unit='s')
        upd = pd.DataFrame(data=data, index=pd.DatetimeIndex(name='ts', data=[ts]))
        self._df = self._df.append(upd)
        self._df = self.df.sort_index(ascending=False)

    def truncate(self):
        now = datetime.utcnow()
        self._df = self._df[now:now - timedelta(weeks=4)]

    def daily(self):
        now = datetime.utcnow()
        return self._df[now:now - timedelta(days=1)]

    def weekly(self):
        now = datetime.utcnow()
        return self._df[now:now - timedelta(weeks=1)].resample('1H').mean()

    def monthly(self):
        now = datetime.utcnow()
        return self._df[now:now - timedelta(weeks=4)].resample('3H').mean()

    def load(self, datafile: Optional[str] = None) -> None:
        self._df = pd.read_json(self._datafile if datafile is None else datafile)

    def save(self, datafile: Optional[str] = None) -> None:
        self._df.to_json(self._datafile if datafile is None else datafile,
                         date_format='epoch',
                         date_unit='ns',
                         index=True)

    def equals(self, t):
        return self._df.equals(t.df)
