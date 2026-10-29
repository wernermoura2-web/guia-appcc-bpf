"""Restore full phrase descriptions and use process display codes on original guide."""
from pathlib import Path
import json,fitz
from pypdf import PdfReader
from PIL import Image
from process_metadata import apply
ROOT=Path(__file__).resolve().parents[1]
paper=json.loads((ROOT/'paper-data.js').read_text().split('=',1)[1].strip().rstrip(';'))
cfg=apply(json.loads((ROOT/'config.js').read_text().split('=',1)[1].strip().rstrip(';')),ROOT)
p=ROOT/'Guia_APPCC_BPF.pdf';before=PdfReader(p);signature={k:(v.get('/FT'),v.get('/V'))for k,v in before.get_fields().items()};doc=fitz.open(p)
for idx in range(13):
 page=doc[idx];entries=list({c['code']:c for c in cfg['itens'].values()if c['page']==idx}.values());fields=paper[idx]['fields'];notes=[f for f in fields if f['n'].startswith('obs_gerais')]
 bottom=min(f['y']for f in notes)-19 if notes else 775
 riskend=max(f['y']+f['h']for f in fields if f['n'].startswith(('risk_','risco_resultado_')))
 positions=[r for c in entries for label in (c['code'],c['processId']) for r in page.search_for(label)if r.x0<61 and riskend+15<r.y0<bottom]
 top=min(r.y0 for r in positions)-4
 # Remove prior full/short summaries as a single block, retaining live form areas.
 assert not any(f['y']<bottom and f['y']+f['h']>top and f['x']<581 and f['x']+f['w']>14 for f in fields),(idx,top,bottom)
 page.add_redact_annot(fitz.Rect(14,top,581,bottom),fill=(1,1,1))
 # Replace item numbers in the response table without altering stable field names.
 codes=[]
 for c in entries:
  for label in (c['code'],c['processId']):
   for r in page.search_for(label):
    if r.x0<61 and r.y0<top:
     page.add_redact_annot(r,fill=(.94,.96,.97));codes.append((r,c['processId']))
 headers=[]
 for block in page.get_text('blocks'):
  if 'ITENS DO ANEXO' in block[4].upper() or 'ITENS DE BPF E APPCC' in block[4].upper():headers.append(fitz.Rect(block[:4]))
 for r in headers:page.add_redact_annot(r,fill=(.86,.91,.94))
 page.apply_redactions(images=0,graphics=0,text=0)
 for r,code in codes:
  page.insert_textbox(fitz.Rect(r.x0-1,r.y0-1,max(59,r.x1+1),r.y1+2),code,fontsize=6.3,fontname='hebo',align=1)
 for r in headers:page.insert_textbox(fitz.Rect(14,r.y0-1,581,r.y1+3),'ITENS DE BPF E APPCC (Anexo I da norma de BPF - Resolução RDC Anvisa nº 173/06)',fontsize=6.7,fontname='hebo',align=1)
 # Allocate row heights from the full text, never omit a phrase.
 for size in [7,6.7,6.4,6.1,5.8,5.5]:
  heights=[]
  for c in entries:
   text='\n'.join('F'+str(i+1)+' - '+f['texto']for i,f in enumerate(c['frases']))
   from reportlab.lib.utils import simpleSplit
   lines=sum(len(simpleSplit('F'+str(i+1)+' - '+f['texto'],'Helvetica',size,512))for i,f in enumerate(c['frases']))
   heights.append(max(lines*size*1.22+6,25))
  if sum(heights)<=bottom-top:break
 assert sum(heights)<=bottom-top,(idx,sum(heights),bottom-top)
 y=top
 for c,h in zip(entries,heights):
  page.draw_rect((14,y,581,y+h),color=(.52,.6,.65),fill=(1,1,1),width=.4)
  page.draw_rect((14,y,60,y+h),color=(.52,.6,.65),fill=(.94,.96,.97),width=.4)
  assert page.insert_textbox((15,y+3,59,y+h-1),c['processId']+'\n('+c['code']+')',fontsize=6.4,fontname='hebo',align=1)>=0
  text='\n'.join('F'+str(i+1)+' - '+f['texto']for i,f in enumerate(c['frases']))
  assert page.insert_textbox((63,y+2,579,y+h),text,fontsize=size,fontname='helv',lineheight=1.17)>=0,(idx,c['code'])
  y+=h
 print('Page',idx+1,'font',size,'phrases',sum(len(c['frases'])for c in entries))
# Change static PPO labels; appearances for live form controls are refreshed separately.
for page in doc:
 for r in page.search_for('PPHO'):
  page.add_redact_annot(r,fill=(1,1,1));page.apply_redactions(images=0,graphics=0,text=0)
  page.insert_textbox(r+fitz.Rect(0,-1,2,2),'PPO',fontsize=min(7,r.height*.65),fontname='helv')
 # Field storage keys remain stable; display aliases are handled by native JS.
tmp=p.with_suffix('.descriptions.pdf');doc.save(tmp,garbage=0,deflate=True);doc.close();p.write_bytes(tmp.read_bytes());tmp.unlink()
check=PdfReader(p);assert len(check.pages)==22;assert signature=={k:(v.get('/FT'),v.get('/V'))for k,v in check.get_fields().items()}
# Render only static content; live controls, answers and simulations remain browser overlays.
doc=fitz.open(p)
for idx in range(13):
 pix=doc[idx].get_pixmap(matrix=fitz.Matrix(1.6,1.6),annots=False);im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples);im.save(ROOT/paper[idx]['image'])
 if idx==12:im.save((ROOT/paper[idx]['image']).with_suffix('.webp'),quality=92)
print('22 pages, field identities and saved values preserved; backgrounds regenerated')
