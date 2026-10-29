"""Correct displayed PPO labels to POP without changing the APPCC configuration or weights."""
from pathlib import Path
import json,fitz
from PIL import Image
from pypdf import PdfReader,PdfWriter
from pypdf.generic import TextStringObject,NameObject,ArrayObject
R=Path(__file__).resolve().parents[1];path=R/'Guia_APPCC_BPF.pdf'
reader=PdfReader(path);writer=PdfWriter();writer.clone_document_from_reader(reader)
for obj in writer._objects:
 if not isinstance(obj,dict):continue
 for key in ['/V','/DV']:
  if obj.get(key)=='PPO':obj[NameObject(key)]=TextStringObject('POP')
 if '/Opt'in obj:
  obj[NameObject('/Opt')]=ArrayObject([TextStringObject('POP')if str(value)=='PPO'else value for value in obj['/Opt']])
 if '/JS'in obj:
  value=obj['/JS'].get_object();text=value.get_data().decode()if hasattr(value,'get_data')else str(value)
  if 'PPO'in text:
   text=text.replace('PPO','POP').replace("/PPHO/g,'POP'","/PPHO|PPO/g,'POP'")
   text=text.replace('CFG.pesos.POP=CFG.pesos.PPHO;', 'CFG.pesos.POP=CFG.pesos.PPHO;CFG.pesos.PPO=CFG.pesos.PPHO;')
   obj[NameObject('/JS')]=TextStringObject(text)
tmp=path.with_suffix('.pop.pdf');writer.write(tmp);tmp.replace(path)
doc=fitz.open(path)
# Change appearance text as well as the logical choice values, including hidden F templates.
for xref in range(1,doc.xref_length()):
 if doc.xref_is_stream(xref)and doc.xref_get_key(xref,'Subtype')[1]=='/Form':
  raw=doc.xref_stream(xref)
  if b'PPO'in raw:doc.update_stream(xref,raw.replace(b'PPO',b'POP'))
for page in doc:
 rects=page.search_for('PPO')
 for rect in rects:page.add_redact_annot(rect,fill=(1,1,1))
 if rects:
  page.apply_redactions(images=0,graphics=0,text=0)
  for rect in rects:page.insert_textbox(rect+fitz.Rect(0,-1,2,2),'POP',fontsize=min(7,rect.height*.65),fontname='helv')
tmp=path.with_suffix('.pop.pdf');doc.save(tmp,garbage=0,deflate=True);doc.close();tmp.replace(path)
check=PdfReader(path);assert len(check.pages)==22;assert set(reader.get_fields())==set(check.get_fields());assert all(str(f.get('/V',''))!='PPO'for f in check.get_fields().values())
paper=json.loads((R/'paper-data.js').read_text().split('=',1)[1].strip().rstrip(';'));doc=fitz.open(path)
for i,model in enumerate(paper):
 pix=doc[i].get_pixmap(matrix=fitz.Matrix(1.6,1.6),annots=False);im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples);im.save(R/model['image']);im.save((R/model['image']).with_suffix('.webp'),quality=92)
print('PASS: POP nos rótulos e opções do PDF, 22 páginas e identificadores preservados.')
