"""Sync existing editable PDF data without rebuilding its page layout."""
import json,re
from pathlib import Path
from pypdf import PdfReader,PdfWriter
from pypdf.generic import NameObject,TextStringObject,ArrayObject
cfg=json.loads(Path('config.js').read_text().removeprefix('const CFG=').strip().removesuffix(';'))
path=Path('Guia_APPCC_BPF.pdf');reader=PdfReader(path);writer=PdfWriter();writer.clone_document_from_reader(reader)
names=writer.root_object['/Names']['/JavaScript']['/Names'];count=0
for i in range(1,len(names),2):
 obj=names[i].get_object();raw=obj['/JS'].get_object();s=raw.get_data().decode() if hasattr(raw,'get_data') else str(raw)
 if 'var CFG=' not in s:continue
 start=s.index('var CFG=')+8;old,end=json.JSONDecoder().raw_decode(s[start:])
 for key,c in old['itens'].items():
  for j,f in enumerate(c['frases']):
   src=cfg['itens'][key]['frases'][j]
   for prop in ['cat','orientacao','consideracao','fundamento','providencia']:f[prop]=src.get(prop,'')
 old['classificationRevision']=cfg['classificationRevision'];old['inspectorGuidanceVersion']=cfg['inspectorGuidanceVersion']
 s=s[:start]+json.dumps(old,ensure_ascii=True,separators=(',',':'))+s[start+end:]
 needle="+'\\nOrientação: '+c.frases[i].orientacao"
 if 'Fundamento da classificação:' not in s:
  s=s.replace(needle,"+'\\nBPF/APPCC: '+String(c.frases[i].cat).replace('PPHO','POP')+'\\nFundamento da classificação: '+(c.frases[i].fundamento||c.frases[i].consideracao||'')"+needle)
 obj[NameObject('/JS')]=TextStringObject(s);count+=1
assert count==1
# Remove the protocol/literature appendix; preserve the 22 inspection pages.
if len(writer.pages)>22:
 assert any('Protocolo' in (pg.extract_text() or '') or 'Literatura' in (pg.extract_text() or '') for pg in writer.pages[22:])
 for i in range(len(writer.pages)-1,21,-1):writer.remove_page(i)
fields=writer.get_fields();values={}
for cf in {c['classField'] for c in cfg['itens'].values()}:
 c=next(c for c in cfg['itens'].values() if c['classField']==cf);fs=c['frases'];unique=lambda xs:list(dict.fromkeys(xs))
 vals={cf:'/'.join(unique([f['cat'].replace('PPHO','POP') for f in fs])),'criticidade_'+cf:'/'.join(unique([str(cfg['pesos'][f['cat']]) for f in fs])),'pontuacao_'+cf[7:]:str(sum(cfg['pesos'][f['cat']]*f.get('P',c['P']) for f in fs))}
 values.update({k:v for k,v in vals.items() if k in fields})
for pg in writer.pages:
 for a in pg.get('/Annots',[]):
  o=a.get_object();n=str(o.get('/T',''))
  if n in values:
   o[NameObject('/DV')]=TextStringObject(values[n])
   if o.get('/FT')=='/Ch':
    opts=o.get('/Opt',ArrayObject())
    if values[n] not in [str(v) for v in opts]:opts.append(TextStringObject(values[n]));o[NameObject('/Opt')]=opts
 relevant={str(a.get_object().get('/T','')):values[str(a.get_object().get('/T',''))] for a in pg.get('/Annots',[]) if str(a.get_object().get('/T','')) in values}
 if relevant:writer.update_page_form_field_values(pg,relevant,auto_regenerate=False)
with path.open('wb') as f:writer.write(f)
result=PdfReader(path);assert len(result.pages)==22
actual=result.get_fields();assert len(actual)==len(fields)
for k,v in values.items():assert str(actual[k]['/V'])==v
print('PDF sincronizado:',len(result.pages),'páginas;',len(actual),'campos preservados.')

