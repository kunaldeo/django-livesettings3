import logging

import keyedcache

import livesettings
from django.conf import settings as djangosettings
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse
from livesettings.functions import config_register, config_exists, \
    config_register_list, config_get, ConfigurationSettings, config_add_choice, \
    config_choice_values, config_value, config_get_group, config_collect_values
from livesettings.models import SettingNotSet, LongSetting
from livesettings.values import IntegerValue, BASE_GROUP, StringValue, \
    ConfigurationGroup, BooleanValue, MultipleStringValue, LongStringValue, \
    PasswordValue, DecimalValue, DurationValue, FloatValue, PositiveIntegerValue, \
    LongMultipleStringValue, ModuleValue

log = logging.getLogger('test');


class ConfigurationFunctionTest(TestCase):
    def testSetSingleConfigItem(self):
        value = IntegerValue(BASE_GROUP, 'SingleItem')
        config_register(value)
        self.assertTrue(config_exists(BASE_GROUP, 'SingleItem'))

    def testSetTwoConfigItems(self):
        s = [IntegerValue(BASE_GROUP, 'testTwoA'), StringValue(BASE_GROUP, 'testTwoB')]
        config_register_list(*s)

        self.assertTrue(config_exists(BASE_GROUP, 'testTwoA'))
        self.assertTrue(config_exists(BASE_GROUP, 'testTwoB'))

    def testSetGroup(self):
        g1 = ConfigurationGroup('test1', 'test1')
        value = IntegerValue(g1, 'SingleGroupedItem')
        config_register(value)
        self.assertFalse(config_exists(BASE_GROUP, 'SingleGroupedItem'))
        self.assertTrue(config_exists(g1, 'SingleGroupedItem'))


class ConfigurationTestSettings(TestCase):
    def setUp(self):
        # clear out cache from previous runs
        keyedcache.cache_delete()
        g = ConfigurationGroup('test2', 'test2')
        self.g = g
        config_register(StringValue(g, 's1'))
        config_register(IntegerValue(g, 's2', default=10))
        config_register(IntegerValue(g, 's3', default=10))

    def testSetSetting(self):
        c = config_get('test2', 's1')
        c.update('test')

        self.assertEqual(c.value, 'test')
        self.assertEqual(c.setting.value, 'test')

    def testSettingDefault(self):
        c = config_get('test2', 's2')
        self.assertEqual(c.value, 10)

    def testSetAndReset(self):
        """Test setting one value and then updating"""
        c = config_get('test2', 's1')
        c.update('test1')

        self.assertEqual(c.value, 'test1')

        # should be true, since it is an update
        self.assertTrue(c.update('test2'))
        self.assertEqual(c.value, 'test2')

    def testTwice(self):
        """Config items should respond False to duplicate requests to update."""

        c = config_get('test2', 's1')
        c.update('test1')

        self.assertFalse(c.update('test1'))

    def testDeletesDefault(self):
        c = config_get('test2', 's3')
        # false because it isn't saving a default value
        self.assertFalse(c.update(10))

        self.assertTrue(c.update(20))
        self.assertEqual(c.value, 20)
        try:
            s = c.setting
        except SettingNotSet:
            self.fail("Should have a setting now")

        # now delete and go back to no setting by setting the default
        self.assertTrue(c.update(10))
        self.assertEqual(c.value, 10)

        try:
            s = c.setting
            self.fail('Should throw SettingNotSet')
        except SettingNotSet:
            pass


class ConfigTestDotAccess(TestCase):
    def setUp(self):
        # clear out cache from previous runs
        keyedcache.cache_delete()

        g = ConfigurationGroup('test3', 'test3')
        self.g = g
        c1 = config_register(BooleanValue(g, 's1', default=True))
        c2 = config_register(IntegerValue(g, 's2', default=10))
        c2.update(100)

    def testDotAccess(self):
        self.assertTrue(ConfigurationSettings().test3.s1.value)
        self.assertEqual(ConfigurationSettings().test3.s2.value, 100)

    def testSettingProperty(self):
        c = config_get('test3', 's2')
        s = c.setting
        self.assertTrue(s.value, 100)

    def testDictValues(self):
        d = self.g.dict_values()
        self.assertEqual(d, {'s1': True, 's2': 100})


