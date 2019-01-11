from Workspace.WorkspaceClient import Workspace
import json
import os
wsid = 15792



def grab(upa, file):
  if not os.path.exists(file):
    d = ws.get_objects2({'objects': [{'ref': upa}]})
    with open(file, 'w') as f:
      f.write(json.dumps(d, indent=4))



ws = Workspace('https://ci.kbase.us/services/ws')
#d = ws.get_workspace_info({'id': wsid})
#with open('get_workspace_info.json', 'w') as f:
#    f.write(json.dumps(d))
#d = ws.list_objects({'ids': [wsid]})
#with open('list_objects.json', 'w') as f:
#    f.write(json.dumps(d))

grab('15792/2', './test/mock_data/genome_object.json')

grab('38735/4/1', './test/mock_data/genome2_object.json')

grab('4/24/1', './test/mock_data/genome3_object.json')
