# -*- coding: utf-8 -*-
#BEGIN_HEADER
from Utils.GenomeIndexer import GenomeIndexer
#END_HEADER


class kb_GenomeIndexer:
    '''
    Module Name:
    kb_GenomeIndexer

    Module Description:
    A KBase module: kb_GenomeIndexer
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "0.0.1"
    GIT_URL = ""
    GIT_COMMIT_HASH = "HEAD"

    #BEGIN_CLASS_HEADER
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.shared_folder = config['scratch']
        self.wsa_token = None
        self.wsa_token = config.get('workspace-admin-token', None)
        self.indexer = GenomeIndexer(config)
        #END_CONSTRUCTOR
        pass


    def genome_index(self, ctx, params):
        """
        :param params: instance of mapping from String to unspecified object
        :returns: instance of type "Results" -> structure: parameter
           "file_name" of String, parameter "index" of unspecified object
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN genome_index
        output = self.indexer.index(params['upa'])
        #END genome_index

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method genome_index return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]

    def genome_mapping(self, ctx, params):
        """
        :param params: instance of mapping from String to unspecified object
        :returns: instance of type "Results" -> structure: parameter
           "file_name" of String, parameter "index" of unspecified object
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN genome_mapping
        output = self.indexer.mapping('genome_schema.json')
        #END genome_mapping

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method genome_mapping return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]

    def genomefeature_index(self, ctx, params):
        """
        :param params: instance of mapping from String to unspecified object
        :returns: instance of type "Results" -> structure: parameter
           "file_name" of String, parameter "index" of unspecified object
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN genomefeature_index
        output = self.indexer.index_features(params['upa'])
        #END genomefeature_index

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method genomefeature_index return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]

    def genomefeature_mapping(self, ctx, params):
        """
        :param params: instance of mapping from String to unspecified object
        :returns: instance of type "Results" -> structure: parameter
           "file_name" of String, parameter "index" of unspecified object
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN genomefeature_mapping
        output = self.indexer.mapping('genomefeature_schema.json')
        #END genomefeature_mapping

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method genomefeature_mapping return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]

    def genomenoncodingfeatures_index(self, ctx, params):
        """
        :param params: instance of mapping from String to unspecified object
        :returns: instance of type "Results" -> structure: parameter
           "file_name" of String, parameter "index" of unspecified object
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN genomenoncodingfeatures_index
        output = self.indexer.index_non_coding_features(params['upa'])
        #END genomenoncodingfeatures_index

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method genomenoncodingfeatures_index return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]

    def genomenoncodingfeatures_mapping(self, ctx, params):
        """
        :param params: instance of mapping from String to unspecified object
        :returns: instance of type "Results" -> structure: parameter
           "file_name" of String, parameter "index" of unspecified object
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN genomenoncodingfeatures_mapping
        output = self.indexer.mapping('genomenoncodingfeature_schema.json')
        #END genomenoncodingfeatures_mapping

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method genomenoncodingfeatures_mapping return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]
    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
