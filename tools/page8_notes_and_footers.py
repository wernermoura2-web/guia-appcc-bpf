from pathlib import Path
import json,fitz,re
from PIL import Image
from pypdf import PdfReader
from reportlab.lib.utils import simpleSplit
R=Path(__file__).resolve().parents[1];path=R/'Guia_APPCC_BPF.pdf';paper=json.loads((R/'paper-data.js').read_text().split('=',1)[1].strip().rstrip(';'));cfg=json.loads((R/'config.js').read_text().split('=',1)[1].strip().rstrip(';'));metadata=json.loads((R/'process-display-data.json').read_text());before=PdfReader(path);signature={k:(v.get('/FT'),v.get('/V'))for k,v in before.get_fields().items()};doc=fitz.open(path)
logo_xref=next(image[0] for image in doc[0].get_images(full=True) if image[2:4]==(183,35))
logo_bytes=doc.extract_image(logo_xref)['image']
# Remove instructional footer text and the old printed button captions; keep page numbers and branding.
for page in doc:
 for b in page.get_text('dict')['blocks']:
  for line in b.get('lines',[]):
   text=''.join(s['text']for s in line['spans']).strip();rect=fitz.Rect(line['bbox'])
   if rect.y0>780 and text and not text.startswith(('Página ','Limpar página')):page.add_redact_annot(rect,fill=(1,1,1))
 page.apply_redactions(images=0,graphics=0,text=0)
# Page 8: compact unused spacing between the complete descriptions, retaining the phrase font.
idx=7;page=doc[idx];notes=[f for f in paper[idx]['fields']if f['n'].startswith('obs_gerais')];old_height=notes[0]['h'];new_height=old_height*1.5;bottom=812.;new_top=bottom-new_height;top=315.
page.add_redact_annot((14,top,581,bottom),fill=(1,1,1));page.apply_redactions(images=0,graphics=0,text=0);page.draw_rect((14,top,581,bottom),color=None,fill=(1,1,1))
entries=list({c['code']:c for c in cfg['itens'].values()if c['page']==idx}.values());size=5.8;heights=[max(17,sum(len(simpleSplit('F'+str(i+1)+' - '+f['texto'],'Helvetica',size,512))for i,f in enumerate(c['frases']))*size*1.18+3)for c in entries];assert top+sum(heights)<new_top-17
at=top
for c,h in zip(entries,heights):
 page.draw_rect((14,at,581,at+h),color=(.52,.6,.65),fill=(1,1,1),width=.4);page.draw_rect((14,at,60,at+h),color=(.52,.6,.65),fill=(.94,.96,.97),width=.4)
 code=metadata[str(idx)+':'+c['code']]['processId'];assert page.insert_textbox((15,at+1,59,at+h),code+'\n('+c['code']+')',fontsize=5.5,fontname='hebo',align=1,lineheight=1.1)>=0
 text='\n'.join('F'+str(i+1)+' - '+f['texto']for i,f in enumerate(c['frases']));assert page.insert_textbox((63,at+1,579,at+h),text,fontsize=size,fontname='helv',lineheight=1.17)>=0,c['code'];at+=h
page.draw_rect((14,new_top-17,581,new_top-2),color=(.52,.6,.65),fill=(.94,.96,.97),width=.4);page.insert_textbox((14,new_top-15,581,new_top-3),'OBSERVAÇÕES GERAIS',fontsize=7,fontname='hebo',align=1)
for f in notes:
 f['y']=new_top;f['h']=new_height;w=next(w for w in page.widgets()if w.field_name==f['n']);w.rect=fitz.Rect(f['x'],new_top,f['x']+f['w'],bottom);w.update();page.draw_rect(w.rect,color=(.52,.6,.65),width=.4)
# Put every clear-page button to the left of the page number, with a gap below the notes.
for i,model in enumerate(paper):
 for f in model['fields']:
  if not f['n'].startswith('limpar_processo_'):continue
  f.update(x=390.,y=817.,w=100.,h=14.)
  bound_page=doc[i];w=next(w for w in bound_page.widgets()if w.field_name==f['n']);w.rect=fitz.Rect(390,817,490,831);w.update()
# Redraw page numbers cleanly in their own area to the right of the buttons.
for i,page in enumerate(doc):
 page.add_redact_annot((498,814,581,835),fill=(1,1,1));page.apply_redactions(images=0,graphics=0,text=0)
 assert page.insert_textbox((498,817,581,833),'Página '+str(i+1)+' de '+str(len(doc)),fontsize=7.5,fontname='helv',align=2)>=0
 # Repaint the complete official SES logo last so no footer mask can cover it.
 page.draw_rect((245,813,351,835),color=None,fill=(1,1,1))
 page.insert_image((246,815,350.5,834.98),stream=logo_bytes,keep_proportion=True,overlay=True)
tmp=path.with_suffix('.layout.pdf');doc.save(tmp,garbage=0,deflate=True);doc.close();tmp.replace(path);(R/'paper-data.js').write_text('const PAPER='+json.dumps(paper,ensure_ascii=False,separators=(',',':'))+';\n')
check=PdfReader(path);assert signature=={k:(v.get('/FT'),v.get('/V'))for k,v in check.get_fields().items()};assert len(check.pages)==22
for f in notes:assert f['h']==old_height*1.5
# Re-render every page because footer instructions appeared throughout the guide.
doc=fitz.open(path)
for i,model in enumerate(paper):
 pix=doc[i].get_pixmap(matrix=fitz.Matrix(1.6,1.6),annots=False);im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples);im.save(R/model['image']);im.save((R/model['image']).with_suffix('.webp'),quality=92)
 for b in doc[i].get_text('dict')['blocks']:
  for line in b.get('lines',[]):
   text=''.join(s['text']for s in line['spans']).strip()
   assert not(line['bbox'][1]>780 and text and not text.startswith(('Página ','Limpar página'))),(i,text)
print('PASS: page 8 observation height',old_height,'->',new_height,'(+50%); 22 pages; fields and saved values preserved; footer text removed; clear buttons moved.')
