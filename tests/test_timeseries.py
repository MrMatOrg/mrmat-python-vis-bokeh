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

import numpy as np
import pandas as pd

from mrmat_python_vis_bokeh.model import Timeseries


def test_init_empty(tmp_path):
    datafile = tmp_path / 'test.json'
    assert not os.path.exists(datafile)
    t = Timeseries(datafile=datafile)
    assert t.datafile == datafile
    assert t.df is not None


def test_init_data(tmp_path):
    datafile = tmp_path / 'test.json'
    t1 = Timeseries(datafile=datafile)
    t1.update(data={'foo': [1], 'bar': [2]})
    t1.save()
    t2 = Timeseries(datafile=datafile)
    assert t2.equals(t1)


def test_update(tmp_path):
    datafile = tmp_path / 'test.json'
    assert not os.path.exists(datafile)
    t = Timeseries(datafile=datafile)
    t.update(data={'foo': [1]})
    t.save()
    assert os.path.exists(datafile)
    df = pd.read_json(datafile)
    assert df.equals(t.df)


def test_save(tmp_path):
    datafile = tmp_path / 'test.json'
    assert not os.path.exists(datafile)
    t = Timeseries(datafile=str(datafile))
    t.save()
    assert os.path.exists(datafile)


def test_load(tmp_path):
    datafile = tmp_path / 'test.json'
    assert not os.path.exists(datafile)
    t1 = Timeseries(datafile=str(datafile))
    t1.save()
    assert os.path.exists(datafile)
    t1.load()


def test_dayly(tmp_path):
    datafile = tmp_path / 'test.json'
    t1 = Timeseries(datafile=str(datafile))
    for t in range(0, 4 * 24 * 30):
        t1.update(ts=datetime.utcnow() - timedelta(minutes=15 * t), data={
            'foo': [np.random.randint(10)],
            'bar': [np.random.randint(10)],
            'baz': [np.random.randint(10)]
        })
    assert len(t1.df) == 2880
    assert len(t1.daily()) == 96


def test_weekly(tmp_path):
    datafile = tmp_path / 'test.json'
    t1 = Timeseries(datafile=str(datafile))
    for t in range(0, 4 * 24 * 30):
        t1.update(ts=datetime.utcnow() - timedelta(minutes=15 * t), data={
            'foo': [np.random.randint(10)],
            'bar': [np.random.randint(10)],
            'baz': [np.random.randint(10)]
        })
    assert len(t1.df) == 2880
    assert len(t1.weekly()) == 169


def test_monthly(tmp_path):
    datafile = tmp_path / 'test.json'
    t1 = Timeseries(datafile=str(datafile))
    for t in range(0, 4 * 24 * 30):
        t1.update(ts=datetime.utcnow() - timedelta(minutes=15 * t), data={
            'foo': [np.random.randint(10)],
            'bar': [np.random.randint(10)],
            'baz': [np.random.randint(10)]
        })
    assert len(t1.df) == 2880
    assert len(t1.monthly()) == 225


def test_truncation(tmp_path):
    datafile = tmp_path / 'test.json'
    t1 = Timeseries(datafile=str(datafile))
    for t in range(0, 4 * 24 * 30):
        t1.update(ts=datetime.utcnow() - timedelta(minutes=15 * t), data={
            'foo': [np.random.randint(10)],
            'bar': [np.random.randint(10)],
            'baz': [np.random.randint(10)]})
    assert len(t1.df) == 2880
    current_head = t1.df.head()
    current_tail = t1.df.tail()

    t1.update(ts=datetime.utcnow() + timedelta(days=2), data={
        'foo': [np.random.randint(10)],
        'bar': [np.random.randint(10)],
        'baz': [np.random.randint(10)]})
    assert len(t1.df) == 2881
    t1.truncate()
    assert len(t1.df) == 2688

    assert t1.df.head().equals(current_head)
    assert not t1.df.tail().equals(current_tail)
