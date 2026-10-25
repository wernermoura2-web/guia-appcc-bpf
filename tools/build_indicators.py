"""Build the legislative indicators in the validated 22-page BPF layout.

Run from the site root. Source PDF is retained in .build; generated PDF, page
backgrounds and browser form geometry are emitted together from one model.
"""
import json, math, re, shutil
from pathlib import Path
import fitz
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, DictionaryObject, ArrayObject, NumberObject

ROOT=Path(__file__).resolve().parents[1]
CFG=json.loads((ROOT/'config.js').read_text().split('=',1)[1].rstrip().rstrip(';'))
BUILD=ROOT/'.build';BUILD.mkdir(exist_ok=True)
SOURCE=BUILD/'source.pdf'
if not SOURCE.exists():shutil.copyfile(ROOT/'Guia_APPCC_BPF.pdf',SOURCE)
doc=fitz.open(SOURCE)
BLUE=(.86,.91,.94); PALE=(.94,.96,.97); LINE=(.35,.42,.46)
PAGE_NAMES=['Captação','Condução das captações','Reservatórios - Captação 1','Reservatórios - Captação 2','Reservatórios - Captação 3','Reservatórios - Captação 4','Recepção de embalagens e insumos','Higienização de retornáveis e tampas','Higienização de descartáveis e tampas','Envase de retornáveis','Envase de descartáveis','Controle de qualidade','Responsabilidade e manipuladores']
names={0:['CAPTAÇÃO 1','CAPTAÇÃO 2','CAPTAÇÃO 3','CAPTAÇÃO 4'],1:['CONDUÇÃO 1','CONDUÇÃO 2','CONDUÇÃO 3','CONDUÇÃO 4'],6:['RETORNÁVEIS','DESCARTÁVEIS','RÓTULOS','SANEANTES'],7:['LINHA 1','LINHA 2','LINHA 3','TAMPAS'],8:['LINHA 1','LINHA 2','LINHA 3','TAMPAS'],9:['LINHA 1','LINHA 2','LINHA 3','LINHA 4'],10:['LINHA 1','LINHA 2','LINHA 3','LINHA 4']}
ORDER={6:[18,22,19,20,21],7:[30,31,32,33,34,40,35,36,37,38,39],8:[43,44,45,51,46,47,48,49,50]}
FONTS={'helv':fitz.Font('helv'),'hebo':fitz.Font('hebo')}
def clean(text):
 return str(text).replace('–','-').replace('—','-').replace('’',"'").replace('‘',"'").replace('“','"').replace('”','"').replace('Σ','Soma').replace('≥','>=').replace('≤','<=')
def lines(text,width,size,font='helv'):
 out=[]
 for paragraph in clean(text).split('\n'):
  line=''
  for word in paragraph.split():
   if line and FONTS[font].text_length(line+' '+word,fontsize=size)>width:out.append(line);line=word
   else:line=(line+' '+word).strip()
  out.append(line)
 return out
def text(pg,rect,value,size=7,bold=False,align=0,color=(0,0,0)):
 r=fitz.Rect(rect);font='hebo' if bold else 'helv';ls=lines(value,r.width-4,size,font)
 height=len(ls)*size*1.15
 if height>r.height-1:
  raise ValueError(f'Text overflow p{pg.number+1}: {value[:70]!r}: {height:.1f}>{r.height:.1f}')
 y=r.y0+(r.height-height)/2+size*.91
 for line in ls:
  length=FONTS[font].text_length(line,fontsize=size)
  x=r.x0+2 if align==0 else r.x0+(r.width-length)/2
  pg.insert_text((x,y),line,fontname=font,fontsize=size,color=color);y+=size*1.15
def cell(pg,rect,value='',size=7,bold=False,fill=None,align=0):
 pg.draw_rect(rect,color=LINE,fill=fill,width=.45)
 if value:text(pg,rect,value,size,bold,align)