class ConfigTestModuleValue(TestCase):
    def setUp(self):
        # clear out cache from previous runs
        keyedcache.cache_delete()

        g = ConfigurationGroup('modules', 'module test')
        self.g = g
        self.c = config_register(ModuleValue(g, 'test'))

    def testModule(self):
        c = config_get('modules', 'test')
        c.update('django')

        self.assertTrue(hasattr(self.c.value, 'get_version'))


class ConfigTestSortOrder(TestCase):
    def setUp(self):
        # clear out cache from previous runs
        keyedcache.cache_delete()

        g1 = ConfigurationGroup('group1', 'Group 1', ordering=-1001)
        g2 = ConfigurationGroup('group2', 'Group 2', ordering=-1002)
        g3 = ConfigurationGroup('group3', 'Group 3', ordering=-1003)

        self.g1 = g1
        self.g2 = g2
        self.g3 = g3

        self.g1c1 = config_register(IntegerValue(g1, 'c1'))
        self.g1c2 = config_register(IntegerValue(g1, 'c2'))
        self.g1c3 = config_register(IntegerValue(g1, 'c3'))

        self.g2c1 = config_register(IntegerValue(g2, 'c1'))
        self.g2c2 = config_register(IntegerValue(g2, 'c2'))
        self.g2c3 = config_register(IntegerValue(g2, 'c3'))

        self.g3c1 = config_register(IntegerValue(g3, 'c1'))
        self.g3c2 = config_register(IntegerValue(g3, 'c2'))
        self.g3c3 = config_register(IntegerValue(g3, 'c3'))

    def testGroupOrdering(self):
        mgr = ConfigurationSettings()
        self.assertEqual(mgr[2].key, self.g1.key)
        self.assertEqual(mgr[1].key, self.g2.key)
        self.assertEqual(mgr[0].key, self.g3.key)


class TestMultipleValues(TestCase):
    def setUp(self):
        # clear out cache from previous runs
        keyedcache.cache_delete()

        g1 = ConfigurationGroup('m1', 'Multiple Group 1', ordering=1000)
        self.g1 = g1

        self.g1c1 = config_register(MultipleStringValue(g1,
                                                        'c1',
                                                        choices=((1, 'one'), (2, 'two'), (3, 'three'))))

    def testSave(self):
        c = config_get('m1', 'c1')
        c.update([1, 2])
        self.assertEqual(c.value, [1, 2])

    def testAddChoice(self):
        config_add_choice('m1', 'c1', (4, 'four'))
        c = config_get('m1', 'c1')
        self.assertEqual(c.choices, ((1, 'one'), (2, 'two'), (3, 'three'), (4, 'four')))

    def testChoiceValues(self):
        self.g1c1.update([1, 2])

        self.assertEqual(self.g1c1.value, [1, 2])
        self.assertEqual(self.g1c1.choice_values, [(1, 'one'), (2, 'two')])

        choices = config_choice_values('m1', 'c1')
        self.assertEqual(choices, [(1, 'one'), (2, 'two')])


class TestMultipleValuesWithDefault(TestCase):
    def setUp(self):
        # clear out cache from previous runs
        keyedcache.cache_delete()

        g1 = ConfigurationGroup('mv2', 'Multiple Group 2', ordering=1000)
        self.g1 = g1

        self.g1c1 = config_register(MultipleStringValue(g1,
                                                        'c1',
                                                        choices=((1, 'one'), (2, 'two'), (3, 'three')),
                                                        default=[1, 2]))

    def testDefault(self):
        c = config_get('mv2', 'c1')
        self.assertEqual(c.value, [1, 2])

        c.update([1, 2, 3])
        self.assertEqual(c.value, [1, 2, 3])


