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
