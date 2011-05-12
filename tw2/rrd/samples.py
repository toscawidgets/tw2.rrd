import tw2.rrd

data_directory = '/'.join(__file__.split('/')[:-1]) + '/data'

class DemoRRDFlotWidget(tw2.rrd.RRDFlotWidget):
    rrd_filenames = [
        data_directory + '/cpu_user.rrd',
        data_directory + '/cpu_system.rrd',
        data_directory + '/cpu_wio.rrd',
    ]

class DemoRRDStreamGraph(tw2.rrd.RRDStreamGraph):
    steps = 10
    logarithmic = True
    rrd_filenames = [
        data_directory + '/cpu_user.rrd',
        data_directory + '/cpu_system.rrd',
        data_directory + '/cpu_wio.rrd',
    ]
