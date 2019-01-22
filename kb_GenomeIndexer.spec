/*
A KBase module: kb_GenomeIndexer
*/

module kb_GenomeIndexer {
    typedef structure {
        string file_name;
        UnspecifiedObject index;
    } Results;

    funcdef genome_index(mapping<string,UnspecifiedObject> params) returns (Results output) authentication required;

    funcdef genomefeature_index(mapping<string,UnspecifiedObject> params) returns (Results output) authentication required;

    funcdef genomenoncodingfeatures_index(mapping<string,UnspecifiedObject> params) returns (Results output) authentication required;

};
