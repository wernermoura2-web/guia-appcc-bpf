"""Synchronize four split items in Acrobat templates and printed process sheets."""
from pathlib import Path
import json,re
import fitz
from pypdf import PdfReader,PdfWriter
from pypdf.generic import NameObject,TextStringObject,ArrayObject,FloatObject,DictionaryObject,NumberObject
from reportlab.lib.utils import simpleSplit
R=Path(__file__).resolve().parents[1];path=R/'Guia_APPCC_BPF.pdf'
cfg=json.loads((R/'config.js').read_text()[10:].strip().rstrip(';'))
counts={'4.2.7':3,'4.3.5':3,'4.7.4':4,'4.7.5':5};moves={'4.2.7':{1:1},'4.3.5':{0:0},'4.7.4':{1:3},'4.7.5':{1:4}}
reader=PdfReader(path);writer=PdfWriter();writer.clone_document_from_reader(reader);before=set(writer.get_fields())
names=writer.root_object['/Names']['/Templates']['/Names'];fields=writer.root_object['/AcroForm']['/Fields']
for code,count in counts.items():
 source=next(c for c in cfg['itens'].values()if c['code']==code);assert len(source['frases'])==count
 template='Frases_'+code.replace('.','_')+'_S';prefix='F_'+code.replace('.','_')+'_S_ed_'
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
 height={3:174,4:140,5:110}[count];gap={3:16,4:14,5:14}[count];values={}
 for i in range(count):
  bottom=724-height-i*(height+gap)
  for _,obj,m in rows[i]:
   old=rects[m[1]+m[3]];rect=[old[0],bottom+(old[1]-basebottom)*height/(basetop-basebottom),old[2],bottom+(old[3]-basebottom)*height/(basetop-basebottom)]
   obj[NameObject('/Rect')]=ArrayObject([FloatObject(x)for x in rect]);obj[NameObject('/F')]=NumberObject(4);obj[NameObject('/NM')]=TextStringObject(str(obj['/T']))
   if obj.get('/FT')not in ['/Tx','/Ch']:continue
   f=source['frases'][i];kind=m[1]
   value=('F'+str(i+1)+' - '+f['texto']+'\nOrientação: '+f['orientacao'])if kind=='text'else f['cat'].replace('PPHO','POP')if kind=='cat'else str(cfg['pesos'][f['cat']])if kind=='nc'else str(f['P'])if kind=='p'else str(cfg['pesos'][f['cat']]*f['P'])if kind=='score'else ''if kind=='obs'else 'BPF/APPCC'if kind=='label'and m[3]=='_APPCC'else str(obj.get('/V',''))
   obj.pop(NameObject('/AP'),None);obj[NameObject('/DA')]=TextStringObject('0 0 0 rg /Helv 5.5 Tf');obj[NameObject('/DV')]=TextStringObject(value);values[str(obj['/T'])]=value
 for ref in annots:
  obj=ref.get_object()
  if obj.get('/T')==prefix+'context':
   value='NC: PPR=1; POP=2; PC=3; PPRO=4; PCC=5. P: 1 a 5. BPF/APPCC informativo; resultado oficial por item.'
   obj.pop(NameObject('/AP'),None);obj[NameObject('/V')]=TextStringObject(value);obj[NameObject('/DV')]=TextStringObject(value);values[str(obj['/T'])]=value
 writer.update_page_form_field_values(page,values,auto_regenerate=False)
