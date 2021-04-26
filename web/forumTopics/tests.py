from django.test import TestCase
from .utils import generate_topics_pdf
# Create your tests here.

class UtilsTestCase(TestCase):

    def test_pdf(self):
        generate_topics_pdf()
