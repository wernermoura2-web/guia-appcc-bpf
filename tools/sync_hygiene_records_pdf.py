"""Synchronize hygiene records, three-row Acrobat template and saved data."""
from pathlib import Path
import json,re
import fitz
from pypdf import PdfReader,PdfWriter
from pypdf.generic import NameObject,TextStringObject,ArrayObject,FloatObject,DictionaryObject,NumberObject
from reportlab.lib.utils import simpleSplit
R=Path(__file__).resolve().parents[1];path=R/'Guia_APPCC_BPF.pdf'
cfg=json.loads((R/'config.js').read_text()[10:].strip().rstrip(';'))
source=next(c for c in cfg['itens'].values()if c['code']=='4.6.11');assert len(source['frases'])==2
reader=PdfReader(path);writer=PdfWriter();writer.clone_document_from_reader(reader)
before=set(writer.get_fields());names=writer.root_object['/Names']['/Templates']['/Names']
page=next(names[i+1].get_object()for i in range(0,len(names),2)if names[i]=='Frases_4_6_11_S')
prefix='F_4_6_11_S_ed_';pattern=re.compile(re.escape(prefix)+r'(panel|text|label|cat|nc|p|score|b|obs)_(\d+)(.*)$')
fields=writer.root_object['/AcroForm']['/Fields'];annots=page['/Annots']
rows={i:[]for i in range(3)}
for ref in annots:
 obj=ref.get_object();m=pattern.fullmatch(str(obj.get('/T','')))
 if m:rows[int(m[2])].append((ref,obj,m))
# The existing template has five slots. Clone the fifth slot once for F6.
if not rows[2]:
 for ref,obj,m in rows[1]:
  new=DictionaryObject({k:v for k,v in obj.items()if k not in ['/P','/Parent']});new[NameObject('/T')]=TextStringObject(prefix+m[1]+'_2'+m[3])
  if obj.get('/A'):
   action=obj['/A'].get_object();raw=action.get('/JS');js=raw.get_object()if hasattr(raw,'get_object')else raw
   js=js.get_data().decode()if hasattr(js,'get_data')else str(js)
   new[NameObject('/A')]=DictionaryObject({NameObject('/S'):NameObject('/JavaScript'),NameObject('/JS'):TextStringObject(js.replace('this,1,','this,2,'))})
  ref=writer._add_object(new);annots.append(ref);fields.append(ref)
  rows[2].append((ref,new,pattern.fullmatch(str(new['/T']))))
# Use identical geometry for every slot; keep the header and action buttons.
rects={m[1]+m[3]:list(map(float,obj['/Rect']))for _,obj,m in rows[1]}
basebottom=rects['panel'][1];basetop=rects['panel'][3]
values={}
for i in range(3):
 bottom=550-i*190
 for ref,obj,m in rows[i]:
  if i>=len(source['frases']):
   obj[NameObject('/F')]=NumberObject(2);continue
  old=rects[m[1]+m[3]];rect=[old[0],bottom+(old[1]-basebottom)*174/(basetop-basebottom),old[2],bottom+(old[3]-basebottom)*174/(basetop-basebottom)]
  obj[NameObject('/Rect')]=ArrayObject([FloatObject(v)for v in rect])
  obj[NameObject('/F')]=NumberObject(4)
  obj[NameObject('/NM')]=TextStringObject(str(obj['/T']))
  if obj.get('/FT') in ['/Tx','/Ch']:
   if m[1]=='text':value='F'+str(i+1)+' - '+source['frases'][i]['texto']+'\nOrientação: '+source['frases'][i]['orientacao']
   elif m[1]=='cat':value=source['frases'][i]['cat'].replace('PPHO','POP')
   elif m[1]=='nc':value=str(cfg['pesos'][source['frases'][i]['cat']])
   elif m[1]=='p':value=str(source['frases'][i]['P'])
   elif m[1]=='score':value=str(cfg['pesos'][source['frases'][i]['cat']]*source['frases'][i]['P'])
   elif m[1]=='obs':value=''
   elif m[1]=='label' and m[3]=='_APPCC':value='BPF/APPCC'
   else:value=str(obj.get('/V',''))
   obj.pop(NameObject('/AP'),None)
   obj[NameObject('/DA')]=TextStringObject('0 0 0 rg /Helv 5.5 Tf');obj[NameObject('/DV')]=TextStringObject(value);values[str(obj['/T'])]=value
for ref in annots:
 obj=ref.get_object()
 if obj.get('/T')==prefix+'context':
  value='NC: PPR=1; POP=2; PC=3; PPRO=4; PCC=5. P: 1 a 5. BPF/APPCC informativo; o resultado oficial permanece por item.'
  obj.pop(NameObject('/AP'),None);obj[NameObject('/V')]=TextStringObject(value);obj[NameObject('/DV')]=TextStringObject(value);values[str(obj['/T'])]=value
