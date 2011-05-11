import tw2.core as twc
import tw2.jqplugins.flot as flot

import pyrrd.rrd

import datetime
import time
import math

class RRDMixin(twc.Widget):
    rrd_filename = twc.Param(
        "filename of a `.rrd` file.",
        default=twc.Required
    )
    start = twc.Param("Start as a python datetime")
    end = twc.Param("End as a python datetime")

    @classmethod
    def fetch(cls, cf='AVERAGE', steps=100):
        if not hasattr(cls, 'end'):
            cls.end = datetime.datetime.now()

        if not hasattr(cls, 'start'):
            cls.start = cls.end - datetime.timedelta(days=365)

        if cls.end <= cls.start:
            raise ValueError, "end <= start"

        rrd = pyrrd.rrd.RRD(cls.rrd_filename)

        # TODO -- is this necessary?
        rrd.load(cls.rrd_filename, include_data=True)

        # Convert to seconds since the epoch
        end_s = int(time.mktime(cls.end.timetuple()))
        start_s = int(time.mktime(cls.start.timetuple()))

        # Convert `steps` to `resolution` (seconds per step)
        resolution = (end_s - start_s)/steps

        # Query the round robin database
        result = rrd.fetch(cf, resolution, start_s, end_s)

        # TODO -- are there other things to return?
        result = result['sum']

        # Convert from 'nan' to 0.
        for i in range(len(result)):
            if math.isnan(result[i][1]):
                result[i] = (result[i][0], 0)

        return result


class RRDFlotWidget(flot.FlotWidget, RRDMixin):
    data = twc.Variable("Internally produced.")
    end = datetime.datetime.now()
    start = datetime.datetime.now() - datetime.timedelta(days=365)

    def prepare(self):
        # TODO -- can this be moved to post_define?
        self.data = [
            {
                'data' : self.fetch(),
                'label' : self.label,
            }
        ]
        super(RRDFlotWidget, self).prepare()
