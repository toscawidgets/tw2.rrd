import tw2.core as twc
import tw2.core.util as util

import tw2.jit
import tw2.jqplugins.flot
import tw2.protovis.custom
import tw2.protovis.conventional

import math
import os

from tw2.rrd.widgets.core import RRDBaseMixin

class RRDFlatMixin(RRDBaseMixin):
    rrd_filenames = twc.Param(
        """ A collection of rrd_filesnames.

        This can be of the following forms::

            - A list of .rrd filenames.
            - A list of (label, filename) tuples.

        If no labels are specified, tw2.core.util.name2label is used.
        """)

    @classmethod
    def flat_fetch(cls):
        cls.sanity()

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

        return cls._do_flat_fetch(rrd_filenames)


class FlatRRDJitAreaChart(tw2.jit.AreaChart, RRDFlatMixin):
    data = twc.Variable("Internally produced.")
    type = 'stacked'

    def prepare(self):
        self.data = self.flat_fetch()
        labels = [ series['label'] for series in self.data ]

        values = [{ 'label' : datum[0], 'values' : [] }
                  for datum in self.data[0]['data']]

        for i in range(len(self.data)):
            for j in range(len(self.data[0]['data'])):
                values[j]['values'].append(self.data[i]['data'][j][1])

        self.data = { 'label' : labels, 'values' : values }

        super(FlatRRDJitAreaChart, self).prepare()

class FlatRRDFlotWidget(tw2.jqplugins.flot.FlotWidget, RRDFlatMixin):
    data = twc.Variable("Internally produced.")

    options = {
        'xaxis' : {
            'mode' : 'time',
        }
    }

    def prepare(self):
        # TODO -- can this be moved to post_define?
        self.data = self.flat_fetch()
        super(FlatRRDFlotWidget, self).prepare()

class FlatRRDProtoLineChart(tw2.protovis.conventional.LineChart, RRDFlatMixin):
    p_data = twc.Variable("Internally produced")
    p_labels = twc.Variable("Internally produced")

    p_time_series = True
    p_time_series_format = "%b %Y"

    def prepare(self):
        data = self.flat_fetch()
        self.p_labels = [d['label'] for d in data]
        self.p_data = [
            [
                {
                    'x': int(d[0]),
                    'y': d[1],
                } for d in series['data']
            ] for series in data
        ]
        super(FlatRRDProtoLineChart, self).prepare()

class FlatRRDProtoBarChart(tw2.protovis.conventional.BarChart, RRDFlatMixin):
    series_sorter = twc.Param("function to compare to data points for sorting",
                              default=None)
    prune_zeroes = twc.Param("hide zero-valued series?", default=False)
    p_data = twc.Variable("Internally produced")
    p_labels = twc.Variable("Internally produced")
    method = twc.Param(
        "Method for consolidating values.  Either 'sum' or 'average'",
        default='average')

    def prepare(self):
        data = self.flat_fetch()

        if self.series_sorter:
            data.sort(self.series_sorter)

        if not self.method in ['sum', 'average']:
            raise ValueError, "Illegal value '%s' for method" % self.method

        self.p_labels = [series['label'] for series in data]

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

        super(FlatRRDProtoBarChart, self).prepare()

class FlatRRDProtoBubbleChart(tw2.protovis.custom.BubbleChart, RRDFlatMixin):
    series_sorter = twc.Param("function to compare to data points for sorting",
                              default=None)
    p_data = twc.Variable("Internally produced")
    method = twc.Param(
        "Method for consolidating values.  Either 'sum' or 'average'",
        default='average')

    def prepare(self):
        data = self.flat_fetch()

        if self.series_sorter:
            data.sort(self.series_sorter)

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
                    ]),
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
                    ])/len(series['data']),
                } for series in data
            ]

        # Remove all zero-valued bubbles!  (They don't make sense...)
        self.p_data = [d for d in self.p_data if d['value'] != 0]

        super(FlatRRDProtoBubbleChart, self).prepare()

class FlatRRDProtoStackedAreaChart(tw2.protovis.conventional.StackedAreaChart,
                                   RRDFlatMixin):
    p_data = twc.Variable("Internally produced")
    p_labels = twc.Variable("Internally produced")

    p_time_series = True
    p_time_series_format = "%b %Y"

    def prepare(self):
        data = self.flat_fetch()
        self.p_labels = [d['label'] for d in data]
        self.p_data = [
            [
                {
                    'x': int(d[0]),
                    'y': d[1],
                } for d in series['data']
            ] for series in data
        ]

        super(FlatRRDProtoStackedAreaChart, self).prepare()

class FlatRRDStreamGraph(tw2.protovis.custom.StreamGraph, RRDFlatMixin):
    """ TODO -- this guy needs a lot of work until he looks cool. """

    p_data = twc.Variable("Internally produced")
    logarithmic = twc.Param("Logscale?  Boolean!", default=False)

    def prepare(self):
        data = self.flat_fetch()
        self.p_data = [[item[1] for item in series['data']] for series in data]
        if self.logarithmic:
            self.p_data = [
                [
                    math.log(value+1) for value in series
                ] for series in self.p_data
            ]
        super(FlatRRDStreamGraph, self).prepare()
