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
    
    totals = [0 for r in x_date]
    bars = []
    for ver in versions:
        row_data = installs_per_version[ver]
        
        # bar chart for version
        bars.append(
            ax.bar(
                x_date,
                row_data,
                bottom=totals,
                label=ver
            )
        )

        # sum values for totals of next bar
        totals = [previous_total + current_version for previous_total, current_version in zip(totals, row_data)]
        
    # total installation cound inside last bar
    ax.bar_label(bars[-1], labels=totals, label_type='edge', padding=-20,
        # https://matplotlib.org/stable/api/text_api.html#matplotlib.text.Text
        rotation=90, color='white')

    # % on current version in the middle of the top version bar
    current_percents = [
        "{:.1%}".format(latest_version * 1.0 / total,)
        for total, latest_version in zip(totals, installs_per_version[versions[-1]])]
    ax.bar_label(bars[-1], labels=current_percents, label_type='center', padding=3,
        # https://matplotlib.org/stable/api/text_api.html#matplotlib.text.Text
        rotation=90, color='white')

    # inverse legend, so that newest version is on top:
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1], loc='upper left')

    # texts and formatting
    ax.set_ylabel('Installations')
    # titles
    plt.text(x=.5, y=.94, s='Govee integration: installations per version', fontsize=18, ha="center", transform=fig.transFigure)
    subtitle_text = "{0} total installations, {1} on latest version".format(totals[-1], current_percents[-1])
    plt.text(x=.5, y=.88, s=subtitle_text, fontsize=12, ha="center", transform=fig.transFigure)
    plt.subplots_adjust(top=0.85, wspace=0.1)
    # source info
    plt.text(x=.04, y=.045, s='data source: https://analytics.home-assistant.io/custom_integrations.json', fontsize=8, ha="left", transform=fig.transFigure)
    plt.text(x=.04, y=.02, s='history & plot: https://github.com/LaggAt/actions', fontsize=8, ha="left", transform=fig.transFigure)
    # autoformat date on x
    fig.autofmt_xdate()
    
    # write picture:
    plt.savefig(png_filename, facecolor=fig.get_facecolor(), edgecolor='none')


if __name__ == "__main__":
    graph()
    #plt.show()
    
