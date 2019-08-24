from django.contrib.auth.models import User
from django.test import TestCase

class modelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('dva',password='Littledva123')

    def test_1(self):
        from .view.life import createSaveId, checkSaveId
        pass
