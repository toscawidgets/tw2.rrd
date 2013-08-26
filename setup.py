from setuptools import setup, find_packages

f = open('README.rst')
long_description = f.read().strip()
long_description = long_description.split('split here', 1)[1]
f.close()

setup(
    name='tw2.rrd',
    version='2.1.0',
    description='tw2/rrdtool mashups!  plot your rrdtool data on the web',
    long_description=long_description,
    author='Ralph Bean',
    author_email='rbean@redhat.com',
    url='http://github.com/toscawidgets/tw2.rrd',
    install_requires=[
        "tw2.jqplugins.jqplot",
        "tw2.jqplugins.flot",
        "tw2.protovis.conventional",
        "tw2.protovis.custom",
        "tw2.protovis.hierarchies",
        "tw2.jit",
        # Constrain version due to the following bug
        # http://code.google.com/p/pyrrd/issues/detail?id=26
        "pyrrd==0.0.7",
    ],
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages = ['tw2'],
    zip_safe=False,
    include_package_data=True,
    entry_points="""
        [tw2.widgets]
        # Register your widgets so they can be listed in the WidgetBrowser
        tw2.rrd = tw2.rrd
    """,
    keywords = [
        'toscawidgets.widgets',
    ],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Environment :: Web Environment :: ToscaWidgets',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Widget Sets',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: JavaScript',
    ],
)
