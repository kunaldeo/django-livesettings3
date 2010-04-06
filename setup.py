from setuptools import setup, find_packages

VERSION = (1, 4, 3)

# Dynamically calculate the version based on VERSION tuple
if len(VERSION)>2 and VERSION[2] is not None:
    str_version = "%d.%d_%s" % VERSION[:3]
else:
    str_version = "%d.%d" % VERSION[:2]

version= str_version

setup(
    name = 'django-livesettings',
    version = version,
    description = "livesettings",
    long_description = """Django-Livesettings is a project split from the Satchmo Project. It provides the ability to configure settings via an admin interface, rather than by editing "settings.py".""",
    author = 'Bruce Kroeze',
    author_email = 'bruce@ecomsmith.com',
    url = 'http://bitbucket.org/bkroeze/django-livesettings/',
    license = 'New BSD License',
    platforms = ['any'],
    classifiers = ['Development Status :: 4 - Beta',
                   'Environment :: Web Environment',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Framework :: Django'],
    packages = find_packages(),
    setup_requires=["setuptools_hg"],
    include_package_data = True,
)
