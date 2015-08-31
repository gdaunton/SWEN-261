from django.test import TestCase
from accounts.models import Doctor, Patient
from .models import Test
from datetime import datetime

# Create your tests here.
class TestUnreleasedCase(TestCase):
    def setUp(self):
        test = Test.objects.create_test('X-Ray', 'You fractured your pelvis', None, None, None, datetime.now())

    def test_test_unreleased(self):
        test_t = Test.objects.get(name='X-Ray')
        self.assertEqual(test_t.released, False)

class TestReleasedCase(TestCase):
    def setUp(self):
        test = Test.objects.create_test('MRI', 'You\'ve been lobotomized', None, None, None, datetime.now())
        test.released = True
        test.save()

    def test_test_released(self):
        test_t = Test.objects.get(name='MRI')
        self.assertEqual(test_t.released, True)
