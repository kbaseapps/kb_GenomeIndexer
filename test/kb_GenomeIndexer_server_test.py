# -*- coding: utf-8 -*-
import os
import unittest
from configparser import ConfigParser

from kb_GenomeIndexer.kb_GenomeIndexerImpl import kb_GenomeIndexer
from kb_GenomeIndexer.kb_GenomeIndexerServer import MethodContext

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

        user_id = 'blah'
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
    def read_mock(cls, filename):
        with open(os.path.join(cls.mock_dir, filename)) as f:
            obj = json.loads(f.read())
        return obj

    def _validate(self, sfile, data):
        with open(self.test_dir + '/../' + sfile) as f:
            d = f.read()

        schema = json.loads(d)
        for key in schema['schema'].keys():
            self.assertIn(key, data)

    def _validate_features(self, sfile, data, plist):
        with open(self.test_dir + '/../' + sfile) as f:
            d = f.read()
        feature = data['features'][0]
        parent = data['parent']

        schema = json.loads(d)
        for key in schema['schema'].keys():
            if key in plist:
                self.assertIn(key, parent)
            else:
                self.assertIn(key, feature)

    # NOTE: According to Python unittest naming rules test method names should start from 'test'. # noqa
    def test_indexers(self):
        impl = self.serviceImpl
        params = {'upa': '1/2/3'}
        plist = [
            'genome_domain',
            'genome_taxonomy',
            'genome_scientific_name',
            'assembly_guid'
        ]
        impl.indexer.ws.get_objects2 = Mock()

        impl.indexer.ws.get_objects2.return_value = self.genomeobj
        ret = impl.genome_index(self.ctx, params)
        self.assertIsNotNone(ret[0])
        self._validate('genome_schema.json', ret[0]['data'])

        ret = impl.genomefeature_index(self.ctx, params)
        self.assertIsNotNone(ret[0])
        self._validate_features('genomefeature_schema.json', ret[0], plist)

        ret = impl.genomenoncodingfeatures_index(self.ctx, params)
        self.assertIsNotNone(ret[0])
        sfile = 'genomenoncodingfeature_schema.json'
        self._validate_features(sfile, ret[0], plist)

        g2obj = self.read_mock('genome2_object.json')
        impl.indexer.ws.get_objects2.return_value = g2obj
        ret = impl.genome_index(self.ctx, params)
        self.assertIsNotNone(ret[0])
        self._validate('genome_schema.json', ret[0]['data'])

        ret = impl.genomefeature_index(self.ctx, params)
        self.assertIsNotNone(ret[0])
        self._validate_features('genomefeature_schema.json', ret[0], plist)
        feature = ret[0]['features'][6069]
        self.assertIn('SSO:000003112', feature['ontology_terms'])
        self.assertIn('SSO:000005103', feature['ontology_terms'])

        ret = impl.genomenoncodingfeatures_index(self.ctx, params)
        self.assertIsNotNone(ret[0])
        sfile = 'genomenoncodingfeature_schema.json'
        self._validate_features(sfile, ret[0], plist)

    def test_mapping(self):
        ret = self.serviceImpl.genome_mapping(self.ctx, {})
        self.assertIsNotNone(ret[0])
        ret = self.serviceImpl.genomefeature_mapping(self.ctx, {})
        self.assertIsNotNone(ret[0])
        ret = self.serviceImpl.genomenoncodingfeatures_mapping(self.ctx, {})
        self.assertIsNotNone(ret[0])
