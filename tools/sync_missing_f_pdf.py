"""Ensure newly expanded items have live F buttons in HTML and native PDF."""
from pathlib import Path
import json
from pypdf import PdfReader,PdfWriter
from pypdf.generic import NameObject,TextStringObject,DictionaryObject,ArrayObject,FloatObject,NumberObject
from inspector_guidance import appearance
R=Path(__file__).resolve().parents[1];p=R/'Guia_APPCC_BPF.pdf';cfg=json.loads((R/'config.js').read_text()[10:].strip().rstrip(';'));paper=json.loads((R/'paper-data.js').read_text().split('=',1)[1].strip().rstrip(';'))
w=PdfWriter();w.clone_document_from_reader(PdfReader(p));form=w.root_object['/AcroForm']['/Fields'];added=[]
for idx,page in enumerate(w.pages):
 annots=page.get('/Annots',ArrayObject());byname={str(ref.get_object().get('/T','')):ref.get_object()for ref in annots}
 for key,c in cfg['itens'].items():
  if c['page']!=idx or len(c['frases'])<2:continue
  name='b_'+key+'_F'
  if name in byname:continue
  assert c.get('template') and c.get('editorPrefix'),key
  fields=[f for f in paper[idx]['fields']if f['n']in ['b_'+key+'_S','b_'+key+'_N']];assert len(fields)==2
  left=fields[0]['x'];top=max(f['y']+f['h']for f in fields)+1;h=fields[0]['h'];width=fields[0]['w']
  rect=[left,float(page.mediabox.height)-top-h,left+width,float(page.mediabox.height)-top]
  obj=DictionaryObject({NameObject('/Type'):NameObject('/Annot'),NameObject('/Subtype'):NameObject('/Widget'),NameObject('/FT'):NameObject('/Btn'),NameObject('/Ff'):NumberObject(65536),NameObject('/F'):NumberObject(4),NameObject('/T'):TextStringObject(name),NameObject('/TU'):TextStringObject('Abrir frases e orientações do item '+c['code']),NameObject('/Rect'):ArrayObject([FloatObject(v)for v in rect]),NameObject('/P'):page.indirect_reference,NameObject('/A'):DictionaryObject({NameObject('/S'):NameObject('/JavaScript'),NameObject('/JS'):TextStringObject('abrirFrases.call(this,'+json.dumps(key)+');')})})
  appearance(w,obj,'F',True,font_size=6);ref=w._add_object(obj);annots.append(ref);form.append(ref)
  for f in fields:
   old=byname[f['n']];old[NameObject('/Ff')]=NumberObject(int(old.get('/Ff',0))|1);old.pop(NameObject('/A'),None);old.pop(NameObject('/AA'),None)
  if not any(f['n']==name for f in paper[idx]['fields']):paper[idx]['fields'].append(dict(n=name,type='/Btn',x=left,y=top,w=width,h=h,ro=False,multi=False,push=True,v='',options=[],label='F',font=6))
  added.append(key)
 page[NameObject('/Annots')]=annots
with p.open('wb')as f:w.write(f)
(R/'paper-data.js').write_text('const PAPER='+json.dumps(paper,ensure_ascii=False,separators=(',',':'))+';\n')
fields=PdfReader(p).get_fields();assert all('b_'+key+'_F'in fields for key,c in cfg['itens'].items()if len(c['frases'])>1)
print('F nativo e HTML incluído nos itens expandidos:',len(added))
