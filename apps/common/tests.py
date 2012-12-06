import random
from string import letters

from django import test
from django.conf import settings
from django.contrib.auth.models import User

import test_utils
import elasticutils.contrib.django.estestcase as estestcase

from elasticutils.contrib.django import get_es

from apps.users.cron import index_all_profiles


class TestCase(test_utils.TestCase):
    """Tests for common package."""

    @classmethod
    def setUpClass(cls):
        super(TestCase, cls).setUpClass()
        cls._AUTHENTICATION_BACKENDS = settings.AUTHENTICATION_BACKENDS
        settings.AUTHENTICATION_BACKENDS = ['common.backends.TestBackend']

        # Create a Mozillian
        cls.mozillian = User.objects.create(
                email='u000001@mozillians.org', username='7f3a67u000001')
        profile = cls.mozillian.get_profile()
        profile.is_vouched = True
        profile.full_name='Amandeep McIlrath'
        profile.save()

        # Create a non-vouched account
        cls.pending = User.objects.create(
                email='pending@mozillians.org', username='pending')
        pending_profile = cls.pending.get_profile()
        pending_profile.full_name='Amanda Younger'
        pending_profile.save()

    def setUp(self):
        # TODO: can this be more elegant?
        self.client.get('/')
        self.mozillian_client = test.Client()
        self.mozillian_client.login(email=self.mozillian.email)
        self.pending_client = test.Client()
        self.pending_client.login(email=self.pending.email)

    @classmethod
    def tearDownClass(cls):
        super(TestCase, cls).tearDownClass()
        settings.AUTHENTICATION_BACKENDS = cls._AUTHENTICATION_BACKENDS
        User.objects.all().delete()


class ESTestCase(TestCase, estestcase.ESTestCase):

    @classmethod
    def setUpClass(cls):
        """Runs the :class:`TestCase` setup to add some data.

        Also re-creates indexes respecting data mappings, flushes and
        refreshes the data so it's searchable via computer.

        """
        estestcase.ESTestCase.setUpClass()
        TestCase.setUpClass()
        es = get_es()

        # Add on demand more models here.
        index_all_profiles()

        es.flush(refresh=True)

    @classmethod
    def tearDownClass(cls):
        TestCase.tearDownClass()
        estestcase.ESTestCase.tearDownClass()


def user(**kwargs):
    """Return a user with all necessary defaults filled in.

    Default password is 'testpass' unless you say otherwise in a
    kwarg.

    """
    save = kwargs.pop('save', True)
    is_vouched = kwargs.pop('is_vouched', None)
    vouched_by = kwargs.pop('vouched_by', None)
    defaults = {}
    if 'username' not in kwargs:
        defaults['username'] = ''.join(random.choice(letters)
                                       for x in xrange(15))
    if 'email' not in kwargs:
        defaults['email'] = ''.join(
            random.choice(letters) for x in xrange(10)) + '@example.com'
    defaults.update(kwargs)
    u = User(**defaults)
    u.set_password(kwargs.get('password', 'testpass'))
    if save:
        u.save()
        profile = u.get_profile()
        if is_vouched is not None:
            profile.is_vouched = is_vouched
        if vouched_by is not None:
            profile.vouched_by = vouched_by
        profile.save()
    return u
