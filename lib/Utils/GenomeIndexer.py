# Special Indexer for Narrative Objects
from Utils.WorkspaceAdminUtils import WorkspaceAdminUtils
import json
import os

class GenomeIndexer:
    def __init__(self, config):
        self.ws = WorkspaceAdminUtils(config)
        ldir = os.path.dirname(os.path.abspath(__file__))
        self.schema_dir = '/'.join(ldir.split('/')[0:-2])

    def _guid(self, upa):
        (wsid, objid, ver) = upa.split('/')
        return "WS:%s:%s:%s" % (wsid, objid, ver)

    def index(self, upa):
        obj = self.ws.get_objects2({'objects': [{'ref': upa}]})['data'][0]
        data = obj['data']
        rec = dict()
        for ele in ['id', 'domain', 'taxonomy', 'scientific_name', 'notes',
                    'warnings', 'source', 'source_id', 'genome_tiers',
                    'suspect', 'num_contigs']:
            rec[ele] = data.get(ele)
        rec['scientific_name_keyword'] = data['scientific_name']
        rec['feature_count'] = len(data['features'])
        rec['contig_count'] = int(data['num_contigs'])
        rec['cds_count'] = len(data.get('cdss', []))
        rec['mrna_count'] = len(data.get('mrnas', []))
        rec['non_coding_feature_count'] = len(data.get('non_coding_features', []))
        rec['feature_types'] = data.get('feature_counts', None)
        if 'assembly_ref' in data:
            rec['assembly_guid'] = 'WS:%s' % (data['assembly_ref'])
        elif 'contigset_ref' in data:
            rec['assembly_guid'] = 'WS:%s' % (data['contigset_ref'])
        return {'data': rec}

    def _parent(self, rec):
        p = {
            'genome_domain': rec['domain'],
            'genome_taxonomy': rec['taxonomy'],
            'genome_scientific_name': rec['scientific_name'],
        }
        if 'assembly_ref' in rec:
            p['assembly_guid'] = 'WS:%s' % (rec['assembly_ref'])
        elif 'contigset_ref' in rec:
            p['assembly_guid'] = 'WS:%s' % (rec['contigset_ref'])
        return p

    def index_features(self, upa):
        obj = self.ws.get_objects2({'objects': [{'ref': upa}]})['data'][0]
        data = obj['data']
        rec = {}
        if 'assembly_ref' in data:
            assembly_guid = 'WS:%s' % (data['assembly_ref'])
        elif 'contigset_ref' in data:
            assembly_guid = 'WS:%s' % (data['contigset_ref'])
        rec['parent'] = self._parent(data)
        features_rec = []
        for feature in data['features']:
            frec = {}
            frec['id'] = feature['id']
            frec['protein_translation'] = feature.get('protein_translation')
            if 'function' in feature:
                frec['function'] = feature['function']
            elif 'functions' in feature:
                frec['function'] = feature['functions']
            frec['ontology_terms'] = []
            if 'ontology_terms' in feature:
                ots = feature['ontology_terms']
                for ot in ots:
                    for ns in ots[ot]:
                        frec['ontology_terms'].append(ns)

            frec['aliases'] = feature['aliases'][0]
            frec['feature_type'] = feature['type']
            loc = feature['location'][0]
            frec['contig_id'] = loc[0]
            frec['start'] = loc[1]
            frec['strand'] = loc[2]
            frec['stop'] = loc[3]
            frec['contig_guid'] = '%s:contig/%s' % (assembly_guid, loc[0])
            frec['guid'] = '%s:%s' % (self._guid(upa), feature['id'])
            features_rec.append(frec)

        rec['features'] = features_rec
        return rec

    def index_non_coding_features(self, upa):
        obj = self.ws.get_objects2({'objects': [{'ref': upa}]})['data'][0]
        data = obj['data']
        rec = {}
        if 'assembly_ref' in data:
            assembly_guid = 'WS:%s' % (data['assembly_ref'])
        elif 'contigset_ref' in data:
            assembly_guid = 'WS:%s' % (data['contigset_ref'])
        rec['parent'] = self._parent(data)
        features_rec = []
        for feature in data.get('non_coding_features'):
            frec = {}
            frec['id'] = feature['id']
            frec['functions'] = feature.get('functions')
            #  - path: aliases/[*]
            #    full-text: true
            frec['aliases'] = feature.get('aliases', '')
            frec['feature_type'] = feature['type']
            frec['note'] = feature.get('note')
            loc = feature['location'][0]
            frec['contig_id'] = loc[0]
            frec['start'] = loc[1]
            frec['strand'] = loc[2]
            frec['stop'] = loc[3]
            frec['contig_guid'] = '%s:contig/%s' % (assembly_guid, loc[0])
            frec['guid'] = 'WS:%s:%s' % (self._guid(upa), feature['id'])
            features_rec.append(frec)

        rec['features'] = features_rec
        return rec

    def mapping(self, filename):
        with open(os.path.join(self.schema_dir, filename)) as f:
            schema = json.loads(f.read())
        return schema
