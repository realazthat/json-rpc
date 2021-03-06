""" Test Django Backend."""
from __future__ import absolute_import
import sys
import os
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest


from django.conf.urls import url
from django.core.urlresolvers import RegexURLPattern
from django.test import TestCase
from ...backend.django import api
import json


class TestDjangoBackend(TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ['DJANGO_SETTINGS_MODULE'] = 'jsonrpc.tests.test_backend_django.settings'
        # django.setup()

    def test_urls(self):
        self.assertTrue(isinstance(api.urls, list))
        for api_url in api.urls:
            self.assertTrue(isinstance(api_url, RegexURLPattern))

    def test_client(self):
        @api.dispatcher.add_method
        def dummy(request):
            return ""

        json_data = {
            "id": "0",
            "jsonrpc": "2.0",
            "method": "dummy",
        }
        response = self.client.post(
            '',
            json.dumps(json_data),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf8'))
        self.assertEqual(data['result'], '')

    def test_method_not_allowed(self):
        response = self.client.get(
            '',
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 405, "Should allow only POST")

    def test_invalid_request(self):
        response = self.client.post(
            '',
            '{',
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf8'))
        self.assertEqual(data['error']['code'], -32700)
        self.assertEqual(data['error']['message'], 'Parse error')

    def test_resource_map(self):
        response = self.client.get('/map')
        self.assertEqual(response.status_code, 200)
        data = response.content.decode('utf8')
        self.assertIn("JSON-RPC map", data)
