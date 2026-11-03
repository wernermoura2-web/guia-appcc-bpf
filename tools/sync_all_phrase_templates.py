"""Synchronize four split items in Acrobat templates and printed process sheets."""
from pathlib import Path
import json,re,sys
import fitz
from pypdf import PdfReader,PdfWriter
from pypdf.generic import NameObject,TextStringObject,ArrayObject,FloatObject,DictionaryObject,NumberObject
from reportlab.lib.utils import simpleSplit
R=Path(__file__).resolve().parents[1];path=R/(sys.argv[1] if len(sys.argv)>1 else 'Guia_APPCC_BPF.pdf')
cfg=json.loads((R/'config.js').read_text()[10:].strip().rstrip(';'))
counts={'4.1.3':3,'4.5.3':3};moves={'4.2.7':{1:1},'4.3.5':{0:0},'4.7.4':{1:3},'4.7.5':{1:4}}
reader=PdfReader(path);writer=PdfWriter();writer.clone_document_from_reader(reader);before=set(writer.get_fields())
names=writer.root_object['/Names']['/Templates']['/Names'];fields=writer.root_object['/AcroForm']['/Fields']
for code,count in counts.items():
 source=next(c for c in cfg['itens'].values()if c['code']==code);assert len(source['frases'])==count
 template=source['template'];prefix=source['editorPrefix']+'ed_'
 page=next(names[i+1].get_object()for i in range(0,len(names),2)if names[i]==template)
 pattern=re.compile(re.escape(prefix)+r'(panel|text|label|cat|nc|p|score|b|obs)_(\d+)(.*)$');annots=page['/Annots'];rows={i:[]for i in range(count)}
 for ref in annots:
  obj=ref.get_object();m=pattern.fullmatch(str(obj.get('/T','')))
  if m and int(m[2])<count:rows[int(m[2])].append((ref,obj,m))
 for i in range(count):
  if rows[i]:continue
  for _,obj,m in rows[1]:
   new=DictionaryObject({k:v for k,v in obj.items()if k not in ['/P','/Parent']});new[NameObject('/T')]=TextStringObject(prefix+m[1]+'_'+str(i)+m[3])
   if obj.get('/A'):
    raw=obj['/A'].get('/JS');raw=raw.get_object()if hasattr(raw,'get_object')else raw;js=raw.get_data().decode()if hasattr(raw,'get_data')else str(raw)
    new[NameObject('/A')]=DictionaryObject({NameObject('/S'):NameObject('/JavaScript'),NameObject('/JS'):TextStringObject(js.replace('this,1,','this,'+str(i)+','))})
   ref=writer._add_object(new);annots.append(ref);fields.append(ref);rows[i].append((ref,new,pattern.fullmatch(str(new['/T']))))
 rects={m[1]+m[3]:list(map(float,obj['/Rect']))for _,obj,m in rows[1]};basebottom=rects['panel'][1];basetop=rects['panel'][3]
 height={2:230,3:174,4:140,5:110,6:92}[count];gap=14;values={}
 for i in range(count):
  bottom=724-height-i*(height+gap)
  for _,obj,m in rows[i]:
   old=rects[m[1]+m[3]];rect=[old[0],bottom+(old[1]-basebottom)*height/(basetop-basebottom),old[2],bottom+(old[3]-basebottom)*height/(basetop-basebottom)]
   obj[NameObject('/Rect')]=ArrayObject([FloatObject(x)for x in rect]);obj[NameObject('/F')]=NumberObject(4);obj[NameObject('/NM')]=TextStringObject(str(obj['/T']))
   if obj.get('/FT')not in ['/Tx','/Ch']:continue
   f=source['frases'][i];kind=m[1]
   if kind in ['text','obs']:obj[NameObject('/Ff')]=NumberObject(int(obj.get('/Ff',0))|4096)
   value=('F'+str(i+1)+' - '+f['texto']+'\nOrientação: '+f['orientacao'])if kind=='text'else f['cat'].replace('PPHO','POP')if kind=='cat'else str(cfg['pesos'][f['cat']])if kind=='nc'else str(f['P'])if kind=='p'else str(cfg['pesos'][f['cat']]*f['P'])if kind=='score'else ''if kind=='obs'else 'BPF/APPCC'if kind=='label'and m[3]=='_APPCC'else str(obj.get('/V',''))
   if kind=='text':value='\n'.join(line for paragraph in value.split('\n') for line in simpleSplit(paragraph,'Helvetica',6,528))
   obj.pop(NameObject('/AP'),None);obj[NameObject('/DA')]=TextStringObject('0 0 0 rg /Helv 6 Tf');obj[NameObject('/DV')]=TextStringObject(value);values[str(obj['/T'])]=value
 for ref in annots:
  obj=ref.get_object()
  if obj.get('/T')==prefix+'context':
   value='NC: PPR=1; POP=2; PC=3; PPRO=4; PCC=5. P: 1 a 5. BPF/APPCC informativo; resultado oficial por item.'
   obj.pop(NameObject('/AP'),None);obj[NameObject('/V')]=TextStringObject(value);obj[NameObject('/DV')]=TextStringObject(value);values[str(obj['/T'])]=value
 writer.update_page_form_field_values(page,values,auto_regenerate=False)

with path.open('wb') as f: writer.write(f)
result=PdfReader(path); ns=result.trailer['/Root']['/Names']['/Templates']['/Names']
for code,count in counts.items():
 c=next(c for c in cfg['itens'].values() if c['code']==code)
 page=next(ns[i+1].get_object() for i in range(0,len(ns),2) if ns[i]==c['template'])
 fs={str(a.get_object().get('/T','')):a.get_object() for a in page['/Annots']}
 for i in range(count):
  for suffix in ['text','cat','obs','b']:
   keys=[c['editorPrefix']+'ed_'+suffix+'_'+str(i)+end for end in ((['_S','_N','_A'] if c.get('allowNA') else ['_S','_N']) if suffix=='b' else [''])]
   for key in keys: assert key in fs and not int(fs[key].get('/F',0))&2,(code,key)
  assert ' '.join(c['frases'][i]['texto'].split()) in ' '.join(fs[c['editorPrefix']+'ed_text_'+str(i)]['/V'].split())
print('CAP03 e estágio 4.5.3: todas as frases atualizadas e visíveis.')

# Audit every current template, including the dense 17-phrase CQ03 editor.
for c in cfg['itens'].values():
 if len(c['frases'])<2: continue
 page=next(ns[i+1].get_object() for i in range(0,len(ns),2) if ns[i]==c['template'])
 fs={str(a.get_object().get('/T','')):a.get_object() for a in page['/Annots']}
 for i in range(len(c['frases'])):
  for suffix in ['text','cat','obs','b']:
   for end in (['_S','_N'] if suffix=='b' else ['']):
    key=c['editorPrefix']+'ed_'+suffix+'_'+str(i)+end
    assert key in fs and not int(fs[key].get('/F',0))&2,(c['code'],key)
print('Auditoria completa: campos e respostas visíveis para todas as frases atuais.')
