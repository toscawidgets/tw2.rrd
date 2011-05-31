import tw2.core as twc
import tw2.core.util as util

import tw2.jit
import tw2.jqplugins.flot
import tw2.protovis.custom
import tw2.protovis.conventional
import tw2.protovis.hierarchies

import pyrrd.rrd

import datetime
import time
import math
import os

class RRDBaseMixin(twc.Widget):
    """ Baseclass for RRD Mixins.  Should not be used directly. """

    start = twc.Param("Start as a python datetime")
    end = twc.Param("End as a python datetime")
    timedelta = twc.Param(
        "Overridden if `start` and `end` are specified.",
        default=datetime.timedelta(days=365)
    )
    steps = twc.Param("Number of datapoints to gather.", default=100)
    hide_zeroes = twc.Param("Strip zero-valued series?", default=True)
    consolidation_function = twc.Param(
        "rrdtool consolidation function to use.", default='AVERAGE')
    datasource_name = twc.Param(
        "rrdtool datasource name to use.", default='sum')

    @classmethod
    def sanity(cls):
        if not hasattr(cls, 'end'):
            cls.end = datetime.datetime.now()

        if not hasattr(cls, 'start'):
            cls.start = cls.end - cls.timedelta

        if cls.end <= cls.start:
            raise ValueError, "end <= start"

    @classmethod
    def file2name(cls, fname):
        """ Convert a filename to an `attribute` name """
        return fname.split('/')[-1].split('.')[0]

    @classmethod
    def directory2name(cls, dname):
        """ Convert a filename to an `attribute` name """
        name = dname.split('/')[-1]
        if name == '':
            name = dname.split('/')[-2]
        return name

    @classmethod
    def _do_flat_fetch(cls, rrd_filenames):
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
        data = [
            d.fetch(
                cf=cls.consolidation_function,
                resolution=resolution,
                start=start_s,
                end=end_s
            )[cls.datasource_name] for d in rrds
        ]

        # Convert from 'nan' to 0.
        for i in range(len(data)):
            for j in range(len(data[i])):
                if math.isnan(data[i][j][1]):
                    data[i][j] = (data[i][j][0], 0)

        # Remove all zero-valued series?
        if cls.hide_zeroes:
            together = zip(data, labels)
            together = [t for t in together if sum([
                data_point[1] for data_point in t[0]
            ]) != 0]
            if len(together) != 0:
                data, labels = [list(t) for t in zip(*together)]

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


class RRDNestedMixin(RRDBaseMixin):
    rrd_directories = twc.Param(
        """ A collection of rrd_directories.

        This can be of the following form::

            - A list of directories containing .rrd files.
        """)

    @classmethod
    def nested_fetch(cls):
        cls.sanity()

        if type(cls.rrd_directories) != list:
            raise ValueError, "rrd_directories must be a list"

        if not cls.rrd_directories:
            raise ValueError, "rrd_directories is empty"

        types = [type(item) for item in cls.rrd_directories]
        if len(list(set(types))) != 1:
            raise ValueError, "rrd_directories must be of homogeneous form"

        _type = types[0]
        if not _type in [str]:
            raise ValueError, "rrd_directories items must be 'str'"

        rrd_directories = cls.rrd_directories
        if _type == str:
            rrd_directories = [
                (util.name2label(cls.directory2name(d)), d)
                for d in rrd_directories
            ]

        lens = [len(item) for item in rrd_directories]
        if len(list(set(lens))) != 1:
            raise ValueError, "rrd_directories items must be of the same length"

        _len = lens[0]
        if _len != 2:
            raise ValueError, "rrd_directories items must be of length 2"

        for item in rrd_directories:
            if not os.path.exists(item[1]):
                raise ValueError, "rrd_directory %s does not exist." % item[1]
            if not os.path.isdir(item[1]):
                raise ValueError, "rrd_directory %s is not a file." % item[1]

        ###################################
        # Done error checking.
        # Now we can actually get the data.
        ###################################

        labels = [item[0] for item in rrd_directories]
        data = []
        for name, directory in rrd_directories:
            rrd_filenames = [
                (cls.file2name(directory+fname), directory+fname)
                for fname in os.listdir(directory) if fname.endswith('.rrd')
            ]
            data.append(cls._do_flat_fetch(rrd_filenames))

        # Wrap up the output into a list of dicts
        return [
            {
                'data' : data[i],
                'label' : labels[i],
            } for i in range(len(data))
        ]


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

class NestedRRDProtoCirclePackingWidget(
    tw2.protovis.hierarchies.CirclePackingWidget, RRDNestedMixin):

    p_data = twc.Variable("Internally produced.")
    method = twc.Param(
        "Method for consolidating values.  Either 'sum' or 'average'",
        default='average')

    def prepare(self):
        if not self.method in ['sum', 'average']:
            raise ValueError, "Illegal value '%s' for method" % self.method

        self.data = self.nested_fetch()
        self.p_data = {}

        for i in range(len(self.data)):
            key1 = self.data[i]['label']
            self.p_data[key1] = {}
            for j in range(len(self.data[i]['data'])):
                key2 = self.data[i]['data'][j]['label']
                value = sum([
                    item[1] for item in self.data[i]['data'][j]['data']
                ])

                if self.method == 'average':
                    value = float(value) / len(self.data[i]['data'][j]['data'])

                if value == 0:
                    continue

                self.p_data[key1][key2] = value

        for key in list(self.p_data.keys()):
            if not self.p_data[key]:
                del self.p_data[key]

        super(NestedRRDProtoCirclePackingWidget, self).prepare()


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
