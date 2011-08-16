import tw2.core as twc
import tw2.core.util as util

import pyrrd.rrd

import calendar
import datetime
import time
import math
import os

# Globals used to cache rrds
_last_access = {}
_data_cache = {}

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
    cache_data = twc.Param(
        "Cache rrdfetch results in memory.", default=True)

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

        # Timezone offset in seconds at start time *including* DST
        tz_offset = start_s - calendar.timegm(cls.start.timetuple())

        labels = [item[0] for item in rrd_filenames]
        data = []
        for label, filename in rrd_filenames:
            timespan = end_s - start_s
            cache_key = "%s:%i:%f:%s" % (
                cls.consolidation_function, resolution, timespan, filename)

            stats = os.stat(filename)
            if stats.st_mtime > _last_access.get(cache_key, 0):
                # Query the round robin database
                results = pyrrd.rrd.RRD(filename).fetch(
                    cf=cls.consolidation_function,
                    resolution=resolution,
                    start=start_s,
                    end=end_s
                )[cls.datasource_name]

                if cls.cache_data:
                    # Cache it
                    _data_cache[cache_key] = results
                    _last_access[cache_key] = time.time()
            else:
                # Just get it from the cache
                results = _data_cache[cache_key]

            data.append(results)


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
        # Also subtract timezone offset in order to display the axis in local time.
        for i in range(len(data)):
            data[i] = [((t-tz_offset)*1000, v) for t, v in data[i]]

        # Wrap up the output into a list of dicts
        return [
            {
                'data' : data[i],
                'label' : labels[i],
            } for i in range(len(data))
        ]
