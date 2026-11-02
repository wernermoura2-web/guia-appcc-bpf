"""Create CQ02/CQ03 Acrobat editors; retain 22 inspection pages and all existing fields."""
from pathlib import Path
import re,json
import fitz
from pypdf import PdfReader,PdfWriter
from pypdf.generic import NameObject,TextStringObject,DictionaryObject,ArrayObject,NumberObject,FloatObject
from inspector_guidance import appearance
from reportlab.lib.utils import simpleSplit
R=Path(__file__).resolve().parents[1];path=R/'Guia_APPCC_BPF.pdf';cfg=json.loads((R/'config.js').read_text()[10:].strip().rstrip(';'))
r=PdfReader(path);w=PdfWriter();w.clone_document_from_reader(r);before=set(w.get_fields());templates=w.root_object['/Names']['/Templates']['/Names'];form=w.root_object['/AcroForm']['/Fields']
base=next(templates[i+1].get_object()for i in range(0,len(templates),2)if templates[i]=='Frases_4_7_5_S');baseprefix='F_4_7_5_S_ed_'
basefields={str(ref.get_object().get('/T','')).removeprefix(baseprefix):ref.get_object()for ref in base['/Annots']};pattern=re.compile(r'(panel|text|label|cat|nc|p|score|b|obs)_1(.*)$')
for code in ['4.10.2','4.10.3','4.11.2']:
 c=next(c for c in cfg['itens'].values()if c['code']==code);name=c['template'];prefix=c['editorPrefix']+'ed_';existing=next((templates[i+1].get_object()for i in range(0,len(templates),2)if templates[i]==name),None)
 page=existing or DictionaryObject({k:v for k,v in base.items()if k!='/Annots'});annots=ArrayObject();values={}
 if existing:
  oldrefs={str(ref.get_object().get('/T','')):ref for ref in page['/Annots']}
 else:oldrefs={};templates.extend([TextStringObject(name),w._add_object(page)])
 def add(key,source,rect,value=None,action=None,label=None,flags=None):
  full=prefix+key
  if full in oldrefs:ref=oldrefs[full];o=ref.get_object()
  else:
   o=DictionaryObject({k:v for k,v in source.items()if k not in ['/P','/Parent','/AA']});ref=w._add_object(o);form.append(ref)
  o[NameObject('/T')]=TextStringObject(full);o[NameObject('/NM')]=TextStringObject(full);o[NameObject('/F')]=NumberObject(4);o[NameObject('/Rect')]=ArrayObject([FloatObject(v)for v in rect])
  if flags is not None:o[NameObject('/Ff')]=NumberObject(flags)
  if action:o[NameObject('/A')]=DictionaryObject({NameObject('/S'):NameObject('/JavaScript'),NameObject('/JS'):TextStringObject(action)})
  if value is not None and o.get('/FT')in ['/Tx','/Ch']:
   o.pop(NameObject('/AP'),None);o[NameObject('/DA')]=TextStringObject('0 0 0 rg /Helv 5.2 Tf');o[NameObject('/DV')]=TextStringObject(str(value));values[full]=str(value)
  if label is not None:appearance(w,o,label,push=bool(o.get('/Ff',0)&65536),font_size=5)
  annots.append(ref);return o
 for key in ['title','context','resumo','voltar','guardar']:
  src=basefields[key];v=('Item '+code+' - AVALIAÇÃO DAS FRASES')if key=='title'else ('F1-F3: funções alternativas; ao menos uma aplicável. F4-F6: conselhos conforme atividade e atribuição legal. Justificar NA.'if code=='4.11.2'else 'BPF/APPCC informativo. Avaliar cada parâmetro e frequência; NA somente no laboratório próprio não utilizado.')if key=='context'else 'Item pendente: avaliar todas as frases aplicáveis.'if key=='resumo'else None
  add(key,src,list(map(float,src['/Rect'])),v)
 count=len(c['frases']);cols=1 if count<=3 or code=='4.11.2'else 2;rows=(count+cols-1)//cols;height=88 if code=='4.11.2'else 174 if cols==1 else 64;gap=12 if code=='4.11.2'else 16 if cols==1 else 2
 for i,f in enumerate(c['frases']):
  col=i//rows;row=i%rows;left=23+col*278;top=724-row*(height+gap);width=549 if cols==1 else 271
  if cols==1:
   model=list(map(float,basefields['panel_1']['/Rect']));bottom=top-height
  for key,src in basefields.items():
   m=pattern.fullmatch(key)
   if not m:continue
   kind,suffix=m[1],m[2];newkey=kind+'_'+str(i)+suffix
   if cols==1:
    old=list(map(float,src['/Rect']));rect=[old[0],bottom+(old[1]-model[1])*height/(model[3]-model[1]),old[2],bottom+(old[3]-model[1])*height/(model[3]-model[1])]
   elif kind=='panel':rect=[left,top-height,left+width,top]
   elif kind=='text':rect=[left+3,top-36,left+width-3,top-2]
   elif kind=='obs':rect=[left+3,top-63,left+width-3,top-52]
   elif kind=='b':rect=[left+(190 if suffix=='_S'else 228),top-50,left+(225 if suffix=='_S'else 266),top-40]
   else:
    pos={'APPCC':(3,60),'NC':(64,87),'P':(91,114),'NCxP':(118,153)}
    labelkey=suffix.removeprefix('_')if kind=='label'else {'cat':'APPCC','nc':'NC','p':'P','score':'NCxP'}[kind]
    a,b=pos[labelkey];rect=[left+a,top-(40 if kind=='label'else 50),left+b,top-(36 if kind=='label'else 41)]
   value=('F'+str(i+1)+' - '+f['texto']+'\n'+f['orientacao'])if kind=='text'else f['cat'].replace('PPHO','POP')if kind=='cat'else cfg['pesos'][f['cat']]if kind=='nc'else f['P']if kind=='p'else cfg['pesos'][f['cat']]*f['P']if kind=='score'else ''if kind in ['panel','obs']else 'BPF/APPCC'if kind=='label'and suffix=='_APPCC'else str(src.get('/V',''))
   if kind=='text':value='\r'.join(line for paragraph in str(value).split('\n')for line in simpleSplit(paragraph,'Helvetica',5.2,rect[2]-rect[0]-4))
   add(newkey,src,rect,value,action='marcarFrase.call(this,'+str(i)+',"'+suffix[-1]+'");'if kind=='b'else None,label=('Sim'if suffix=='_S'else'Não')if kind=='b'else None)
  if f.get('allowNA'):
   srect=next(list(map(float,ref.get_object()['/Rect']))for ref in annots if ref.get_object().get('/T')==prefix+'b_'+str(i)+'_S')
   add('b_'+str(i)+'_A',basefields['b_1_S'],[491,srect[1],558,srect[3]],action='marcarFrase.call(this,'+str(i)+',"A");',label='NA')
 page[NameObject('/Annots')]=annots;w.update_page_form_field_values(page,values,auto_regenerate=False)