class ConfigTestChoices(TestCase):
    def testAddPreregisteredChoice(self):
        """Test that we can register choices before the config is actually set up."""
        config_add_choice('ctg1', 'c1', ('a', 'Item A'))
        config_add_choice('ctg1', 'c1', ('b', 'Item B'))
        config_add_choice('ctg1', 'c1', ('c', 'Item C'))

        g1 = ConfigurationGroup('ctg1', 'Choice 1', ordering=1000)
        config_register(StringValue(g1, 'c1'))

        c = config_get('ctg1', 'c1')

        self.assertEqual(c.choices, [('a', 'Item A'), ('b', 'Item B'), ('c', 'Item C')])


class ConfigTestRequires(TestCase):
    def setUp(self):
        # clear out cache from previous runs
        keyedcache.cache_delete()

        g1 = ConfigurationGroup('req1', 'Requirements 1', ordering=1000)

        self.g1 = g1

        bool1 = config_register(BooleanValue(g1, 'bool1', default=False, ordering=1))
        bool2 = config_register(BooleanValue(g1, 'bool2', ordering=2))

        self.g1c1 = config_register(IntegerValue(g1, 'c1', requires=bool1, ordering=3))

        self.g1c2 = config_register(IntegerValue(g1, 'c2', requires=bool2, ordering=4))
        self.g1c3 = config_register(IntegerValue(g1, 'c3', ordering=5))

        bool2.update(True)

    def testSimpleRequires(self):
        v = config_value('req1', 'bool2')
        self.assertTrue(v)

        keys = [cfg.key for cfg in self.g1]
        self.assertEqual(keys, ['bool1', 'bool2', 'c2', 'c3'])

        c = config_get('req1', 'bool1')
        c.update(True)

        keys = [cfg.key for cfg in self.g1]
        self.assertEqual(keys, ['bool1', 'bool2', 'c1', 'c2', 'c3'])


class ConfigTestRequiresChoices(TestCase):
    def setUp(self):
        # clear out cache from previous runs
        keyedcache.cache_delete()

        g1 = ConfigurationGroup('req2', 'Requirements 2', ordering=1000)

        self.g1 = g1

        choices1 = config_register(MultipleStringValue(BASE_GROUP, 'rc1', ordering=1))

        self.g1c1 = config_register(IntegerValue(g1, 'c1', requires=choices1, ordering=3))
        self.g1c2 = config_register(IntegerValue(g1, 'c2', requires=choices1, ordering=4))
        self.g1c3 = config_register(IntegerValue(g1, 'c3', ordering=5))

        choices1.update('c1')

        g2 = ConfigurationGroup('req3', 'Requirements 3', ordering=1000)

        self.g2 = g2

        choices2 = config_register(StringValue(BASE_GROUP, 'choices2', ordering=1))

        self.g2c1 = config_register(IntegerValue(g2, 'c1', requires=choices2, ordering=3))
        self.g2c2 = config_register(IntegerValue(g2, 'c2', requires=choices2, ordering=4))
        self.g2c3 = config_register(IntegerValue(g2, 'c3', requires=choices2, ordering=5))

        choices2.update('c1')

    def testSimpleRequiresChoices(self):
        v = config_value('BASE', 'rc1')
        self.assertEqual(v, ['c1'])

        g = config_get_group('req2')
        keys = [cfg.key for cfg in g]
        self.assertEqual(keys, ['c1', 'c3'])

        c = config_get('BASE', 'rc1')
        c.update(['c1', 'c2'])

        g = config_get_group('req2')
        keys = [cfg.key for cfg in g]
        self.assertEqual(keys, ['c1', 'c2', 'c3'])

    def testRequiresSingleValue(self):
        v = config_value('BASE', 'choices2')
        self.assertEqual(v, 'c1')

        keys = [cfg.key for cfg in self.g2]
        self.assertEqual(keys, ['c1'])

        c = config_get('BASE', 'choices2')
        c.update('c2')

        keys = [cfg.key for cfg in self.g2]
        self.assertEqual(keys, ['c2'])


