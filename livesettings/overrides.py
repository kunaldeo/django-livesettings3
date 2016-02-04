"""Allows livesettings to be "locked down" and no longer use the settings page or the database
for settings retrieval.
"""

from django.conf import settings as djangosettings
from django.contrib.sites.models import Site

__all__ = ['get_overrides']


def _safe_get_siteid(site):
    if not site:
        try:
            site = Site.objects.get_current()
            siteid = site.id
        except:
            siteid = djangosettings.SITE_ID
    else:
        siteid = site.id
    return siteid


def get_overrides(siteid=-1):
    """Check to see if livesettings is allowed to use the database.  If not, then
    it will only use the values in the dictionary, LIVESETTINGS_OPTIONS[SITEID]['SETTINGS'],
    this allows 'lockdown' of a live site.

    The LIVESETTINGS dict must be formatted as follows::

    LIVESETTINGS_OPTIONS = {
            1 : {
                    'DB' : False,  # or True
                    'SETTINGS' : {
                        'GROUPKEY' : {'KEY', val, 'KEY2', val},
                        'GROUPKEY2' : {'KEY', val, 'KEY2', val},
                    }
                }
            }

    In the settings dict above, the "val" entries must exactly match the format 
    stored in the database for a setting, which is a string representation of the
    value. Do not use e.g. a literal True or an integer.
    The easiest way to get a right formated expression is by the URL
    http://your.site/settings/export/

    Returns a tuple (DB_ALLOWED, SETTINGS)
    """
    overrides = (True, {})
    if hasattr(djangosettings, 'LIVESETTINGS_OPTIONS'):
        if siteid == -1:
            siteid = _safe_get_siteid(None)

        opts = djangosettings.LIVESETTINGS_OPTIONS
        if siteid in opts:
            opts = opts[siteid]
            overrides = (opts.get('DB', True), opts['SETTINGS'])

    return overrides