pairs=sorted([(templates[i],templates[i+1])for i in range(0,len(templates),2)],key=lambda x:str(x[0]))
templates[:]=[v for pair in pairs for v in pair]
scripts=w.root_object['/Names']['/JavaScript']['/Names']
for i in range(1,len(scripts),2):
 obj=scripts[i].get_object();raw=obj['/JS'].get_object();s=raw.get_data().decode()if hasattr(raw,'get_data')else str(raw)
 if 'var CFG='not in s:continue
 s=s.replace("if(a==='A'&&!c.allowNA)a='';","if(a==='A'&&!(c.frases[i].allowNA===undefined?c.allowNA:c.frases[i].allowNA))a='';").replace("if(a==='A'&&!c.allowNA)return;","if(a==='A'&&!(c.frases[i].allowNA===undefined?c.allowNA:c.frases[i].allowNA))return;").replace("aa!=='A'||c.allowNA","aa!=='A'||(c.frases[i].allowNA===undefined?c.allowNA:c.frases[i].allowNA)")
 s=s.replace('guideField.textSize=6;','guideField.textSize=c.code==="4.10.3"?5.2:6;').replace('quebrarLinhas(guideText,528,6)','quebrarLinhas(guideText,c.code==="4.10.3"?264:528,c.code==="4.10.3"?5.2:6)')
 if 'function migrarDetalhesResponsavel'not in s:
  fn="""function migrarDetalhesResponsavel(){var d=dados.call(this);if(d.responsibleDetailsVersion==='responsabilidade-conselhos-20261101')return;d.legacyResponsibleDetails=d.legacyResponsibleDetails||{};for(var key in CFG.itens){var c=CFG.itens[key];if(c.code!=='4.11.2'||!d.u[key])continue;var old=d.u[key];if(old[5])continue;d.legacyResponsibleDetails[key]=JSON.parse(JSON.stringify(old));d.u[key]=[];for(var j=0;j<c.frases.length;j++)d.u[key][j]={c:c.frases[j].cat,a:'',o:'Revisar função e conselhos aplicáveis; resposta anterior preservada no histórico.'};}d.responsibleDetailsVersion='responsabilidade-conselhos-20261101';gravar.call(this,d);}
"""
  s=s.replace('function iniciar(){try{',fn+'function iniciar(){try{migrarDetalhesResponsavel.call(this);')
 if 'function migrarDetalhesCQ'not in s:
  fn="""function migrarDetalhesCQ(){var d=dados.call(this);if(d.qualityDetailsVersion==='cq-parametros-20261101')return;d.legacyQualityDetails=d.legacyQualityDetails||{};for(var key in CFG.itens){var c=CFG.itens[key];if((c.code!=='4.10.2'&&c.code!=='4.10.3')||!d.u[key])continue;var old=d.u[key];if(old[c.frases.length-1])continue;d.legacyQualityDetails[key]=JSON.parse(JSON.stringify(old));d.u[key]=[];for(var j=0;j<c.frases.length;j++)d.u[key][j]={c:c.frases[j].cat,a:'',o:'Revisar requisitos laboratoriais e analíticos individualmente; resposta geral anterior preservada no histórico.'};}d.qualityDetailsVersion='cq-parametros-20261101';gravar.call(this,d);}\n"""
  s=s.replace('function iniciar(){try{',fn+'function iniciar(){try{migrarDetalhesCQ.call(this);')
 if '/* role-alternatives */'not in s:
  guard="""/* role-alternatives */if(c.roleAlternatives){var allNA=true;for(var ri=0;ri<c.roleAlternatives.length;ri++){var rr=rs[c.roleAlternatives[ri]];if(!rr||rr.a!=='A')allNA=false;}if(allNA){hasNo=true;active=true;pending=false;num=0;den=den||1;}}"""
  s=s.replace("var answer=hasNo?'N':",guard+"var answer=hasNo?'N':")
  role_guard="""if(ACTIVE&&a==='A'){var ca=CFG.itens[ACTIVE.key],da=dados.call(this);if(ca.roleAlternatives&&ca.roleAlternatives.indexOf(i)>=0){var allNA=true;for(var ri=0;ri<ca.roleAlternatives.length;ri++){var idx=ca.roleAlternatives[ri];if(idx!==i&&(!da.u[ACTIVE.key]||!da.u[ACTIVE.key][idx]||da.u[ACTIVE.key][idx].a!=='A'))allNA=false;}if(allNA){app.alert('Ao menos uma função responsável deve ser aplicável. Registre Não se não houver responsável.');mostrarEditor.call(this);return;}}}"""
  s=s.replace('function marcarFrase(i,a){','function marcarFrase(i,a){'+role_guard)
 obj[NameObject('/JS')]=TextStringObject(s)