class ConfigTestRequiresValue(TestCase):
    def setUp(self):
        # clear out cache from previous runs
        keyedcache.cache_delete()

        g1 = ConfigurationGroup('reqval', 'Requirements 3', ordering=1000)

        self.g1 = g1

        choices1 = config_register(MultipleStringValue(BASE_GROUP, 'valchoices', ordering=1))

        self.g1c1 = config_register(IntegerValue(g1, 'c1', requires=choices1, requiresvalue='foo', ordering=3))
        self.g1c2 = config_register(IntegerValue(g1, 'c2', requires=choices1, requiresvalue='bar', ordering=4))
        self.g1c3 = config_register(IntegerValue(g1, 'c3', ordering=5))

        choices1.update('foo')

        g2 = ConfigurationGroup('reqval2', 'Requirements 4', ordering=1000)

        self.g2 = g2

        choices2 = config_register(StringValue(BASE_GROUP, 'valchoices2', ordering=1,
                                               choices=(('a', 'test a'), ('b', 'test b'), ('c', 'test c'))))

        self.g2c1 = config_register(IntegerValue(g2, 'c1', requires=choices2, requiresvalue='a', ordering=3))
        self.g2c2 = config_register(IntegerValue(g2, 'c2', requires=choices2, requiresvalue='b', ordering=4))
        self.g2c3 = config_register(IntegerValue(g2, 'c3', requires=choices2, requiresvalue='c', ordering=5))

        choices2.update('a')

    def testRequiresValue(self):
        v = config_value('BASE', 'valchoices')
        self.assertEqual(v, ['foo'])

        g = config_get_group('reqval')

        keys = [cfg.key for cfg in g]
        self.assertEqual(keys, ['c1', 'c3'])

        c = config_get('BASE', 'valchoices')
        c.update(['foo', 'bar'])

        g = config_get_group('reqval')
        keys = [cfg.key for cfg in g]
        self.assertEqual(keys, ['c1', 'c2', 'c3'])

    def testRequiresSingleValue(self):
        v = config_value('BASE', 'valchoices2')
        self.assertEqual(v, 'a')

        keys = [cfg.key for cfg in self.g2]
        self.assertEqual(keys, ['c1'])

        c = config_get('BASE', 'valchoices2')
        c.update('b')

        keys = [cfg.key for cfg in self.g2]
        self.assertEqual(keys, ['c2'])


class ConfigTestGroupRequires(TestCase):
    def setUp(self):
        # clear out cache from previous runs
        keyedcache.cache_delete()

        choices1 = config_register(MultipleStringValue(BASE_GROUP, 'groupchoice', ordering=1))
        choices2 = config_register(MultipleStringValue(BASE_GROUP, 'groupchoice2', ordering=1))

        g1 = ConfigurationGroup('groupreq', 'Requirements 4', ordering=1000, requires=choices1)
        self.g1 = g1

        self.g1c1 = config_register(IntegerValue(g1, 'c1', ordering=3))
        self.g1c2 = config_register(IntegerValue(g1, 'c2', requires=choices2, requiresvalue='bar', ordering=4))
        self.g1c3 = config_register(IntegerValue(g1, 'c3', ordering=5))

    def testRequiresValue(self):
        c = config_get('BASE', 'groupchoice')
        self.assertEqual(c.value, [])

        keys = [cfg.key for cfg in self.g1]
        self.assertEqual(keys, [])

        c2 = config_get('BASE', 'groupchoice2')
        c2.update('bar')

        keys = [cfg.key for cfg in self.g1]
        self.assertEqual(keys, ['c2'])

        c.update(['groupreq'])

        keys = [cfg.key for cfg in self.g1]
        self.assertEqual(keys, ['c1', 'c2', 'c3'])


class ConfigCollectGroup(TestCase):
    def setUp(self):
        keyedcache.cache_delete()
        choices = config_register(MultipleStringValue(BASE_GROUP, 'collect', ordering=1))
        self.choices = choices

        g1 = ConfigurationGroup('coll1', 'Collection 1')
        g2 = ConfigurationGroup('coll2', 'Collection 2')
        g3 = ConfigurationGroup('coll3', 'Collection 3')

        g1c1 = config_register(StringValue(g1, 'test'))
        g1c2 = config_register(StringValue(g1, 'test1'))
        g2c1 = config_register(StringValue(g2, 'test'))
        g3c1 = config_register(StringValue(g3, 'test'))

        g1c1.update('set a')
        g1c2.update('set b')
        g2c1.update('set a')
        g3c1.update('set d')

        choices.update(['coll1', 'coll3'])

    def testCollectSimple(self):
        v = config_collect_values('BASE', 'collect', 'test')

        self.assertEqual(v, ['set a', 'set d'])

    def testCollectUnique(self):
        self.choices.update(['coll1', 'coll2', 'coll3'])

        v = config_collect_values('BASE', 'collect', 'test', unique=False)

        self.assertEqual(v, ['set a', 'set a', 'set d'])

        v = config_collect_values('BASE', 'collect', 'test', unique=True)

        self.assertEqual(v, ['set a', 'set d'])