scripts=writer.root_object['/Names']['/JavaScript']['/Names']
for i in range(1,len(scripts),2):
 obj=scripts[i].get_object();raw=obj['/JS'].get_object();s=raw.get_data().decode()if hasattr(raw,'get_data')else str(raw)
 if 'var CFG='not in s:continue
 if 'function migrarFrasesIndividuais'not in s:
  fn="""function migrarFrasesIndividuais(){var d=dados.call(this);if(d.individualPhrasesVersion==='frases-individuais-20261101')return;var counts={'4.2.7':3,'4.3.5':3,'4.7.4':4,'4.7.5':5},moves={'4.2.7':{1:1},'4.3.5':{0:0},'4.7.4':{1:3},'4.7.5':{1:4}};d.legacyIndividualPhrases=d.legacyIndividualPhrases||{};for(var key in CFG.itens){var c=CFG.itens[key];if(!counts[c.code]||!d.u[key])continue;var old=d.u[key];if(old[counts[c.code]-1])continue;d.legacyIndividualPhrases[key]=JSON.parse(JSON.stringify(old));var next=[];for(var j=0;j<counts[c.code];j++)next[j]={c:c.frases[j].cat,a:'',o:'Revisar após individualizar requisitos; respostas anteriores preservadas no histórico.'};for(var from in moves[c.code])if(old[from])next[moves[c.code][from]]=old[from];d.u[key]=next;}d.individualPhrasesVersion='frases-individuais-20261101';gravar.call(this,d);}\n"""
  s=s.replace('function iniciar(){try{',fn+'function iniciar(){try{migrarFrasesIndividuais.call(this);')
 obj[NameObject('/JS')]=TextStringObject(s)
with path.open('wb')as f:writer.write(f)
assert before.issubset(PdfReader(path).get_fields());assert len(PdfReader(path).pages)==22
paper=json.loads((R/'paper-data.js').read_text().split('=',1)[1].strip().rstrip(';'));metadata=json.loads((R/'process-display-data.json').read_text());doc=fitz.open(path)
for idx in [1,2,3,4,5,9,10]:
 pg=doc[idx];entries=list({c['code']:c for c in cfg['itens'].values()if c['page']==idx}.values());fs=paper[idx]['fields']
 bottom=min(f['y']for f in fs if f['n'].startswith('obs_gerais'))-19;labels=[b[1]for b in pg.get_text('blocks')if 'OBSERVAÇÕES GERAIS'in b[4]]
 if labels:bottom=min(bottom,min(labels)-4)
 riskend=max(f['y']+f['h']for f in fs if f['n'].startswith(('risk_','risco_resultado_')))
 for c in entries:c['processId']=metadata[str(idx)+':'+c['code']]['processId']
 positions=[r for c in entries for label in [c['code'],c['processId']]for r in pg.search_for(label)if r.x0<61 and riskend+15<r.y0<bottom];assert positions;top=min(r.y0 for r in positions)-4
 pg.add_redact_annot(fitz.Rect(14,top,581,bottom),fill=(1,1,1));pg.apply_redactions(images=0,graphics=0)
 for size in [6.1,5.9,5.7,5.5,5.3,5.1,4.9,4.7,4.5]:
  heights=[max(18,sum(len(simpleSplit('F'+str(i+1)+' - '+f['texto'],'Helvetica',size,512))for i,f in enumerate(c['frases']))*size*1.22+5)for c in entries]
  if sum(heights)<=bottom-top:break
 assert sum(heights)<=bottom-top,(idx,top,bottom,heights)
 y=top
 for c,h in zip(entries,heights):
  pg.draw_rect((14,y,581,y+h),color=(.52,.6,.65),fill=(1,1,1),width=.4);pg.draw_rect((14,y,60,y+h),color=(.52,.6,.65),fill=(.94,.96,.97),width=.4)
  assert pg.insert_textbox((15,y+1,59,y+h-1),c['processId']+'\n('+c['code']+')',fontsize=5.5,fontname='hebo',align=1,lineheight=1.05)>=0
  text='\n'.join('F'+str(i+1)+' - '+f['texto']for i,f in enumerate(c['frases']));assert pg.insert_textbox((63,y+2,579,y+h),text,fontsize=size,fontname='helv',lineheight=1.17)>=0;y+=h
tmp=path.with_suffix('.individual.pdf');doc.save(tmp,garbage=0,deflate=True);doc.close();tmp.replace(path);doc=fitz.open(path)
for idx in [1,2,3,4,5,9,10]:doc[idx].get_pixmap(matrix=fitz.Matrix(1.6,1.6),annots=False).save(R/paper[idx]['image'])
print('Quatro itens individualizados: templates interativos e sete páginas de processo sincronizados.')
