from django.test import TestCase, Client
from django.urls import reverse
from dashboard.models import Estacao, Parametro, SessionData, SessionDataUnits
import json
import os


class TestViews(TestCase):
    fixtures = ["data.json"]

    def setUp(self):
        self.client = Client()
        self.index_url = reverse('index')
        self.map_url = reverse('mapData')

    def test_map_GET(self):

        response = self.client.get(self.map_url)
        self.assertEquals(response.status_code, 200)

        result = json.loads(response.content)
        self.assertEquals(result['features'][0]['properties']['codigo'], '02G/01U')

    def test_index_GET(self):

        response = self.client.get(self.index_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

    def test_index_POST(self):

        response = self.client.post(self.index_url, {
            'stat_id': 5526,
            'param_id': 13,
        })
        self.assertEquals(response.status_code, 200)

    def test_index_POST_nodata(self):

        response = self.client.post(self.index_url)
        self.assertEquals(response.status_code, 200)
