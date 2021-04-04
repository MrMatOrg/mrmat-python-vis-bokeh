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

import sys
import os
import argparse
import time
import json
from datetime import datetime, timedelta
from threading import Thread, Lock

import psutil
from flask import Flask
from bokeh.themes import CALIBER
from bokeh.embed import file_html
from bokeh.models import ColumnDataSource, Range1d,  HoverTool
from bokeh.resources import CDN
from bokeh.plotting import figure

from mrmat_python_vis_bokeh import __version__

app = Flask(__name__)
ds = ColumnDataSource(data={
    'ts': [],
    'memory_free': [],
    'memory_used': []})
ds_weekly = ColumnDataSource(data={
    'ts': [],
    'memory_free': [],
    'memory_used': []
})
lock = Lock()
datafile = None


@app.route('/healthz')
def healthz():
    """
    Check application health
    :return: 'OK' and a 200 upon success, a descriptive message and non-200 status code otherwise
    """
    return 'OK', 200


@app.route('/', methods=['GET'])
def index():
    p = figure(title='Memory Usage (Last 24 hours)',
               x_axis_type='datetime',
               plot_width=800,
               plot_height=300,
               toolbar_location='above',
               output_backend='webgl')
    p.xaxis.axis_label = 'Time'
    p.x_range = Range1d(datetime.now() - timedelta(days=1), datetime.now())
    p.yaxis.axis_label = 'Bytes'
    p.toolbar.autohide = True

    p.add_tools(HoverTool(
        tooltips=[
            ('Time', '@ts{%H:%M}'),
            ('Memory Free', '@memory_free'),
            ('Memory Used', '@memory_used')
        ],
        formatters={
            '@ts': 'datetime'
        },
        mode='vline'
    ))

    p.circle(source=ds, x='ts', y='memory_free', fill_color='#882334')
    p.line(source=ds, x='ts', y='memory_free', line_color='#882334', legend_label='Memory Free')
    p.circle(source=ds, x='ts', y='memory_used', fill_color='#a7bb99')
    p.line(source=ds, x='ts', y='memory_used', line_color='#a7bb99', legend_label='Memory Used')

    p.legend.location = 'center_right'
    p.legend.border_line_width = 1
    p.legend.border_line_color = '#696969'
    p.legend.background_fill_color = '#333333'

    return file_html(models=p, resources=CDN, title='MrMat :: Python :: Vis :: Bokeh', theme=CALIBER)


def dataworker():
    while True:
        with lock:
            ts = datetime.now()
            svmem = psutil.virtual_memory()
            ds.stream(rollover=60, new_data={
                'ts': [ts],
                'memory_free': [svmem.free],
                'memory_used': [svmem.used]
            })
            with open(datafile, 'w') as d:
                json.dump({
                    'ts': [int(t.timestamp()) for t in ds.data['ts']],
                    'memory_free': ds.data['memory_free'],
                    'memory_used': ds.data['memory_used']
                }, d)
            print(f'{ts}: {svmem.free} - {svmem.used} - {datafile}')
        time.sleep(60)


def main() -> int:
    """
    Main entry point for the CLI

    :return: Exit code
    """
    parser = argparse.ArgumentParser(description=f'mrmat-python-vis-bokeh - {__version__}')
    parser.add_argument('-d', '--debug', action='store_true', dest='debug', help='Debug')
    parser.add_argument('--host',
                        dest='host',
                        required=False,
                        default='localhost',
                        help='Host interface to bind to')
    parser.add_argument('--port',
                        dest='port',
                        required=False,
                        default=8080,
                        help='Port to bind to')
    parser.add_argument('--data',
                        dest='data',
                        required=True,
                        help='Datafile to persist data in')

    args = parser.parse_args()

    #
    # Seed previously collected data

    global datafile
    datafile = args.data
    if os.path.exists(args.data):
        with open(args.data, 'r') as d:
            j = json.load(d)
            ds.data = {
                'ts': [datetime.utcfromtimestamp(t) for t in j['ts']],
                'memory_free': j['memory_free'],
                'memory_used': j['memory_used']
            }

    #
    # Start a data collection thread

    collector_thread = Thread(target=dataworker, daemon=True)
    collector_thread.start()

    #
    # Start the app

    app.run(host=args.host, port=args.port, debug=args.debug)

    return 0


if __name__ == '__main__':
    sys.exit(main())
