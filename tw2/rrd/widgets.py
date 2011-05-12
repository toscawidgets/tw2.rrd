import tw2.core as twc
import tw2.core.util as util
import tw2.jqplugins.flot as flot

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

        labels = [item[0] for item in rrd_filenames]
        rrds = [pyrrd.rrd.RRD(item[1]) for item in rrd_filenames]

        # Query the round robin database
        # TODO -- are there other things to return other than 'sum'?
        # TODO -- resolution is actually irrelevant.  need to fix that
        data = [d.fetch(cf, resolution, start_s, end_s)['sum'] for d in rrds]

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


class RRDFlotWidget(flot.FlotWidget, RRDMixin):
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