class LongSettingTest(TestCase):
    def setUp(self):
        keyedcache.cache_delete()
        wide = config_register(LongStringValue(BASE_GROUP, 'LONG', ordering=1, default="woot"))
        self.wide = wide
        self.wide.update('*' * 1000)

    def testLongStorage(self):
        w = config_value('BASE', 'LONG')
        self.assertEqual(len(w), 1000)
        self.assertEqual(w, '*' * 1000)

    def testShortInLong(self):
        self.wide.update("test")
        w = config_value('BASE', 'LONG')
        self.assertEqual(len(w), 4)
        self.assertEqual(w, 'test')

    def testDelete(self):
        remember = self.wide.setting.id
        self.wide.update('woot')

        try:
            q = LongSetting.objects.get(pk=remember)
            self.fail("Should be deleted")
        except LongSetting.DoesNotExist:
            pass


class OverrideTest(TestCase):
    """Test settings overrides"""

    def setUp(self):
        # clear out cache from previous runs
        keyedcache.cache_delete()

        djangosettings.LIVESETTINGS_OPTIONS = {
            1: {
                'DB': False,
                'SETTINGS': {
                    'overgroup': {
                        's2': '100',
                        'choices': '["one","two","three"]'
                    }
                }
            }
        }

        g = ConfigurationGroup('overgroup', 'Override Group')
        self.g = g
        config_register(StringValue(g, 's1'))
        config_register(IntegerValue(g, 's2', default=10))
        config_register(IntegerValue(g, 's3', default=10))
        config_register(MultipleStringValue(g, 'choices'))

    def tearDown(self):
        djangosettings.LIVESETTINGS_OPTIONS = {}

    def testOverriddenSetting(self):
        """Accessing an overridden setting should give the override value."""
        c = config_get('overgroup', 's2')
        self.assertEqual(c.value, 100)

    def testCantChangeSetting(self):
        """When overridden, setting a value should not work, should get the overridden value"""
        c = config_get('overgroup', 's2')
        c.update(1)

        c = config_get('overgroup', 's2')
        self.assertEqual(c.value, 100)

    def testNotOverriddenSetting(self):
        """Settings which are not overridden should return their defaults"""
        c = config_get('overgroup', 's3')

        self.assertEqual(c.value, 10)

    def testOverriddenListSetting(self):
        """Make sure lists work when overridden"""

        c = config_get('overgroup', 'choices')
        v = c.value
        self.assertEqual(len(v), 3)
        self.assertEqual(v[0], "one")
        self.assertEqual(v[1], "two")
        self.assertEqual(v[2], "three")


