# -*- coding: utf-8 -*-
import json  # noqa: F401
import os  # noqa: F401
import time
import unittest
from configparser import ConfigParser  # py3
from os import environ
from unittest.mock import patch

from Utils.GenomeIndexer import GenomeIndexer
from installed_clients.WorkspaceClient import Workspace as workspaceService


class GenomeIndexerTester(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.token = environ.get('KB_AUTH_TOKEN', None)
        config_file = environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('kb_GenomeIndexer'):
            cls.cfg[nameval[0]] = nameval[1]
        # Getting username from Auth profile for token
        # authServiceUrl = cls.cfg['auth-service-url']
        # auth_client = _KBaseAuth(authServiceUrl)
        # user_id = auth_client.get_user(cls.token)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.wsURL = cls.cfg['workspace-url']
        cls.wsClient = workspaceService(cls.wsURL)
        cls.scratch = cls.cfg['scratch']
        cls.cfg['token'] = cls.token
        cls.upa = '1/2/3'
        cls.upa2 = '15792/2/12'
        cls.test_dir = os.path.dirname(os.path.abspath(__file__))
        cls.mock_dir = os.path.join(cls.test_dir, 'mock_data')

        cls.wsinfo = cls.read_mock('get_workspace_info.json')
        cls.genobj = cls.read_mock('genome_object.json')

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')

    @classmethod
    def read_mock(cls, filename):
        with open(os.path.join(cls.mock_dir, filename)) as f:
            obj = json.loads(f.read())
        return obj

    def getWsClient(self):
        return self.__class__.wsClient

    def getWsName(self):
        if hasattr(self.__class__, 'wsName'):
            return self.__class__.wsName
        suffix = int(time.time() * 1000)
        wsName = "test_GenomeIndexer_" + str(suffix)
        ret = self.getWsClient().create_workspace({'workspace': wsName})  # noqa
        self.__class__.wsName = wsName
        return wsName

    @patch('Utils.GenomeIndexer.WorkspaceAdminUtils', autospec=True)
    def index_object_test(self, mock_wsa):
        iu = GenomeIndexer(self.cfg)
        iu.ws.get_objects2.return_value = self.genobj
        res = iu.index(self.upa)
        self.assertIsNotNone(res)
        self.assertIn('data', res)
        res = iu.index_features(self.upa)
        self.assertIsNotNone(res)
        self.assertIn('documents', res)
        self.assertIn('guid', res['documents'][0])
        self.assertIn('objdata', res['documents'][0])
        self.assertIn('location', res['documents'][0]['objdata'])

        res = iu.index_non_coding_features(self.upa)
        self.assertIsNotNone(res)
        self.assertIn('documents', res)
        self.assertIn('guid', res['documents'][0])

    def index_ws_object_xtest(self):
        iu = GenomeIndexer(self.cfg)
        res = iu.index(self.upa2)
        self.assertIsNotNone(res)
        self.assertIn('data', res)
        res = iu.index_features(self.upa2)
        self.assertIsNotNone(res)
        self.assertIn('documents', res)
        self.assertIn('guid', res['documents'][0])
