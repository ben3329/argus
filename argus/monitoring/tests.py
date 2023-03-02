from django.test import TestCase
from .models import *
from django.contrib.auth import get_user_model
from .engine import assets, secrets, ssh

# Create your tests here.


class AssetsTest(TestCase):
    def setUp(self):
        User = get_user_model()
        User.objects.create_superuser(
            'admin', 'admin@myproject.com', 'password')
        self.super_user = User.objects.get(username='admin')
        User.objects.create_user(
            'test', 'test@myproject.com', 'password')
        self.normal_user = User.objects.get(username='test')
        Asset.objects.all().delete()

    def tearDown(self):
        Asset.objects.all().delete()

    def test_register_asset(self):
        assets_mgr = assets.AssetsManager(self.super_user)
        rc = assets_mgr.register_asset(name='test_server', access_type='ssh')
        self.assertIs(rc, True)
        asset = Asset.objects.filter(
            user=self.super_user, name='test_server', access_type='ssh').first()
        self.assertIsNotNone(asset)

    def test_get_assets_list_super_user(self):
        assets_mgr = assets.AssetsManager(self.super_user)
        rc = assets_mgr.register_asset(name='test_server', access_type='ssh')
        self.assertIs(rc, True)
        assets_list = assets_mgr.get_assets_list()
        self.assertEqual(len(assets_list.data), 1)
        assets_mgr_normal = assets.AssetsManager(self.normal_user)
        assets_list = assets_mgr_normal.get_assets_list()
        self.assertEqual(len(assets_list.data), 0)

    def test_get_assets_list_normal_user(self):
        assets_mgr = assets.AssetsManager(self.normal_user)
        rc = assets_mgr.register_asset(name='test_server', access_type='ssh')
        self.assertIs(rc, True)
        assets_list = assets_mgr.get_assets_list()
        self.assertEqual(len(assets_list.data), 1)
        assets_mgr_normal = assets.AssetsManager(self.super_user)
        assets_list = assets_mgr_normal.get_assets_list()
        self.assertEqual(len(assets_list.data), 1)

    def test_delete_asset(self):
        assets_mgr = assets.AssetsManager(self.super_user)
        rc = assets_mgr.register_asset(name='test_server', access_type='ssh')
        self.assertIs(rc, True)
        assets_list = assets_mgr.get_assets_list()
        self.assertEqual(len(assets_list.data), 1)
        rc = assets_mgr.delete_asset(user=self.super_user, name='test_server')
        self.assertIs(rc, True)
        assets_list = assets_mgr.get_assets_list()
        self.assertEqual(len(assets_list.data), 0)

    def test_delete_other_user_asset(self):
        assets_mgr = assets.AssetsManager(self.super_user)
        rc = assets_mgr.register_asset(name='test_server', access_type='ssh')
        self.assertIs(rc, True)
        assets_list = assets_mgr.get_assets_list()
        self.assertEqual(len(assets_list.data), 1)
        assets_mgr_normal = assets.AssetsManager(self.normal_user)
        rc = assets_mgr_normal.delete_asset(
            user=self.super_user, name='test_server')
        self.assertIs(rc, False)
        assets_list = assets_mgr.get_assets_list()
        self.assertEqual(len(assets_list.data), 1)

    def test_delete_other_user_asset_by_super_user(self):
        assets_mgr = assets.AssetsManager(self.normal_user)
        rc = assets_mgr.register_asset(name='test_server', access_type='ssh')
        self.assertIs(rc, True)
        assets_list = assets_mgr.get_assets_list()
        self.assertEqual(len(assets_list.data), 1)
        assets_mgr_super = assets.AssetsManager(self.super_user)
        assets_list = assets_mgr_super.get_assets_list()
        rc = assets_mgr_super.delete_asset(
            user=self.normal_user, name='test_server')
        self.assertIs(rc, True)
        assets_list = assets_mgr.get_assets_list()
        self.assertEqual(len(assets_list.data), 0)


class SecretTest(TestCase):
    def setUp(self):
        User = get_user_model()
        User.objects.create_user(
            'test', 'test@myproject.com', 'password')
        self.user = User.objects.get(username='test')
        with open('/root/.ssh/id_rsa', 'r') as f:
            self.secret = f.read()
        self.secret_mgr = secrets.SecretsManager(self.user)

    def tearDown(self):
        Asset.objects.all().delete()

    def test_create_secret(self):
        rc = self.secret_mgr.create_secret(
            name='test', access_type='ssh', secret=self.secret)
        self.assertIs(rc, True)
        secret = Secret.objects.filter(
            user=self.user, name='test', access_type='ssh', secret=self.secret).first()
        self.assertIsNotNone(secret)

    def test_get_secret(self):
        rc = self.secret_mgr.create_secret(
            name='test', access_type='ssh', secret=self.secret)
        self.assertIs(rc, True)
        secret = self.secret_mgr.get_secret(name='test')
        self.assertIsNotNone(secret)

    def test_delete_secret(self):
        rc = self.secret_mgr.create_secret(
            name='test', access_type='ssh', secret=self.secret)
        self.assertIs(rc, True)
        secret = self.secret_mgr.get_secret(name='test')
        self.assertIsNotNone(secret)
        rc = self.secret_mgr.delete_secret(name='test')
        self.assertIs(rc, True)
        secret = self.secret_mgr.get_secret(name='test')
        self.assertIsNone(secret)


class SSHTest(TestCase):
    def setUp(self):
        User = get_user_model()
        User.objects.create_user(
            'test', 'test@myproject.com', 'password')
        self.user = User.objects.get(username='test')
        assets_mgr = assets.AssetsManager(self.user)
        assets_mgr.register_asset(name='test_server', access_type='ssh')
        self.ip = '172.30.0.3'
        self.port = 22
        self.user_id = 'root'
        self.password = 'admin_password'

    def tearDown(self):
        Asset.objects.all().delete()