with path.open('wb')as f:w.write(f)
assert before.issubset(PdfReader(path).get_fields());assert len(PdfReader(path).pages)==22
# Current CQ page: fit the complete requirements, retaining the observation block.
paper=json.loads((R/'paper-data.js').read_text().split('=',1)[1].strip().rstrip(';'));metadata=json.loads((R/'process-display-data.json').read_text());doc=fitz.open(path);idx=11;pg=doc[idx];entries=list({c['code']:c for c in cfg['itens'].values()if c['page']==idx}.values());fs=paper[idx]['fields'];bottom=790;labels=[]
if labels:bottom=min(bottom,min(labels)-4)
riskend=max(f['y']+f['h']for f in fs if f['n'].startswith(('risk_','risco_resultado_')))
for c in entries:c['processId']=metadata[str(idx)+':'+c['code']]['processId']
positions=[r for c in entries for label in [c['code'],c['processId']]for r in pg.search_for(label)if r.x0<61 and riskend+15<r.y0<bottom];top=min(r.y0 for r in positions)-4
pg.add_redact_annot(fitz.Rect(14,top,581,bottom),fill=(1,1,1));pg.apply_redactions(images=0,graphics=0)
def overview(c):
 if c['code']=='4.10.3':return 'Produto envasado: F1 coliformes totais; F2 E. coli; F3 enterococos; F4 P. aeruginosa; F5 esporos sulfito redutores; F6 esporos de C. perfringens; F7 heterotróficas.\nCaptação semanal: F8 coliformes totais; F9 E. coli; F10 heterotróficas.\nReservatório semanal: F11 coliformes totais; F12 E. coli; F13 P. aeruginosa; F14 heterotróficas.\nF15: análise anual das substâncias do Anexo I da RDC 717/2022. F16: cinco amostras mensais do mesmo lote em laboratório externo. F17: cinco unidades de todos os lotes, início/meio/término. Requisitos completos no botão F.'
 return '\n'.join('F'+str(i+1)+' - '+f['texto']for i,f in enumerate(c['frases']))
for size in [6.1,5.9,5.7,5.5,5.3,5.1,4.9]:
 heights=[max(18,sum(len(simpleSplit(line,'Helvetica',size,512))for line in overview(c).split('\n'))*size*1.22+5)for c in entries]
 if sum(heights)<=bottom-top:break
assert sum(heights)<=bottom-top,(top,bottom,heights)
y=top
for c,h in zip(entries,heights):
 pg.draw_rect((14,y,581,y+h),color=(.52,.6,.65),fill=(1,1,1),width=.4);pg.draw_rect((14,y,60,y+h),color=(.52,.6,.65),fill=(.94,.96,.97),width=.4)
 assert pg.insert_textbox((15,y+1,59,y+h-1),c['processId']+'\n('+c['code']+')',fontsize=5.5,fontname='hebo',align=1,lineheight=1.05)>=0
 text=overview(c);assert pg.insert_textbox((63,y+2,579,y+h),text,fontsize=size,fontname='helv',lineheight=1.17)>=0;y+=h
tmp=path.with_suffix('.cq.pdf');doc.save(tmp,garbage=0,deflate=True);doc.close();tmp.replace(path);doc=fitz.open(path);doc[11].get_pixmap(matrix=fitz.Matrix(1.6,1.6),annots=False).save(R/paper[11]['image'])
print('CQ02 e CQ03: templates interativos e página de controle de qualidade atualizados.')
