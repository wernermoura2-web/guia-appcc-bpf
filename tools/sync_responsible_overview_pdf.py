"""Sync full six-phrase RM02 description without changing form geometry."""
from pathlib import Path
import json,fitz
from reportlab.lib.utils import simpleSplit
from pypdf import PdfReader
R=Path(__file__).resolve().parents[1];path=R/'Guia_APPCC_BPF.pdf';signature=set(PdfReader(path).get_fields())
cfg=json.loads((R/'config.js').read_text()[10:].strip().rstrip(';'));paper=json.loads((R/'paper-data.js').read_text().split('=',1)[1].strip().rstrip(';'));metadata=json.loads((R/'process-display-data.json').read_text())
doc=fitz.open(path);idx=12;pg=doc[idx];entries=list({c['code']:c for c in cfg['itens'].values()if c['page']==idx}.values());fs=paper[idx]['fields'];bottom=790;riskend=max(f['y']+f['h']for f in fs if f['n'].startswith(('risk_','risco_resultado_')))
for c in entries:c['processId']=metadata[str(idx)+':'+c['code']]['processId']
positions=[r for c in entries for label in [c['code'],c['processId']]for r in pg.search_for(label)if r.x0<61 and riskend+15<r.y0<bottom];assert positions;top=min(r.y0 for r in positions)-4
pg.add_redact_annot(fitz.Rect(14,top,581,bottom),fill=(1,1,1));pg.apply_redactions(images=0,graphics=0)
for size in [6.1,5.9,5.7,5.5,5.3,5.1,4.9]:
 heights=[max(18,sum(len(simpleSplit('F'+str(i+1)+' - '+f['texto'],'Helvetica',size,512))for i,f in enumerate(c['frases']))*size*1.22+5)for c in entries]
 if sum(heights)<=bottom-top:break
assert sum(heights)<=bottom-top,(top,bottom,heights)
y=top
for c,h in zip(entries,heights):
 pg.draw_rect((14,y,581,y+h),color=(.52,.6,.65),fill=(1,1,1),width=.4);pg.draw_rect((14,y,60,y+h),color=(.52,.6,.65),fill=(.94,.96,.97),width=.4)
 assert pg.insert_textbox((15,y+1,59,y+h-1),c['processId']+'\n('+c['code']+')',fontsize=5.5,fontname='hebo',align=1,lineheight=1.05)>=0
 text='\n'.join('F'+str(i+1)+' - '+f['texto']for i,f in enumerate(c['frases']));assert pg.insert_textbox((63,y+2,579,y+h),text,fontsize=size,fontname='helv',lineheight=1.17)>=0;y+=h
tmp=path.with_suffix('.rm.pdf');doc.save(tmp,garbage=0,deflate=True);doc.close();tmp.replace(path)
assert signature==set(PdfReader(path).get_fields());doc=fitz.open(path);pix=doc[12].get_pixmap(matrix=fitz.Matrix(1.6,1.6),annots=False);pix.save(R/paper[12]['image'])
from PIL import Image
im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples);im.save((R/paper[12]['image']).with_suffix('.webp'),quality=92)
print('RM02 F1–F6: PDF e fundos HTML atualizados; campos preservados.')