def widget(pg,name,rect,value='',ro=False,multi=False,button=False,label='',script=''):
 w=fitz.Widget();w.field_name=name;w.rect=fitz.Rect(rect);w.field_type=fitz.PDF_WIDGET_TYPE_BUTTON if button else fitz.PDF_WIDGET_TYPE_TEXT
 w.field_value=value;w.field_label=label;w.text_font='Helv';w.text_fontsize=6.6 if not multi else 7
 w.text_color=(0,0,0);w.fill_color=(1,1,1);w.border_width=0
 if button:w.field_flags=fitz.PDF_BTN_FIELD_IS_PUSHBUTTON;w.button_caption=label or value;w.script=script
 else:w.field_flags=(fitz.PDF_FIELD_IS_READ_ONLY if ro else 0)|(fitz.PDF_TX_FIELD_IS_MULTILINE if multi else 0)
 pg.add_widget(w)
def inset(r,n=.7):return fitz.Rect(r[0]+n,r[1]+n,r[2]-n,r[3]-n)
def phrases_for(entries):
 out=[];seen=set()
 for c in entries:
  for j,f in enumerate(c['frases']):
   sig=(j,f['texto'],f['ref'])
   if sig in seen:continue
   seen.add(sig);out.append((j+1,f))
 return out

for page in range(13):
 pg=doc[page];pnum=page+1;top=183 if page==0 else 90
 # Retain the original institutional header, identification, title and footer.
 for w in list(pg.widgets() or []):
  if w.rect.y1>top and w.rect.y0<795:pg.delete_widget(w)
 pg.add_redact_annot(fitz.Rect(13,top-1,582,795),fill=(1,1,1))
 pg.apply_redactions(images=0,graphics=1,text=0)
 # The first page's old label refers only to the former RDC item numbering.
 if page==0:
  pg.add_redact_annot(fitz.Rect(14,165,581,181),fill=BLUE);pg.apply_redactions(images=0,graphics=1)
  text(pg,(14,165,581,181),'INDICADORES - REVISÃO LEGISLATIVA / APPCC BPF',8,True,1)
 entries={k:c for k,c in CFG['itens'].items() if c['page']==page}
 codes=sorted({int(c['code']) for c in entries.values()},key=lambda c:ORDER.get(page,[]).index(c) if page in ORDER else c)
 columns=sorted({c['col'] for c in entries.values()})
 def description_height(size):
  return sum(max(16,sum(len(lines(f'F{j} - '+f['texto']+' ['+f['ref']+']',516,size))*size*1.13+2 for j,f in phrases_for([c for c in entries.values() if c['code']==str(code)]))) for code in codes)
 xs=[14,60,98,126,155,174,258,342,426,510,581] if page<11 else [14,60,98,126,155,174,510,581]
 headers=['INDIC.','APPCC','NC','P','NC x P']
 if page<11:headers+=names.get(page,['RESERV. 1','RESERV. 2','RESERV. 3','RESERV. 4'])+['RESULTADO']
 else:headers+=['OBSERVAÇÕES (2 COLUNAS)','RESULTADO']
 hh=28 if page<11 else 22
 for a,b,label in zip(xs,xs[1:],headers):cell(pg,(a,top,b,top+hh),label,6.2,True,BLUE,1)
 y=top+hh
 if page in (0,1):
  # Keep the original names, brand and flow fields in the 4-column layout.
  for row,label in enumerate(['NOME DA CAPTAÇÃO']+(['MARCAS ENVASADAS','VAZÃO (m³/h)'] if page==0 else [])):
   h=14;cell(pg,(14,y,174,y+h),label,6.8,True,PALE)
   for col in columns:
    cell(pg,(xs[4+col],y,xs[5+col],y+h))
    if page==0:
     fields={0:[3,9,4,10],1:[5,11,6,12],2:[13,15,14,16]}
     name=f'campo_p1_{fields[row][col-1]}'
    else:name=f'nome_captacao_p2_{col}'
    widget(pg,name,inset((xs[4+col],y,xs[5+col],y+h)))
   cell(pg,(510,y,581,y+h));y+=h
 if page==0:
  cell(pg,(14,y,174,y+14),'FONTE: POÇO OU SURGÊNCIA',6.5,True,PALE)
  for col in columns:
   a,b=xs[4+col],xs[5+col];mid=(a+b)/2;cell(pg,(a,y,b,y+14))
   for j,(left,right,label) in enumerate([(a,mid,'Poço'),(mid,b,'Surgência')]):
    widget(pg,f'fonte_{col}_{j}',inset((left,y,right,y+14)),label=label,button=True,script=f'selecionarFonte.call(this,{col},{json.dumps(label)});')
  cell(pg,(510,y,581,y+14));y+=14
 rowheight=15.3 if page<11 else (23 if page==11 else 37)
 if page in (11,12):
  rowheight=(788-y-56-description_height(7.25))/len(codes)
 for code in codes:
  cs=[c for c in entries.values() if c['code']==str(code)]
  fs=[f for c in cs for f in c['frases']]
  cats='/'.join(dict.fromkeys(f['cat'] for f in fs));ns='/'.join(str(x) for x in dict.fromkeys(CFG['pesos'][f['cat']] for f in fs));ps='/'.join(str(x) for x in dict.fromkeys(f['P'] for f in fs))
  refs='/'.join(str(x) for x in dict.fromkeys(sum(CFG['pesos'][f['cat']]*f['P'] for f in c['frases']) for c in cs))
  values=[str(code),cats if len(cats)<11 else 'Ver F',ns if len(ns)<7 else 'Ver F',ps,refs]
  for i,value in enumerate(values):
   cell(pg,(xs[i],y,xs[i+1],y+rowheight),value,5.4 if i==1 and len(cats)>12 else 6.1,i==0,BLUE if i==0 else None,1)
  # Summary fields show all phrase classes; changing a class is done in F.
  summary_top=y+(rowheight-13)/2 if page>=11 else y+.7
  summary_bottom=summary_top+13 if page>=11 else y+rowheight-.7
  for name,a,b,value in [(f'classe_p{pnum}_{code}',60,98,cats),(f'criticidade_classe_p{pnum}_{code}',98,126,ns),(f'prob_classe_p{pnum}_{code}',126,155,ps),(f'pontuacao_p{pnum}_{code}',155,174,refs)]:widget(pg,name,(a+.7,summary_top,b-.7,summary_bottom),value if len(value)<11 else 'Ver F',ro=True)
  if page<11:
   for col in columns:
    a,b=xs[4+col],xs[5+col];cell(pg,(a,y,b,y+rowheight))
    pair=next(((k,c) for k,c in entries.items() if c['code']==str(code) and c['col']==col),None)
    if not pair:text(pg,(a,y,b,y+rowheight),'NÃO APLICÁVEL',5.6,False,1);continue
    key,c=pair;choices=['S','N']+(['A'] if c['allowNA'] else [])+['F'];cw=(b-a)/len(choices)
    for j,ch in enumerate(choices):
     r=(a+j*cw,y,b if j==len(choices)-1 else a+(j+1)*cw,y+rowheight)
     label={'S':'Sim','N':'Não','A':'NA','F':'F'}[ch]
     widget(pg,f'b_{key}_{ch}',inset(r),label=label,button=True,script=f'abrirFrases.call(this,{json.dumps(key)});' if ch=='F' else f'marcarItem.call(this,{json.dumps(key)},{json.dumps(ch)});')
  else:
   cell(pg,(174,y,510,y+rowheight));mid=342;pg.draw_line((mid,y),(mid,y+rowheight),color=LINE,width=.4)
   widget(pg,f'obs_p{pnum}_{code}',(175,y+1,341,y+rowheight-1),multi=True)
   widget(pg,f'obs_p{pnum}_{code}_col2',(343,y+1,509,y+rowheight-1),multi=True)
   key=next(k for k,c in entries.items() if c['code']==str(code))
   button_top=y+(rowheight-16)/2
   widget(pg,f'b_{key}_F',(512,button_top,532,button_top+16),label='F',button=True,script=f'abrirFrases.call(this,{json.dumps(key)});')
  cell(pg,(510,y,581,y+rowheight))
  result_top=y+(rowheight-14)/2 if page>=11 else y+1
  result_bottom=result_top+14 if page>=11 else y+rowheight-1
  widget(pg,f'res_p{pnum}_{code}',(533 if page>=11 else 511,result_top,580,result_bottom),ro=True)
  y+=rowheight
 for mode,label in [('pct','% ATENDIDO'),('risk','RISCO')]:
  cell(pg,(14,y,174,y+14),label,7,True,BLUE,1)
  if page<11:
   for col in columns:
    a,b=xs[4+col],xs[5+col];cell(pg,(a,y,b,y+14));widget(pg,f'{mode}_p{pnum}c{col}',inset((a,y,b,y+14)),ro=True)
  else:cell(pg,(174,y,510,y+14))
  cell(pg,(510,y,581,y+14));widget(pg,f'{"pct_resultado" if mode=="pct" else "risco_resultado"}_p{pnum}',inset((510,y,581,y+14)),ro=True);y+=14
 for label,ranges,colors in [('AVALIAÇÃO',['100%','76 - 99%','51 - 75%','0 - 50%'],[None]*4),('RISCO',['1 BAIXO','1 BAIXO','2 MÉDIO','3 ALTO'],[(.57,.82,.31),(.57,.82,.31),(1,1,0),(1,.14,.14)])]:
  cell(pg,(14,y,126,y+12),label,6.5,True,None,1)
  for i,(value,color) in enumerate(zip(ranges,colors)):a=126+i*(455/4);cell(pg,(a,y,a+455/4,y+12),value,6.4,True,color,1)
  y+=12
 y+=4
 # Full legislative text, including the references. Font size is fitted once
 # per page. Never silently clip or omit a phrase to fit a fixed page count.
 available=788-y-(68 if page<11 else 0)
 size=7.25
 # Page 8 keeps the former response grid. Shrink ONLY the description text
 # and reserve twice the baseline editable height for the two note columns.
 if page==7:
  former_note_top=y+description_height(7.25)+19
  former_usable_height=789-former_note_top-1.4
  note_top=789-2*former_usable_height-1.4
  available=note_top-19-y
  low,high=5.5,7.25
  for _ in range(45):
   middle=(low+high)/2
   if description_height(middle)<=available:low=middle
   else:high=middle
  size=math.floor(low*1000)/1000
 while description_height(size)>available+.001 and size>6.1:size-=.1
 if description_height(size)>available+.001:raise ValueError(f'Page {pnum}: descriptions do not fit')
 # Description rows retain their original height and font; only the UPPER
 # indicator/observation rows receive the additional A4 space on pages 12/13.
 extra_description_height=0
 description_bottoms=[]
 for code in codes:
  pf=phrases_for([c for c in entries.values() if c['code']==str(code)])
  texts=[f'F{j} - '+f['texto']+' ['+f['ref']+']' for j,f in pf]
  heights=[len(lines(t,516,size))*size*1.13+2 for t in texts];h=max(16,sum(heights))+extra_description_height
  cell(pg,(14,y,60,y+h),f'Indicador\n{code}',6.5,True,PALE,1);cell(pg,(60,y,581,y+h))
  dy=y+1
  for t,th in zip(texts,heights):
   ls=lines(t,516,size)
   for line in ls:pg.insert_text((62,dy+size*.91),clean(line),fontname='helv',fontsize=size);dy+=size*1.13
   dy+=2
  glyph_bottom=dy-2+.1*size
  if glyph_bottom>y+h+.01:raise ValueError(f'Page {pnum}: description crosses its row')
  description_bottoms.append(glyph_bottom)
  y+=h
 if page<11:
  if page==7:y=max(y,note_top-19)
  y+=3;cell(pg,(14,y,581,y+14),'OBSERVAÇÕES GERAIS',7,True,PALE,1);y+=16
  if description_bottoms and max(description_bottoms)>y-16+.01:raise ValueError(f'Page {pnum}: notes overlap descriptions')
  for suffix,a,b in [('',14,294),('_col2',301,581)]:
   rect=(a,y,b,789);cell(pg,rect);widget(pg,f'obs_gerais_p{pnum}{suffix}',inset(rect),multi=True)
 print(f'Page {pnum}: {len(codes)} indicators; description font {size:.2f}; ends at {y:.1f}')
 # Per-phrase data are stored in invisible canonical fields used by Acrobat F.
 for key,c in entries.items():
  for j,f in enumerate(c['frases']):
   for prefix,value in [('ans',''),('cat',f['cat']),('note','')]:
    widget(pg,f'{prefix}_{key}_{j}',(-30,-30,-20,-20),value)

