# -*- coding: utf-8 -*-
import os
import time
import unittest
from configparser import ConfigParser

from kb_GenomeIndexer.kb_GenomeIndexerImpl import kb_GenomeIndexer
from kb_GenomeIndexer.kb_GenomeIndexerServer import MethodContext
from kb_GenomeIndexer.authclient import KBaseAuth as _KBaseAuth

from installed_clients.WorkspaceClient import Workspace
from unittest.mock import Mock
import json


class kb_GenomeIndexerTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = os.environ.get('KB_AUTH_TOKEN', None)
        config_file = os.environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('kb_GenomeIndexer'):
            cls.cfg[nameval[0]] = nameval[1]
        cls.cfg['workspace-admin-token'] = token

        # Getting username from Auth profile for token
        authServiceUrl = cls.cfg['auth-service-url']
        auth_client = _KBaseAuth(authServiceUrl)
        user_id = auth_client.get_user(token)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({'token': token,
                        'user_id': user_id,
                        'provenance': [
                            {'service': 'kb_GenomeIndexer',
                             'method': 'please_never_use_it_in_production',
                             'method_params': []
                             }],
                        'authenticated': 1})
        cls.wsURL = cls.cfg['workspace-url']
        cls.wsClient = Workspace(cls.wsURL)
        cls.serviceImpl = kb_GenomeIndexer(cls.cfg)
        cls.scratch = cls.cfg['scratch']
        cls.test_dir = os.path.dirname(os.path.abspath(__file__))
        cls.mock_dir = os.path.join(cls.test_dir, 'mock_data')

        cls.genomeobj = cls.read_mock('genome_object.json')

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
        wsName = "test_kb_GenomeIndexer_" + str(suffix)
        ret = self.getWsClient().create_workspace({'workspace': wsName})  # noqa
        self.__class__.wsName = wsName
        return wsName

    def getImpl(self):
        return self.__class__.serviceImpl

    def getContext(self):
        return self.__class__.ctx

    # NOTE: According to Python unittest naming rules test method names should start from 'test'. # noqa
    def test_indexers(self):
        impl = self.getImpl()
        params = {'upa': '1/2/3'}
        impl.indexer.ws.get_objects2 = Mock()

        impl.indexer.ws.get_objects2.return_value = self.genomeobj
        ret = impl.genome_index(self.getContext(), params)
        self.assertIsNotNone(ret[0])

        ret = impl.genomefeature_index(self.getContext(), params)
        self.assertIsNotNone(ret[0])

        ret = impl.genomenoncodingfeatures_index(self.getContext(), params)
        self.assertIsNotNone(ret[0])

    def test_mapping(self):
        ret = self.getImpl().genome_mapping(self.getContext(), {})
        self.assertIsNotNone(ret[0])
        ret = self.getImpl().genomefeature_mapping(self.getContext(), {})
        self.assertIsNotNone(ret[0])
        ret = self.getImpl().genomenoncodingfeatures_mapping(self.getContext(), {})
        self.assertIsNotNone(ret[0])