writer.update_page_form_field_values(page,values,auto_regenerate=False)
scripts=writer.root_object['/Names']['/JavaScript']['/Names']
for i in range(1,len(scripts),2):
 obj=scripts[i].get_object();raw=obj['/JS'].get_object();s=raw.get_data().decode()if hasattr(raw,'get_data')else str(raw)
 if 'var CFG='not in s:continue
 if 'function migrarRegistrosEmbalagens'not in s:
  fn="""function migrarRegistrosEmbalagens(){var d=dados.call(this);if(d.hygieneRecordsVersion==='higienizacao-registros-f2-20261101')return;d.legacyHygieneRecords=d.legacyHygieneRecords||{};for(var key in CFG.itens){if(CFG.itens[key].code!=='4.6.11'||!d.u[key])continue;var old=d.u[key];if(old[2])continue;d.legacyHygieneRecords[key]=JSON.parse(JSON.stringify(old));var next=[];next[0]=old[0]||{};next[1]={c:'PPR',a:'',o:'Confirmar registros de higienização na nova F2.'};next[2]=old[1]||{};d.u[key]=next;}d.hygieneRecordsVersion='higienizacao-registros-f2-20261101';gravar.call(this,d);}
"""
  s=s.replace('function iniciar(){try{',fn+'function iniciar(){try{migrarRegistrosEmbalagens.call(this);')
 obj[NameObject('/JS')]=TextStringObject(s)
with path.open('wb')as f:writer.write(f)
check=PdfReader(path);assert before.issubset(check.get_fields());assert prefix+'b_2_S'in check.get_fields();assert len(check.pages)==22
# Rewrite the description block on all four reservoir sheets, preserving fields.
paper=json.loads((R/'paper-data.js').read_text().split('=',1)[1].strip().rstrip(';'))
doc=fitz.open(path)
for idx in [7,8]:
 pg=doc[idx];entries=list({c['code']:c for c in cfg['itens'].values()if c['page']==idx}.values())
 fs=paper[idx]['fields'];bottom=min(f['y']for f in fs if f['n'].startswith('obs_gerais'))-19
 riskend=max(f['y']+f['h']for f in fs if f['n'].startswith(('risk_','risco_resultado_')))
 labels=[b[1] for b in pg.get_text('blocks') if 'OBSERVAÇÕES GERAIS' in b[4]]
 if labels:bottom=min(bottom,min(labels)-4)
 positions=[r for c in entries for label in [c['code'],c.get('processId','RES'+str(entries.index(c)+1)).zfill(0)]for r in pg.search_for(label)if r.x0<61 and riskend+15<r.y0<bottom]
 # Current display codes are also available in the metadata JSON.
 metadata=json.loads((R/'process-display-data.json').read_text())
 for c in entries:c['processId']=metadata[str(idx)+':'+c['code']]['processId']
 positions +=[r for c in entries for r in pg.search_for(c['processId'])if r.x0<61 and riskend+15<r.y0<bottom]
 assert positions;top=min(r.y0 for r in positions)-4
 assert not any(f['y']<bottom and f['y']+f['h']>top and f['x']<581 and f['x']+f['w']>14 for f in fs)
 pg.add_redact_annot(fitz.Rect(14,top,581,bottom),fill=(1,1,1));pg.apply_redactions(images=0,graphics=0)
 for size in [6.1,5.9,5.7,5.5,5.3,5.1,4.9]:
  heights=[max(18 if idx==7 else 25,sum(len(simpleSplit('F'+str(i+1)+' - '+f['texto'],'Helvetica',size,512))for i,f in enumerate(c['frases']))*size*1.22+5)for c in entries]
  if sum(heights)<=bottom-top:break
 assert sum(heights)<=bottom-top,(idx,top,bottom,heights)
 y=top
 for c,h in zip(entries,heights):
  pg.draw_rect((14,y,581,y+h),color=(.52,.6,.65),fill=(1,1,1),width=.4);pg.draw_rect((14,y,60,y+h),color=(.52,.6,.65),fill=(.94,.96,.97),width=.4)
  assert pg.insert_textbox((15,y+1,59,y+h-1),c['processId']+'\n('+c['code']+')',fontsize=5.5,fontname='hebo',align=1,lineheight=1.05)>=0
  text='\n'.join('F'+str(i+1)+' - '+f['texto']for i,f in enumerate(c['frases']))
  assert pg.insert_textbox((63,y+2,579,y+h),text,fontsize=size,fontname='helv',lineheight=1.17)>=0
  y+=h
tmp=path.with_suffix('.res.pdf');doc.save(tmp,garbage=0,deflate=True);doc.close();tmp.replace(path)
doc=fitz.open(path)
for idx in [7,8]:
 assert 'F2 - As operações de limpeza'in doc[idx].get_text()
 doc[idx].get_pixmap(matrix=fitz.Matrix(1.6,1.6),annots=False).save(R/paper[idx]['image'])
print('4.6.11: F1 execução, F2 capacitação; antiga F2 de registros retirada da pontuação; retornáveis e descartáveis atualizados.')
