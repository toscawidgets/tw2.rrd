import tw2.core as twc
import tw2.rrd

import sys
import datetime

arch = ['32', '64'][sys.maxsize > 2**32]
data_directory = '/'.join(__file__.split('/')[:-1] + ['data', arch]) + '/'

class DemoNestedRRDJitTreeMap(tw2.rrd.NestedRRDJitTreeMap):
    start = datetime.datetime.fromtimestamp(1306557540)
    end = datetime.datetime.fromtimestamp(1306558380)

    root_title = "Country versus Filename"

    rrd_directories = [
        data_directory + 'nested/filename/' + country
        for country in [
            'Brazil/',
            'Canada/',
            'China/',
            'France/',
            'Germany/',
            'Greece/',
            'India/',
            'Italy/',
            'Malaysia/',
            'Mexico/',
            'Peru/',
            'Puerto_Rico/',
            'Russian_Federation/',
            'Singapore/',
            'Spain/',
            'Sweden/',
            'Turkey/',
            'Ukraine/',
            'United_Kingdom/',
            'United_States/',
        ]
    ]


    Tips = {
        'enable' : True,
        'offsetX' : 20,
        'offsetY' : 20,
        'onShow' : twc.JSSymbol(src="""
            (function(tip, node, isLeaf, domElement) {
                   var html = '<div class="tip-title">' + node.name
                     + '</div><div class="tip-text">';
                   var data = node.data;
                   if(data['$area']) {
                     html += ' hits per second:  ' + data['$area'].toFixed(2);
                   }
                   tip.innerHTML =  html;
            })
            """)
    }

    onCreateLabel = twc.JSSymbol(src="""
        (function(domElement, node){
           domElement.innerHTML = node.name;
           var style = domElement.style;
           style.display = '';
           style.border = '1px solid transparent';
           style.color = '#000000';
           domElement.onmouseover = function() {
             style.border = '1px solid #9FD4FF';
           };
           domElement.onmouseout = function() {
             style.border = '1px solid transparent';
           };
        } )
        """)



class DemoNestedRRDProtoCirclePackingWidget(
    tw2.rrd.NestedRRDProtoCirclePackingWidget):

    start = datetime.datetime.fromtimestamp(1306557540)
    end = datetime.datetime.fromtimestamp(1306558380)

    root_title = "Country versus Filename"

    rrd_directories = [
        data_directory + 'nested/filename/' + country
        for country in [
            'Brazil/',
            'Canada/',
            'China/',
            'France/',
            'Germany/',
            'Greece/',
            'India/',
            'Italy/',
            'Malaysia/',
            'Mexico/',
            'Peru/',
            'Puerto_Rico/',
            'Russian_Federation/',
            'Singapore/',
            'Spain/',
            'Sweden/',
            'Turkey/',
            'Ukraine/',
            'United_Kingdom/',
            'United_States/',
        ]
    ]

class DemoFlatRRDJitAreaChart(tw2.rrd.FlatRRDJitAreaChart):
    start   = datetime.datetime.fromtimestamp(1280000000)
    end     = datetime.datetime.fromtimestamp(1304000000)
    rrd_filenames = [
        data_directory + '/flat/cpu_user.rrd',
        data_directory + '/flat/cpu_wio.rrd',
        data_directory + '/flat/cpu_system.rrd',
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


class DemoFlatRRDFlotWidget(tw2.rrd.FlatRRDFlotWidget):
    start   = datetime.datetime.fromtimestamp(1280000000)
    end     = datetime.datetime.fromtimestamp(1304000000)
    rrd_filenames = [
        data_directory + '/flat/cpu_user.rrd',
        data_directory + '/flat/cpu_system.rrd',
        data_directory + '/flat/cpu_wio.rrd',
    ]

class DemoFlatRRDProtoBarChart(tw2.rrd.FlatRRDProtoBarChart):
    start   = datetime.datetime.fromtimestamp(1280000000)
    end     = datetime.datetime.fromtimestamp(1304000000)
    rrd_filenames = [
        data_directory + '/flat/cpu_user.rrd',
        data_directory + '/flat/cpu_system.rrd',
        data_directory + '/flat/cpu_wio.rrd',
    ]

    def series_sorter(self, x, y):
        """ Sort by total value """
        return -1 * cmp(
            sum([d[1] for d in x['data']]),
            sum([d[1] for d in y['data']])
        )


class DemoFlatRRDProtoBubbleChart(tw2.rrd.FlatRRDProtoBubbleChart):
    start   = datetime.datetime.fromtimestamp(1280000000)
    end     = datetime.datetime.fromtimestamp(1304000000)
    rrd_filenames = [
        data_directory + '/flat/cpu_user.rrd',
        data_directory + '/flat/cpu_system.rrd',
        data_directory + '/flat/cpu_wio.rrd',
    ]

    # Sort alphabetically
    series_sorter = lambda self, x, y : cmp(x['label'], y['label'])

class DemoFlatRRDProtoLineChart(tw2.rrd.FlatRRDProtoLineChart):
    start   = datetime.datetime.fromtimestamp(1280000000)
    end     = datetime.datetime.fromtimestamp(1304000000)
    rrd_filenames = [
        data_directory + '/flat/cpu_user.rrd',
        data_directory + '/flat/cpu_system.rrd',
        data_directory + '/flat/cpu_wio.rrd',
    ]

class DemoFlatRRDProtoStackedAreaChart(tw2.rrd.FlatRRDProtoStackedAreaChart):
    start   = datetime.datetime.fromtimestamp(1280000000)
    end     = datetime.datetime.fromtimestamp(1304000000)
    rrd_filenames = [
        data_directory + '/flat/cpu_user.rrd',
        data_directory + '/flat/cpu_system.rrd',
        data_directory + '/flat/cpu_wio.rrd',
    ]

class DemoFlatRRDStreamGraph(tw2.rrd.FlatRRDStreamGraph):
    start   = datetime.datetime.fromtimestamp(1280000000)
    end     = datetime.datetime.fromtimestamp(1304000000)
    logarithmic = True
    rrd_filenames = [
        data_directory + '/flat/cpu_user.rrd',
        data_directory + '/flat/cpu_system.rrd',
        data_directory + '/flat/cpu_wio.rrd',
    ]
