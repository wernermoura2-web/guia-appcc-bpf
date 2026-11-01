"""Update only the CAP03 static description; preserve page geometry and form fields."""
from pathlib import Path
import json,fitz
from pypdf import PdfReader
R=Path(__file__).resolve().parents[1]
p=R/'Guia_APPCC_BPF.pdf';signature=set(PdfReader(p).get_fields())
cfg=json.loads((R/'config.js').read_text()[10:].strip().rstrip(';'))
c=next(c for c in cfg['itens'].values()if c['code']=='4.1.3')
doc=fitz.open(p);page=doc[0]
label=next(r for r in page.search_for('CAP03')if r.y0>360)
rect=fitz.Rect(62,label.y0-3.2,580,453)
page.add_redact_annot(rect,fill=(1,1,1));page.apply_redactions(images=0,graphics=0)
text='\n'.join('F'+str(i+1)+' - '+f['texto']for i,f in enumerate(c['frases']))
assert page.insert_textbox(rect,text,fontname='helv',fontsize=5.8,lineheight=1.05)>=0
tmp=p.with_suffix('.cap.pdf');doc.save(tmp,garbage=0,deflate=True);doc.close();tmp.replace(p)
assert set(PdfReader(p).get_fields())==signature
doc=fitz.open(p);paper=json.loads((R/'paper-data.js').read_text().split('=',1)[1].strip().rstrip(';'))
doc[0].get_pixmap(matrix=fitz.Matrix(1.6,1.6),annots=False).save(R/paper[0]['image'])
assert 'F3 - Devem ser mantidos registros' in doc[0].get_text()
print('CAP03 F1/F2/F3: PDF e imagem HTML atualizados, campos preservados.')
