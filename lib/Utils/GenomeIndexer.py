# Special Indexer for Narrative Objects
import json
import os

from Utils.WorkspaceAdminUtils import WorkspaceAdminUtils


def _guid(upa):
    (wsid, objid, ver) = upa.split('/')
    return f"WS:{wsid}:{objid}:{ver}"


def _get_assembly_guid(data):
    if 'assembly_ref' in data:
        return _guid(data['assembly_ref'])
    elif 'contigset_ref' in data:
        return _guid(data['contigset_ref'])
    
    
def _parent(rec):
    return {'genome_domain': rec['domain'],
            'genome_taxonomy': rec.get('taxonomy'),
            'genome_scientific_name': rec.get('scientific_name'),
            'assembly_guid': _get_assembly_guid(rec)}

class GenomeIndexer:
    def __init__(self, config):
        self.ws = WorkspaceAdminUtils(config)
        self.schema_dir = config['schema-dir']

    def index(self, upa):
        obj = self.ws.get_objects2({'objects': [{'ref': upa}]})['data'][0]
        data = obj['data']

        rec = {'scientific_name_keyword': data['scientific_name'],
               'feature_count': len(data['features']),
               'contig_count': int(data['num_contigs']),
               'cds_count': len(data.get('cdss', [])),
               'mrna_count': len(data.get('mrnas', [])),
               'non_coding_feature_count': len(data.get('non_coding_features', [])),
               'feature_types': data.get('feature_counts', None),
               'assembly_guid': _get_assembly_guid(data)}
        for ele in ['id', 'domain', 'taxonomy', 'scientific_name', 'notes',
                    'warnings', 'source', 'source_id', 'genome_tiers',
                    'suspect', 'num_contigs']:
            rec[ele] = data.get(ele)

        obj = {
            'assembly_ref': rec['assembly_guid'],
            'cdss': rec['cds_count'],
            'domain': rec['domain'],
            'feature_counts': rec['feature_types'],
            "features": rec['feature_count'],
            "genome_tiers": rec["genome_tiers"],
            "id": rec["id"],
            "mrnas": rec["mrna_count"],
            "non_coding_features": rec["non_coding_feature_count"],
            "notes": rec['notes'],
            "num_contigs": rec["contig_count"],
            "scientific_name": rec["scientific_name"],
            "source": rec["source"],
            "source_id": rec["source_id"],
            "taxonomy": rec["taxonomy"],
            "warnings": rec["warnings"]
        }

        rec['objdata'] = obj
        schema = self.mapping('genome_schema.json')
        return {'data': rec, 'schema': schema}

    def index_features(self, upa):
        obj = self.ws.get_objects2({'objects': [{'ref': upa}]})['data'][0]
        data = obj['data']
        rec = {}
        assembly_guid = _get_assembly_guid(data)
        rec['parent'] = _parent(data)
        features_rec = []
        for feature in data['features']:
            loc = feature['location'][0]
            frec = {'id': feature['id'],
                    'protein_translation': feature.get('protein_translation'),
                    'function': '',
                    'ontology_terms': [],
                    'aliases': feature.get('aliases', ''),
                    'feature_type': feature['type'],
                    'contig_id': loc[0],
                    'start': loc[1],
                    'strand': loc[2],
                    'stop': loc[3],
                    'contig_guid': f'{assembly_guid}:contig/{loc[0]}',
                    'guid': f'{_guid(upa)}:{feature["id"]}'}

            if 'function' in feature:
                frec['function'] = feature['function']
            elif 'functions' in feature:
                frec['function'] = feature['functions']

            if 'ontology_terms' in feature:
                ots = feature['ontology_terms']
                for ot in ots:
                    for ns in ots[ot]:
                        frec['ontology_terms'].append(ns)

            obj = {
                "aliases": [frec['aliases']],
                "functions": [frec['function']],
                "id": [frec['id']],
                "type": [frec['feature_type']],
                "location": [loc]
            }
            frec['objdata'] = obj
            features_rec.append(frec)

        rec['documents'] = features_rec
        rec['schema'] = self.mapping('genomefeature_schema.json')
        return rec

    def index_non_coding_features(self, upa):
        obj = self.ws.get_objects2({'objects': [{'ref': upa}]})['data'][0]
        data = obj['data']
        rec = {}
        assembly_guid = _get_assembly_guid(data)
        rec['parent'] = _parent(data)
        features_rec = []
        for feature in data.get('non_coding_features', []):
            loc = feature['location'][0]
            frec = {'id': feature['id'],
                    'functions': feature.get('functions'),
                    'aliases': feature.get('aliases', ''),
                    'feature_type': feature['type'],
                    'note': feature.get('note'),
                    'contig_id': loc[0],
                    'start': loc[1],
                    'strand': loc[2],
                    'stop': loc[3],
                    'contig_guid': f'{assembly_guid}:contig/{loc[0]}',
                    'guid': f'{_guid(upa)}:{feature["id"]}'}

            obj = {
                "aliases": [frec['aliases']],
                "functions": [frec['functions']],
                "id": [frec['id']],
                "type": [frec['feature_type']],
                "location": [loc]}

            frec['objdata'] = obj
            features_rec.append(frec)

        rec['documents'] = features_rec
        rec['schema'] = self.mapping('genomenoncodingfeature_schema.json')
        return rec

    def mapping(self, filename):
        with open(os.path.join(self.schema_dir, filename)) as f:
            schema = json.loads(f.read())
        return schema['schema']
