from django.conf import settings
from django.contrib.sites.models import Site
from django.db import models, connection, DatabaseError

try:
    from django.apps import apps
except ImportError:
    from django.db.models import loading as apps

from django.utils.translation import gettext_lazy as _
from keyedcache import cache_key, cache_get, cache_set, NotCachedError
from keyedcache.models import CachedObjectMixin
from livesettings.overrides import get_overrides
import logging

log = logging.getLogger('configuration.models')

__all__ = ['SettingNotSet', 'Setting', 'LongSetting', 'find_setting']

try:
    is_site_initializing
except:
    is_site_initializing = True  # until the first success find "django_site" table, by any thread
    is_first_warn = True


def _safe_get_siteid(site):
    global is_site_initializing, is_first_warn
    if not site:
        try:
            site = Site.objects.get_current()
            siteid = site.id
        except Exception as e:
            if is_site_initializing and isinstance(e, DatabaseError) and str(e).find('django_site') > -1:
                if is_first_warn:
                    log.warning(str(e).strip())
                    is_first_warn = False
                log.warning('Can not get siteid; probably before syncdb; ROLLBACK')
                connection._rollback()
            else:
                is_site_initializing = False
            siteid = settings.SITE_ID
        else:
            is_site_initializing = False
    else:
        siteid = site.id
    return siteid


def find_setting(group, key, site=None):
    """Get a setting or longsetting by group and key, cache and return it."""

    siteid = _safe_get_siteid(site)
    setting = None

    use_db, overrides = get_overrides(siteid)
    ck = cache_key('Setting', siteid, group, key)

    if use_db:
        try:
            setting = cache_get(ck)

        except NotCachedError as nce:
            if hasattr(apps, 'ready'):
                app_cache_ready = apps.ready
            else:
                app_cache_ready = apps.app_cache_ready()

            if app_cache_ready:
                try:
                    setting = Setting.objects.get(site__id__exact=siteid, key__exact=key, group__exact=group)

                except Setting.DoesNotExist:
                    # maybe it is a "long setting"
                    try:
                        setting = LongSetting.objects.get(site__id__exact=siteid, key__exact=key, group__exact=group)

                    except LongSetting.DoesNotExist:
                        pass

                cache_set(ck, value=setting)

    else:
        grp = overrides.get(group, None)
        if grp and key in grp:
            val = grp[key]
            setting = ImmutableSetting(key=key, group=group, value=val)
            log.debug('Returning overridden: %s', setting)

    if not setting:
        raise SettingNotSet(key, cachekey=ck)

    return setting


class SettingNotSet(Exception):
    def __init__(self, k, cachekey=None):
        self.key = k
        self.cachekey = cachekey
        self.args = [self.key, self.cachekey]


class SettingManager(models.Manager):
    def get_query_set(self):
        return self.get_queryset()

    def get_queryset(self):
        if hasattr(super(SettingManager, self), 'get_queryset'):
            all = super(SettingManager, self).get_queryset()
        else:
            all = super(SettingManager, self).get_query_set()

        siteid = _safe_get_siteid(None)
        return all.filter(site__id__exact=siteid)


class ImmutableSetting(object):
    def __init__(self, group="", key="", value="", site=1):
        self.site = site
        self.group = group
        self.key = key
        self.value = value

    def cache_key(self, *args, **kwargs):
        return cache_key('OverrideSetting', self.site, self.group, self.key)

    def delete(self):
        pass

    def save(self, *args, **kwargs):
        pass

    def __repr__(self):
        return "ImmutableSetting: %s.%s=%s" % (self.group, self.key, self.value)


class Setting(models.Model, CachedObjectMixin):
    site = models.ForeignKey(Site, verbose_name=_('Site'), on_delete=models.CASCADE)
    group = models.CharField(max_length=100, blank=False, null=False)
    key = models.CharField(max_length=100, blank=False, null=False)
    value = models.CharField(max_length=255, blank=True)

    objects = SettingManager()

    def __bool__(self):
        return self.id is not None

    def __str__(self):
        return f'{self.group}.{self.key} = {self.value}'

    def cache_key(self, *args, **kwargs):
        return cache_key('Setting', self.site, self.group, self.key)

    def delete(self, using=None, keep_parents=False):
        self.cache_delete()
        super(Setting, self).delete()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        try:
            site = self.site
        except Site.DoesNotExist:
            self.site = Site.objects.get_current()

        super(Setting, self).save(force_insert=force_insert, force_update=force_update)

        self.cache_set()

    class Meta:
        unique_together = ('site', 'group', 'key')
        app_label = 'livesettings'


class LongSettingManager(models.Manager):
    def get_query_set(self):
        return self.get_queryset()

    def get_queryset(self):
        if hasattr(super(LongSettingManager, self), 'get_queryset'):
            all = super(LongSettingManager, self).get_queryset()
        else:
            all = super(LongSettingManager, self).get_query_set()

        siteid = _safe_get_siteid(None)
        return all.filter(site__id__exact=siteid)


class LongSetting(models.Model, CachedObjectMixin):
    """A Setting which can handle more than 255 characters"""
    site = models.ForeignKey(Site, verbose_name=_('Site'), on_delete=models.CASCADE)
    group = models.CharField(max_length=100, blank=False, null=False)
    key = models.CharField(max_length=100, blank=False, null=False)
    value = models.TextField(blank=True)

    objects = LongSettingManager()

    def __bool__(self):
        return self.id is not None

    def __str__(self):
        return f'{self.group}.{self.key} = {self.value}'

    def cache_key(self, *args, **kwargs):
        # note same cache pattern as Setting.  This is so we can look up in one check.
        # they can't overlap anyway, so this is moderately safe.  At the worst, the
        # Setting will override a LongSetting.
        return cache_key('Setting', self.site, self.group, self.key)

    def delete(self, using=None, keep_parents=False):
        self.cache_delete()
        super(LongSetting, self).delete()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        try:
            site = self.site
        except Site.DoesNotExist:
            self.site = Site.objects.get_current()
        super(LongSetting, self).save(force_insert=force_insert, force_update=force_update)
        self.cache_set()

    class Meta:
        unique_together = ('site', 'group', 'key')
        app_label = 'livesettings'
