# Copyright (c) 2021 Florian Lagg
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from datetime import datetime, timedelta
from jsonl import load_jsonl
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

VIEW_ERROR_DAYS = 7

def parseDate(s: str) -> datetime:
    return datetime.strptime(s, '%Y-%m-%d %H:%M:%S')

def combine_ping_success(get_block):
    return get_block['ping'] * (1 if get_block['success'] else -1)

def get_error(get_block):
    if get_block['success']:
        return ', OK'
    return ', failing: {0}'.format(get_block['error'])

def graph():
    jsonl_filename = 'output/govee-api-up.jsonl'
    png_filename = 'output/govee-api-up.png'
    raw_data = load_jsonl(jsonl_filename)

    data = {
        'timestamp': [parseDate(row['timestamp']) for row in raw_data],

        'get_devices_success': [row['get_devices']['success'] for row in raw_data],
        'get_devices_ping': [row['get_devices']['ping'] for row in raw_data],
        'get_devices_error': [row['get_devices']['error'] for row in raw_data],
        
        'get_states_success': [row['get_states']['success'] for row in raw_data],
        'get_states_ping': [row['get_states']['ping'] for row in raw_data],
        'get_states_error': [row['get_states']['error'] for row in raw_data],
    }

    df = pd.DataFrame(data)
    print(df)

    # prepare strings for last error no more than VIEW_ERROR_DAYS days ago
    relevant_errors = df.where(df.get_devices_success == False).where(df.timestamp > datetime.utcnow() - timedelta(days=VIEW_ERROR_DAYS))
    get_devices_last_error_info = 'get_devices(): No recorded error in {0} days.'.format(VIEW_ERROR_DAYS)
    if relevant_errors.last_valid_index():
        err = relevant_errors.iloc[relevant_errors.last_valid_index()]
        get_devices_last_error_info = 'get_devices() last recorded error at {0}: {1}'.format(err.timestamp, err.get_devices_error)

    relevant_errors = df.where(df.get_states_success == False).where(df.timestamp > datetime.utcnow() - timedelta(days=VIEW_ERROR_DAYS))
    get_states_last_error_info = 'get_states(): No recorded error in {0} days.'.format(VIEW_ERROR_DAYS)
    if relevant_errors.last_valid_index():
        err = relevant_errors.iloc[relevant_errors.last_valid_index()]
        get_states_last_error_info = 'get_states() last recorded error at {0}: {1}'.format(err.timestamp, err.get_states_error)

    # plot
    fig, ax = plt.subplots()
    
    ax.step(
        df.timestamp,
        np.where(df.get_devices_success == True, df.get_devices_ping, np.NaN),
        'g+',
        label='get_devices() OK'
    )
    ax.step(
        df.timestamp,
        np.where(df.get_devices_success == False, df.get_devices_ping, np.NaN),
        'go',
        label='get_devices() Error'
    )

    ax.step(
        df.timestamp,
        np.where(df.get_states_success == True, df.get_states_ping, np.NaN),
        'b+',
        label='get_states() OK'
    )
    ax.step(
        df.timestamp,
        np.where(df.get_states_success == False, df.get_states_ping, np.NaN),
        'bo',
        label='get_states() Error'
    )

    # inverse legend, so that newest version is on top:
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels, loc='upper left')

    # texts and formatting
    ax.set_ylabel('Ping (ms)')
    # titles
    plt.text(x=.5, y=.94, s='Govee API: is it working?', fontsize=18, ha="center", transform=fig.transFigure)
    plt.text(x=.04, y=.90, s=get_devices_last_error_info, fontsize=8, ha="left", transform=fig.transFigure)
    plt.text(x=.04, y=.87, s=get_states_last_error_info, fontsize=8, ha="left", transform=fig.transFigure)
    plt.subplots_adjust(top=0.85, wspace=0.1)
    # source info
    plt.text(x=.04, y=.045, s='data source: Measured on Govee API, using https://github.com/LaggAt/python-govee-api', fontsize=8, ha="left", transform=fig.transFigure)
    plt.text(x=.04, y=.02, s='history & plot: https://github.com/LaggAt/actions', fontsize=8, ha="left", transform=fig.transFigure)
    # autoformat date on x
    fig.autofmt_xdate()
    
    # write picture:
    plt.savefig(png_filename, facecolor=fig.get_facecolor(), edgecolor='none')


if __name__ == "__main__":
    graph()
    #plt.show()
    
