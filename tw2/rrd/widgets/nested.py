import tw2.core as twc
import tw2.core.util as util

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
