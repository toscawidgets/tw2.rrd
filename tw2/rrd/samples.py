import tw2.rrd

data_directory = '/'.join(__file__.split('/')[:-1]) + '/data'

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