tmp=BUILD/'modified.pdf';doc.save(tmp,garbage=4,deflate=True);doc.close()
reader=PdfReader(tmp);writer=PdfWriter();writer.clone_document_from_reader(reader)
root=writer.root_object
names_obj=root.get('/Names',DictionaryObject()).get_object();names_obj.pop(NameObject('/Templates'),None);names_obj.pop(NameObject('/JavaScript'),None)
for pg in writer.pages:
 for obj in pg.get('/Annots',[]):
  obj=obj.get_object();n=str(obj.get('/T',''))
  if n.startswith(('ans_q_','cat_q_','note_q_')):obj[NameObject('/F')]=NumberObject(2)
js=(ROOT/'tools/indicator_pdf.js').read_text().replace('__CFG__',json.dumps(CFG,ensure_ascii=True,separators=(',',':')))
writer.add_js(js)
out=ROOT/'Guia_APPCC_BPF.pdf'
with out.open('wb') as f:writer.write(f)

# Backgrounds have NO widget appearances: live values and controls are drawn
# exclusively from PAPER to prevent stale values on screen and on paper.
pdf=fitz.open(out);paper=[]
(ROOT/'paginas').mkdir(exist_ok=True)
for i,pg in enumerate(pdf):
 fields=[]
 for w in pg.widgets() or []:
  if w.rect.x1<0 or w.field_name.startswith(('ans_q_','cat_q_','note_q_')):continue
  typ={fitz.PDF_WIDGET_TYPE_TEXT:'/Tx',fitz.PDF_WIDGET_TYPE_BUTTON:'/Btn',fitz.PDF_WIDGET_TYPE_CHECKBOX:'/Btn',fitz.PDF_WIDGET_TYPE_COMBOBOX:'/Ch'}.get(w.field_type,'/Tx')
  r=w.rect
  fields.append({'n':w.field_name,'type':typ,'x':r.x0,'y':r.y0,'w':r.width,'h':r.height,'ro':bool(w.field_flags&1),'multi':bool(w.field_flags&4096),'push':bool(w.field_flags&65536),'v':w.field_value or '', 'options':w.choice_values or [],'label':w.button_caption or w.field_label or '', 'font':w.text_fontsize or 7})
 name=f'paginas/layout-v4-{i+1:02d}.webp'
 pix=pg.get_pixmap(matrix=fitz.Matrix(1.6,1.6),annots=False)
 from PIL import Image
 Image.frombytes('RGB',[pix.width,pix.height],pix.samples).save(ROOT/name,'WEBP',quality=92)
 paper.append({'width':pg.rect.width,'height':pg.rect.height,'fields':fields,'image':name})
(ROOT/'paper-data.js').write_text('const PAPER='+json.dumps(paper,ensure_ascii=False,separators=(',',':'))+';\n')
(ROOT/'paper-data-layout-v4.js').write_text('const PAPER='+json.dumps(paper,ensure_ascii=False,separators=(',',':'))+';\n')
shutil.copyfile(out,ROOT/'Guia_APPCC_BPF_Layout_v4.pdf')
# Integrity: canonical fields and widget tree must both include every phrase.
check=PdfReader(out);fields=check.get_fields();expected={f'{prefix}_{k}_{j}' for k,c in CFG['itens'].items() for j,f in enumerate(c['frases']) for prefix in ('ans','cat','note')}
assert expected<=fields.keys(),expected-fields.keys()
assert len(check.pages)==22
assert all(fields[f'cat_{k}_{j}'].get('/V')==f['cat'] for k,c in CFG['itens'].items() for j,f in enumerate(c['frases']))
assert all(not fields[n].get('/V') for n in expected if n.startswith('ans_'))
print(f'Built {out.name}: {len(check.pages)} pages, {len(fields)} canonical fields')

