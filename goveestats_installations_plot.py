# Copyright (c) 2021 Florian Lagg
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from jsonl import load_jsonl
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib as mpl

VIEW_DAYS_DETAIL = 14

def parseDate(s: str) -> datetime:
    return datetime.strptime(s, '%Y-%m-%d %H:%M:%S').date()


def graph():
    start_detail_date = (datetime.today() - relativedelta(days=VIEW_DAYS_DETAIL)).date()
    jsonl_filename = 'output/goveestats_installations.jsonl'
    png_filename = 'output/goveestats_installations.png'
    raw_data = load_jsonl(jsonl_filename)

    # remember versions available
    versions = []
    # only first data row per day
    data = []
    # start reading stats from 1 year back, on the 1st:
    next_plot_date = date.today().replace(day=1) - relativedelta(years=1)
    for row in raw_data:
        d = parseDate(row['timestamp'])
        # do we plot this line?
        if d >= next_plot_date:
            # append row to plot
            row['is_detail'] = d >= start_detail_date
            data.append(row)
            # what versions do we have?
            row_versions = [ k for k in row['installations']['versions'] ]
            for rv in row_versions:
                if rv not in versions:
                    versions.append(rv)
            # next date we want to plot
            next_rough_date = d.replace(day=1) + relativedelta(months=1)
            next_detail_date = date(d.year, d.month, d.day) + relativedelta(days=1)
            if next_detail_date >= start_detail_date:
                next_plot_date = next_detail_date
            elif next_rough_date >= start_detail_date:
                next_plot_date = start_detail_date
            else:
                next_plot_date = next_rough_date
        
    # sort versions
    versions.sort(key=lambda s: [int(u) for u in s.split('.')])

    x_dates = []
    installs_per_version = {}
    for ver in versions:
        installs_per_version[ver] = []
    for row in data:
        dt = parseDate(row['timestamp'])
        x_dt = dt.strftime("%b %Y")
        if dt >= start_detail_date:
            x_dt = dt.strftime("%d.%b")
        x_dates.append(x_dt)
        for ver in versions:
            cnt = 0
            if ver in row['installations']['versions']:
                cnt = row['installations']['versions'][ver]
            installs_per_version[ver].append(cnt)

    # plot
    fig, ax = plt.subplots()
    
    totals = [0 for r in x_dates]
    bars = []
    for ver in versions:
        row_data = installs_per_version[ver]
        
        # bar chart for version
        bars.append(
            ax.bar(
                x_dates,
                row_data,
                bottom=totals,
                label=ver
            )
        )

        # sum values for totals of next bar
        totals = [previous_total + current_version for previous_total, current_version in zip(totals, row_data)]
        
    # total installation cound inside last bar
    ax.bar_label(bars[-1], labels=totals, label_type='edge', padding=-25,
        # https://matplotlib.org/stable/api/text_api.html#matplotlib.text.Text
        rotation=90, color='white'
    )

    # % on current version in the middle of the top version bar
    current_percents = [
        "{:.1%}".format(latest_version * 1.0 / total,)
        for total, latest_version in zip(totals, installs_per_version[versions[-1]])]
    # removed for visibility / positioning was wrong too.
    # ax.bar_label(bars[-1], labels=current_percents, label_type='center', padding=3,
    #     # https://matplotlib.org/stable/api/text_api.html#matplotlib.text.Text
    #     rotation=90, color='white')

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
    # x ticks formatting + spacing
    plt.xticks(fontsize=10, rotation=50)
    plt.subplots_adjust(bottom=0.22)
    
    
    # write picture:
    plt.savefig(png_filename, facecolor=fig.get_facecolor(), edgecolor='none')


if __name__ == "__main__":
    graph()
    #plt.show()
    
