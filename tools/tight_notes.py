from pathlib import Path
import json,math,fitz
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];p=ROOT/'Guia_APPCC_BPF.pdf';paper=json.loads((ROOT/'paper-data.js').read_text().split('=',1)[1].strip().rstrip(';'));doc=fitz.open(p)
for idx in range(11):
 page=doc[idx];notes=[f for f in paper[idx]['fields']if f['n'].startswith('obs_gerais')];oldtop=min(f['y']for f in notes);riskend=max(f['y']+f['h']for f in paper[idx]['fields']if f['n'].startswith(('risk_','risco_resultado_')))
 lines=[l for b in page.get_text('dict')['blocks']if 'lines'in b for l in b['lines']if l['bbox'][0]>60 and riskend+20<l['bbox'][1]<oldtop-19]
 end=max(l['bbox'][3]for l in lines);newtop=min(oldtop,math.ceil(end)+21);bottom=max(f['y']+f['h']for f in notes)
 # Use the entire former gap to enlarge notes, leaving the bottom fixed.
 page.add_redact_annot((14,newtop-19,581,bottom+1),fill=(1,1,1));page.apply_redactions(images=0,graphics=0,text=0)
 page.draw_rect((14,newtop-17,581,newtop-2),color=(.52,.6,.65),fill=(.94,.96,.97),width=.4)
 page.insert_textbox((14,newtop-15,581,newtop-3),'OBSERVAÇÕES GERAIS',fontsize=7,fontname='hebo',align=1)
 for f in notes:
  oldh=f['h'];bottom=f['y']+f['h'];f['y']=newtop;f['h']=bottom-newtop;assert f['h']>=oldh-.01
  w=next(w for w in page.widgets()if w.field_name==f['n']);w.rect=fitz.Rect(f['x'],f['y'],f['x']+f['w'],f['y']+f['h']);w.update();page.draw_rect(w.rect,color=(.52,.6,.65),width=.4)
 print(idx+1,'notes',oldtop,'->',newtop,'height',notes[0]['h'])
tmp=p.with_suffix('.tight.pdf');doc.save(tmp,garbage=0,deflate=True);doc.close();p.write_bytes(tmp.read_bytes());tmp.unlink();(ROOT/'paper-data.js').write_text('const PAPER='+json.dumps(paper,ensure_ascii=False,separators=(',',':'))+';\n')
doc=fitz.open(p)
for idx in range(13):
 pix=doc[idx].get_pixmap(matrix=fitz.Matrix(1.6,1.6),annots=False);im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples);im.save(ROOT/paper[idx]['image'])
 if idx==12:im.save((ROOT/paper[idx]['image']).with_suffix('.webp'),quality=92)