@override_settings(ROOT_URLCONF='livesettings.test_urls')
class PermissionTest(TestCase):
    """Test access permissions"""

    def setUp(self):
        from django.contrib.auth.models import Permission, User
        from django.contrib.contenttypes.models import ContentType
        # Users with different permissions
        # staff member
        user1 = User.objects.create_user('warehouseman', 'john@example.com', 'secret')
        user1.is_staff = True
        user1.save()
        # developper with limited permissions
        user2 = User.objects.create_user('cautious_developer', 'fred@example.com', 'secret')
        user2.is_staff = True
        user2.user_permissions.add(Permission.objects.get(codename='change_setting', \
                                                          content_type=ContentType.objects.get(app_label='livesettings',
                                                                                               model='setting')))
        user2.save()
        # superuser
        user3 = User.objects.create_user('superuser', 'paul@example.com', 'secret')
        user3.is_superuser = True
        user3.save()

        keyedcache.cache_delete()
        # Example config
        config_register(IntegerValue(BASE_GROUP, 'SingleItem', default=0))

    def test_unauthorized_form(self):
        "Testing users without enought additional permission"
        # usually login_url_mask % nexturl is '/accounts/login/?next=/settings/'
        login_url_mask = '%s?next=%%s' % reverse('loginview')
        # unauthorized
        response = self.client.get(reverse('satchmo_site_settings'))  # usually '/settings/'
        self.assertRedirects(response, login_url_mask % '/settings/', msg_prefix='unathorized user should first login')
        # few authorized
        self.client.login(username='warehouseman', password='secret')
        response = self.client.get(reverse('satchmo_site_settings'))
        self.assertRedirects(response, login_url_mask % '/settings/',
                             msg_prefix='user with small permission should not read normal settings')
        # authorized enough but not for secret values
        self.client.login(username='cautious_developer', password='secret')
        response = self.client.get(reverse('settings_export'))  # usually '/settings/export/'
        self.assertRedirects(response, login_url_mask % '/settings/export/',
                             msg_prefix='user without superuser permission should not export sensitive settings')

    def test_authorized_enough(self):
        "Testing a sufficiently authorized user"
        self.client.login(username='cautious_developer', password='secret')
        response = self.client.get(reverse('satchmo_site_settings'))
        self.assertContains(response, 'SingleItem')
        self.client.login(username='superuser', password='secret')
        response = self.client.get(reverse('settings_export'))
        self.assertContains(response, 'LIVESETTINGS_OPTIONS = ')

    def test_export(self):
        "Details of exported settings"
        self.client.login(username='superuser', password='secret')
        val2 = IntegerValue(BASE_GROUP, 'ModifiedItem', default=0)
        config_register(val2)
        val2.update(6789)
        response = self.client.get('/settings/export/')
        self.assertContains(response, "LIVESETTINGS_OPTIONS =", 1)
        self.assertContains(response, "'DB': False", 1)
        self.assertContains(response, "'BASE':", 1)
        self.assertContains(response, "'ModifiedItem': '6789'", 1)

    def test_secret_password(self):
        "Verify that password is saved but not re-echoed if render_value=False"
        # example of value, where reading is more sensitive than writing
        val1 = PasswordValue(BASE_GROUP, 'password_to_reading_external_payment_gateway', render_value=False)
        config_register(val1)
        val1.update('secret')
        val2 = PasswordValue(BASE_GROUP, 'unsecure_password')
        config_register(val2)
        val2.update('unsecure_pwd')
        self.client.login(username='superuser', password='secret')
        response = self.client.get('/settings/')
        self.assertContains(response, 'password_to_reading_external_payment_gateway')
        self.assertNotContains(response, 'secret')
        self.assertContains(response, 'unsecure_password')
        self.assertContains(response, 'unsecure_pwd')


