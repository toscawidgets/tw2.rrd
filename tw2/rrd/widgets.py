import tw2.core as twc
import tw2.core.util as util

import tw2.jit
import tw2.jqplugins.flot
import tw2.protovis.custom
import tw2.protovis.conventional

import pyrrd.rrd

import datetime
import time
import math
import os

class RRDMixin(twc.Widget):
    rrd_filenames = twc.Param(
        """ A collection of rrd_filesnames.

        This can be of the following forms::

            - A list of .rrd filenames.
            - A list of (label, filename) tuples.

        If no labels are specified, tw2.core.util.name2label is used.
        """)

    start = twc.Param("Start as a python datetime")
    end = twc.Param("End as a python datetime")
    timedelta = twc.Param(
        "Overridden if `start` and `end` are specified.",
        default=datetime.timedelta(days=365)
    )
    steps = twc.Param("Number of datapoints to gather.", default=100)

    @classmethod
    def file2name(cls, fname):
        """ Convert a filename to an `attribute` name """
        return fname.split('/')[-1].split('.')[0]

    @classmethod
    def fetch(cls, cf='AVERAGE'):
        if not hasattr(cls, 'end'):
            cls.end = datetime.datetime.now()

        if not hasattr(cls, 'start'):
            cls.start = cls.end - cls.timedelta

        if cls.end <= cls.start:
            raise ValueError, "end <= start"

        if type(cls.rrd_filenames) != list:
            raise ValueError, "rrd_filenames must be a list"

        if not cls.rrd_filenames:
            raise ValueError, "rrd_filenames is empty"

        types = [type(item) for item in cls.rrd_filenames]
        if len(list(set(types))) != 1:
            raise ValueError, "rrd_filenames must be of homogeneous form"

        _type = types[0]
        if _type not in [str, tuple]:
            raise ValueError, "rrd_filenames items must be 'str' or 'tuple'"

        rrd_filenames = cls.rrd_filenames
        if _type == str:
            rrd_filenames = [
                (util.name2label(cls.file2name(f)), f) for f in rrd_filenames
            ]

        lens = [len(item) for item in rrd_filenames]
        if len(list(set(lens))) != 1:
            raise ValueError, "rrd_filenames items must be of the same length"

        _len = lens[0]
        if _len != 2:
            raise ValueError, "rrd_filenames items must be of length 2"

        for item in rrd_filenames:
            if not os.path.exists(item[1]):
                raise ValueError, "rrd_filename %s does not exist." % item[1]
            if not os.path.isfile(item[1]):
                raise ValueError, "rrd_filename %s is not a file." % item[1]

        ###################################
        # Done error checking.
        # Now we can actually get the data.
        ###################################

        # Convert to seconds since the epoch
        end_s = int(time.mktime(cls.end.timetuple()))
        start_s = int(time.mktime(cls.start.timetuple()))

        # Convert `steps` to `resolution` (seconds per step)
        resolution = (end_s - start_s)/cls.steps

        # According to the rrdfetch manpage, the start and end times must be
        # multiples of the resolution.  See *RESOLUTION INTERVAL*.
        start_s = start_s / resolution * resolution
        end_s = end_s / resolution * resolution

        labels = [item[0] for item in rrd_filenames]
        rrds = [pyrrd.rrd.RRD(item[1]) for item in rrd_filenames]

        # Query the round robin database
        # TODO -- are there other things to return other than 'sum'?
        data = [d.fetch(cf=cf, resolution=resolution,
                        start=start_s, end=end_s)['sum'] for d in rrds]

        # Convert from 'nan' to 0.
        for i in range(len(data)):
            for j in range(len(data[i])):
                if math.isnan(data[i][j][1]):
                    data[i][j] = (data[i][j][0], 0)

        # Coerce from seconds to milliseconds  Unix-time is in seconds.
        # *Most* javascript stuff expects milliseconds.
        for i in range(len(data)):
            data[i] = [(t*1000, v) for t, v in data[i]]

        # Wrap up the output into a list of dicts
        return [
            {
                'data' : data[i],
                'label' : labels[i],
            } for i in range(len(data))
        ]

