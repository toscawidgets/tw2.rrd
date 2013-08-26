tw2.rrd
=======

:Author: Ralph Bean <rbean@redhat.com>

.. comment: split here

RRD (round-robin database) data visualization widgets.

You can use the widgets in this module to analyze your data from rrdtool
(usually collected by another tool like collectd or ganglia or.. well, there
are many).

Widgets, by and large, need to either be given a ``rrd_filenames`` list that
tells them what rrd files to graph explicitly, or an ``rrd_directories`` list
that tells them where to look for rrd files (they'll graph every file they find
in the directory).

Take a look at the `samples.py file
<https://github.com/toscawidgets/tw2.rrd/blob/develop/tw2/rrd/samples.py>`_ for
inspiration.

Sampling tw2.rrd in the WidgetBrowser
-------------------------------------

The best way to scope out ``tw2.rrd`` is to load its widgets in the
``tw2.devtools`` WidgetBrowser.  To see the source code that configures them,
check out ``tw2.rrd/tw2/rrd/samples.py``

To give it a try you'll need git, python, and `virtualenvwrapper
<http://pypi.python.org/pypi/virtualenvwrapper>`_.  Run::

    $ git clone git://github.com/toscawidgets/tw2.rrd.git
    $ cd tw2.rrd
    $ mkvirtualenv tw2.rrd
    (tw2.rrd) $ pip install tw2.devtools
    (tw2.rrd) $ python setup.py develop
    (tw2.rrd) $ paster tw2.browser

...and browse to http://localhost:8000/ to check it out.