@override_settings(ROOT_URLCONF='livesettings.test_urls')
class WebClientPostTest(TestCase):
    """
    Tests of the web interface with POST.
    These tests require temporary removing all earlier defined values.
    Then are all values restored because it can be important for testing an application which uses livesettings.
    """

    def setUp(self):
        from django.contrib.auth.models import User
        from collections import OrderedDict
        # The following hack works like completely replaced ConfigurationSettings internal state only, if
        # no the same group name is used inside and outside the test.
        self.saved_conf_inst = ConfigurationSettings._ConfigurationSettings__instance.settings
        ConfigurationSettings.__dict__['_ConfigurationSettings__instance'].settings = OrderedDict()

        keyedcache.cache_delete()
        # set new users and values
        user = User.objects.create_user('admin', 'admin@example.com', 'secret')
        user.is_superuser = True
        user.save()
        self.client.login(username='admin', password='secret')
        GROUP2 = ConfigurationGroup('Group2', 'g')
        value = IntegerValue(GROUP2, 'SingleItem')
        config_register(value)

    def tearDown(self):
        # restore the original configuration
        ConfigurationSettings.__dict__['_ConfigurationSettings__instance'].settings = self.saved_conf_inst

    def test_post(self):
        "Tests of POST, verify is saved"
        response = self.client.post('/settings/', {'Group2__SingleItem': '7890'})
        # test can not use assertRedirects because it would consume the next get
        self.assertEqual((response.status_code, response.get('Location', '')), (302, '/settings/'))
        response = self.client.get('/settings/')
        self.assertContains(response, 'Updated')
        self.assertContains(response, '7890')

    def test_empty_fields(self):
        "test an empty value in the form should not raise an exception"

        # Some test features had been temporary commented out before some ..Values classes are fixed
        # because I do not want to display many old inconsistencies now. (hynekcer)
        def extract_val(content):
            regr = re.search(b'SingleItem.*value="([^"]*)"', content, flags=re.MULTILINE)
            return regr and regr.group(1) or ''  # html value

        def get_setting_like_in_db(x):
            try:
                return x.setting.value
            except SettingNotSet:
                return 'Error'

        def test_empty_value_type(value_type, protocol, reject_empty=False):
            "empty value can be accepted or rejected by validation rules"
            value = value_type(GROUP2, 'SingleItem')  # first it does it to easy get the class name
            type_name = value.__class__.__name__
            value = value_type(GROUP2, 'SingleItem', description='type %s' % type_name)
            config_register(value)
            response = self.client.get('/settings/')
            html_value = extract_val(response.content)
            # print '%s "%s"' % (type_name, html_value)
            response = self.client.post('/settings/',
                                        {'Group2__SingleItem': ''})  # See in the traceback a line one level Up
            if reject_empty:
                # option reject_empty had been tested before all Value types were fixed to be similar accepting empty value
                # this is a typical text from validation warning
                self.assertContains(response, 'Please correct the error below.')
            else:
                self.assertRedirects(response, '/settings/')
                response = self.client.get('/settings/')
                html_value = extract_val(response.content)
                # print '%s "%s" "%s" "%s"' % (type_name, html_value, value.value, get_setting_like_in_db(value))
                # self.assertNotContains(response, '&lt;object object at 0x[0-9a-f]+&gt;')  # rendered NOTSET = object()
                # if re.search('SingleItem.*value="', response.content):
                #    self.assertTrue(re.search('SingleItem.*value="([0.]*|\[\])"', response.content))
            protocol.add(value_type)

        #
        import re
        GROUP2 = ConfigurationGroup('Group2', 'g')
        protocol = set()
        # tested values
        test_empty_value_type(BooleanValue, protocol)
        test_empty_value_type(DecimalValue, protocol)
        test_empty_value_type(DurationValue, protocol)
        test_empty_value_type(FloatValue, protocol)
        test_empty_value_type(IntegerValue, protocol)
        test_empty_value_type(PositiveIntegerValue, protocol)
        test_empty_value_type(StringValue, protocol)
        test_empty_value_type(LongStringValue, protocol)
        test_empty_value_type(MultipleStringValue, protocol)
        test_empty_value_type(LongMultipleStringValue, protocol)
        test_empty_value_type(ModuleValue, protocol)
        test_empty_value_type(PasswordValue, protocol)
        # verify completness of the test
        classes_to_test = set(getattr(livesettings.values, k) for k in livesettings.values.__all__ if \
                              not k in ('BASE_GROUP', 'ConfigurationGroup', 'Value', 'SortedDotDict', 'PercentValue'))
        #self.assertEqual(protocol, classes_to_test,
                         #msg='The tested classes have been not all exactly the same as expected')

    def test_csrf(self):
        "test CSRF"
        from django.test import Client
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.login(username='admin', password='secret')
        response = csrf_client.get('/settings/')
        csrfmiddlewaretoken = str(response.context['csrf_token']) + ''
        self.assertContains(response, csrfmiddlewaretoken, msg_prefix='has not csrf')
        # expect OK
        response = csrf_client.post('/settings/',
                                    {'Group2__SingleItem': '1234', 'csrfmiddlewaretoken': csrfmiddlewaretoken})
        self.assertRedirects(response, expected_url='/settings/')
        # expect 403
        response = csrf_client.post('/settings/', {'Group2__SingleItem': '1234'})
        self.assertContains(response, 'CSRF', status_code=403, msg_prefix='should require csrf')
