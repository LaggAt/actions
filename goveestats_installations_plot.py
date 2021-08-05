# Copyright (c) 2021 Florian Lagg
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import datetime
from jsonl import load_jsonl
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

def parseDate(s: str) -> datetime:
    return datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S').date()


def graph():
    jsonl_filename = 'output/goveestats_installations.jsonl'
    png_filename = 'output/goveestats_installations.png'
    raw_data = load_jsonl(jsonl_filename)

    # remember versions available
    versions = []
    # only first data row per day
    data = []
    last_date = datetime.date.min
    for row in raw_data:
        d = parseDate(row['timestamp'])
        if d > last_date:
            last_date = d
            data.append(row)
            # what versions do we have?
            row_versions = [ k for k in data[0]['installations']['versions'] ]
            for rv in row_versions:
                if rv not in versions:
                    versions.append(rv)

    # sort versions
    versions.sort(key=lambda s: [int(u) for u in s.split('.')])

    x_date = []
    installs_per_version = {}
    for ver in versions:
        installs_per_version[ver] = []
    for row in data:
        x_date.append(parseDate(row['timestamp']))
        for ver in versions:
            cnt = 0
            if ver in row['installations']['versions']:
                cnt = row['installations']['versions'][ver]
            installs_per_version[ver].append(cnt)

    # plot
    fig, ax = plt.subplots()
    
    bottom = [0 for r in x_date]
    for ver in versions:
        row_data = installs_per_version[ver]
        ax.bar(
            x_date,
            row_data,
            bottom=bottom,
            label=ver
        )
        bottom = [x + y for x, y in zip(bottom, row_data)]


    # inverse legend, so that newest version is on top:
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1], loc='upper left')

    # texts and formatting
    ax.set_ylabel('Installations')
    ax.set_title('Govee integration: installations per version')
    fig.autofmt_xdate()
    
    # write picture:
    plt.savefig(png_filename, facecolor=fig.get_facecolor(), edgecolor='none')


if __name__ == "__main__":
    graph()
    #plt.show()
    