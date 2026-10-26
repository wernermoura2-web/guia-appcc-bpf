"""Attach display codes and references without changing assessment keys or wording."""
import json
from pathlib import Path
def apply(cfg,root):
 data=json.loads((Path(root)/'process-display-data.json').read_text())
 for c in cfg['itens'].values():
  m=data[str(c['page'])+':'+str(c['code'])];c['processId']=m['processId'];c['title']=m['title'];c['overviewRef']=m.get('overviewRef',m.get('baseRef',''))
  for f in c['frases']:
   if m.get('baseRef')and not f.get('ref'):f['ref']=m['baseRef']
 return cfg

def summary(c):
 return c['title']+' | Ref.: '+c.get('overviewRef','')
