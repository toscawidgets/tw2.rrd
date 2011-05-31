import tw2.core as twc
import tw2.core.util as util

import tw2.jit
import tw2.protovis.hierarchies

import os

from tw2.rrd.widgets.core import RRDBaseMixin

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


class NestedRRDProtoCirclePackingWidget(
    tw2.protovis.hierarchies.CirclePackingWidget, RRDNestedMixin):

    p_data = twc.Variable("Internally produced.")
    method = twc.Param(
        "Method for consolidating values.  Either 'sum' or 'average'",
        default='average')
    root_title = twc.Param("Root title", default=None)

    def prepare(self):
        if not self.root_title:
            raise ValueError, "Root title is required."

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

class NestedRRDJitTreeMap(tw2.jit.TreeMap, RRDNestedMixin):
    data = twc.Variable("Internally produced.")
    method = twc.Param(
        "Method for consolidating values.  Either 'sum' or 'average'",
        default='average')
    root_title = twc.Param("Root title", default=None)

    postInitJSCallback = twc.JSSymbol(
        src="(function (jitwidget) { jitwidget.refresh(); })")


    def make_from_nested(self, data):
        res = []
        for i in range(len(data)):
            key1 = data[i]['label']
            children = []
            for j in range(len(data[i]['data'])):
                key2 = data[i]['data'][j]['label']
                value = sum([
                    item[1] for item in data[i]['data'][j]['data']
                ])

                if self.method == 'average':
                    value = float(value) / len(data[i]['data'][j]['data'])

                if value == 0:
                    continue

                children.append(self.make_node(
                    primary=key2,
                    secondary=key1,
                    value=value,
                    children=[],
                ))

            if not children:
                continue

            res.append(
                self.make_node(
                    primary=key1,
                    secondary=None,
                    children=children,
                    value=sum([
                        c['data']['$area'] for c in children
                    ]),
                )
            )

        return res

    def make_color(self, value, _max, _min):
        lower, upper = 0x025167 , 0x39AECF
        x = float(value - _min)/(_max - _min)
        color = (x * (upper - lower)) + lower
        return "#%0.6x" % color

    def add_colors(self, _max, _min):
        for i in range(len(self.data['children'])):
            for j in range(len(self.data['children'][i]['children'])):
                self.data['children'][i]['children'][j]['data']['$color'] = \
                        self.make_color(
                            self.data['children'][i]['children'][j]['data']['$area'],
                            _max, _min
                        )

    def find_bounds(self):
        _min, _max = 10000000000, 0
        for i in range(len(self.data['children'])):
            for j in range(len(self.data['children'][i]['children'])):
                v = self.data['children'][i]['children'][j]['data']['$area']
                if v < _min:
                    _min = v
                if v > _max:
                    _max = v

        return _min, _max

    def make_node(self, primary, secondary, value, children):
        return {
            'id' : str(primary) + "-" + str(secondary),
            'name' : primary,
            'children' : children,
            'data' : {
                '$area' : value,
            },
        }

    def prepare(self):
        if not self.root_title:
            raise ValueError, "Root title is required."

        raw_data = self.nested_fetch()

        self.data = {
            'id' : 'root',
            'name' : self.root_title,
            'children' : self.make_from_nested(raw_data),
        }
        _min, _max = self.find_bounds()
        self.add_colors(_max, _min)
        super(NestedRRDJitTreeMap, self).prepare()
