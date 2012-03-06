tw2.rrd
=======

:Author: Ralph Bean <rbean@redhat.com>

.. comment: split here

TODO -- documentation.  :)

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
