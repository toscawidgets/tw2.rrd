import tw2.core as twc
import tw2.rrd

import datetime

data_directory = '/'.join(__file__.split('/')[:-1]) + '/data'

class DemoRRDJitAreaChart(tw2.rrd.RRDJitAreaChart):
    rrd_filenames = [
        data_directory + '/cpu_user.rrd',
        data_directory + '/cpu_wio.rrd',
        data_directory + '/cpu_system.rrd',
    ]
    steps = 25
    timedelta = datetime.timedelta(days=90)
    width="400px"
    height="250px"
    offset = 0

    showAggregates = False
    showLabels = False
    Label = {
        'size': 15,
        'family': 'Arial',
        'color': 'white'
    }
    Tips = {
        'enable': True,
        'onShow' : twc.JSSymbol(src="""
        (function(tip, elem) {
            tip.innerHTML = "<b>" + elem.name + "</b>: " + elem.value + " % cpu usage across 8 cores.";
        })""")
    }


class DemoRRDFlotWidget(tw2.rrd.RRDFlotWidget):
    rrd_filenames = [
        data_directory + '/cpu_user.rrd',
        data_directory + '/cpu_system.rrd',
        data_directory + '/cpu_wio.rrd',
    ]

class DemoRRDProtoBarChart(tw2.rrd.RRDProtoBarChart):
    rrd_filenames = [
        data_directory + '/cpu_user.rrd',
        data_directory + '/cpu_system.rrd',
        data_directory + '/cpu_wio.rrd',
    ]

    def series_sorter(self, x, y):
        """ Sort by total value """
        return -1 * cmp(
            sum([d[1] for d in x['data']]),
            sum([d[1] for d in y['data']])
        )


class DemoRRDProtoBubbleChart(tw2.rrd.RRDProtoBubbleChart):
    rrd_filenames = [
        data_directory + '/cpu_user.rrd',
        data_directory + '/cpu_system.rrd',
        data_directory + '/cpu_wio.rrd',
    ]

    # Sort alphabetically
    series_sorter = lambda self, x, y : cmp(x['label'], y['label'])

class DemoRRDProtoLineChart(tw2.rrd.RRDProtoLineChart):
    rrd_filenames = [
        data_directory + '/cpu_user.rrd',
        data_directory + '/cpu_system.rrd',
        data_directory + '/cpu_wio.rrd',
    ]

class DemoRRDProtoStackedAreaChart(tw2.rrd.RRDProtoStackedAreaChart):
    rrd_filenames = [
        data_directory + '/cpu_user.rrd',
        data_directory + '/cpu_system.rrd',
        data_directory + '/cpu_wio.rrd',
    ]

class DemoRRDStreamGraph(tw2.rrd.RRDStreamGraph):
    logarithmic = True
    rrd_filenames = [
        data_directory + '/cpu_user.rrd',
        data_directory + '/cpu_system.rrd',
        data_directory + '/cpu_wio.rrd',
    ]