class RRDJitAreaChart(tw2.jit.AreaChart, RRDMixin):
    data = twc.Variable("Internally produced.")
    type = 'stacked'

    def prepare(self):
        self.data = self.fetch()
        labels = [ series['label'] for series in self.data ]

        values = [{ 'label' : datum[0], 'values' : [] }
                  for datum in self.data[0]['data']]

        for i in range(len(self.data)):
            for j in range(len(self.data[0]['data'])):
                values[j]['values'].append(self.data[i]['data'][j][1])

        self.data = { 'label' : labels, 'values' : values }

        super(RRDJitAreaChart, self).prepare()


class RRDFlotWidget(tw2.jqplugins.flot.FlotWidget, RRDMixin):
    data = twc.Variable("Internally produced.")

    options = {
        'xaxis' : {
            'mode' : 'time',
        }
    }

    def prepare(self):
        # TODO -- can this be moved to post_define?
        self.data = self.fetch()
        super(RRDFlotWidget, self).prepare()

class RRDProtoLineChart(tw2.protovis.conventional.LineChart, RRDMixin):
    p_data = twc.Variable("Internally produced")
    p_labels = twc.Variable("Internally produced")

    p_time_series = True
    p_time_series_format = "%b %Y"

    def prepare(self):
        data = self.fetch()
        self.p_labels = [d['label'] for d in data]
        self.p_data = [
            [
                {
                    'x': int(d[0]),
                    'y': d[1],
                } for d in series['data']
            ] for series in data
        ]
        super(RRDProtoLineChart, self).prepare()

class RRDProtoBarChart(tw2.protovis.conventional.BarChart, RRDMixin):
    p_data = twc.Variable("Internally produced")
    p_labels = twc.Variable("Internally produced")
    method = twc.Param(
        "Method for consolidating values.  Either 'sum' or 'average'",
        default='average')

    def prepare(self):
        data = self.fetch()
        self.p_labels = [series['label'] for series in data]
        if not self.method in ['sum', 'average']:
            raise ValueError, "Illegal value '%s' for method" % self.method
        if self.method == 'sum':
            self.p_data = [
                sum([d[1] for d in series['data']])
                for series in data
            ]
        elif self.method == 'average':
            self.p_data = [
                sum([d[1] for d in series['data']])/len(series['data'])
                for series in data
            ]
        super(RRDProtoBarChart, self).prepare()

class RRDProtoBubbleChart(tw2.protovis.custom.BubbleChart, RRDMixin):
    p_data = twc.Variable("Internally produced")
    method = twc.Param(
        "Method for consolidating values.  Either 'sum' or 'average'",
        default='average')

    def prepare(self):
        data = self.fetch()
        if not self.method in ['sum', 'average']:
            raise ValueError, "Illegal value '%s' for method" % self.method
        if self.method == 'sum':
            self.p_data = [
                {
                    'name' : series['label'],
                    'text' : series['label'],
                    'group' : series['label'],
                    'value' : sum([
                        d[1] for d in series['data']
                    ])/len(series['data'])
                } for series in data
            ]
        elif self.method == 'average':
            self.p_data = [
                {
                    'name' : series['label'],
                    'text' : series['label'],
                    'group' : series['label'],
                    'value' : sum([
                        d[1] for d in series['data']
                    ])/len(series['data'])
                } for series in data
            ]
        super(RRDProtoBubbleChart, self).prepare()

class RRDProtoStackedAreaChart(tw2.protovis.conventional.StackedAreaChart, RRDMixin):
    p_data = twc.Variable("Internally produced")
    p_labels = twc.Variable("Internally produced")

    p_time_series = True
    p_time_series_format = "%b %Y"

    def prepare(self):
        data = self.fetch()
        self.p_labels = [d['label'] for d in data]
        self.p_data = [
            [
                {
                    'x': int(d[0]),
                    'y': d[1],
                } for d in series['data']
            ] for series in data
        ]
        super(RRDProtoStackedAreaChart, self).prepare()

class RRDStreamGraph(tw2.protovis.custom.StreamGraph, RRDMixin):
    """ TODO -- this guy needs a lot of work until he looks cool. """

    p_data = twc.Variable("Internally produced")
    logarithmic = twc.Param("Logscale?  Boolean!", default=False)

    def prepare(self):
        data = self.fetch()
        self.p_data = [[item[1] for item in series['data']] for series in data]
        if self.logarithmic:
            self.p_data = [
                [
                    math.log(value+1) for value in series
                ] for series in self.p_data
            ]
        super(RRDStreamGraph, self).prepare()
