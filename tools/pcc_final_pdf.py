"""Add editable PCC final considerations without altering the validated layout."""
from pathlib import Path
from pypdf import PdfReader,PdfWriter
from pypdf.generic import NameObject,TextStringObject,DictionaryObject,ArrayObject,NumberObject,FloatObject

def add_pcc_final(path):
 path=Path(path);writer=PdfWriter();writer.clone_document_from_reader(PdfReader(path))
 root=writer.root_object
 if 'pcc_final_generated' in (writer.get_fields() or {}):return
 field=DictionaryObject({NameObject('/FT'):NameObject('/Tx'),NameObject('/T'):TextStringObject('pcc_final_generated'),NameObject('/V'):TextStringObject('{}'),NameObject('/Type'):NameObject('/Annot'),NameObject('/Subtype'):NameObject('/Widget'),NameObject('/F'):NumberObject(2),NameObject('/Rect'):ArrayObject([FloatObject(-30),FloatObject(-30),FloatObject(-20),FloatObject(-20)])})
 ref=writer._add_object(field);root['/AcroForm']['/Fields'].append(ref);writer.pages[17]['/Annots'].append(ref)
 core=Path(__file__).with_name('pcc-final.js').read_text();adapter=Path(__file__).with_name('pcc-pdf.js').read_text()
 names=root['/Names']['/JavaScript']['/Names'];patched=False
 for i in range(1,len(names),2):
  action=names[i].get_object();source=str(action.get('/JS',''))
  if 'function indCalc(' in source or 'function recalcularTudo(' in source:
   action[NameObject('/JS')]=TextStringObject(source+'\n'+core+'\n'+adapter);patched=True
 assert patched,'Main calculation script not found'
 tmp=path.with_suffix('.pcc.tmp')
 with tmp.open('wb') as stream:writer.write(stream)
 tmp.replace(path)
 assert 'pcc_final_generated' in PdfReader(path).get_fields()

if __name__=='__main__':
 import sys
 for p in sys.argv[1:]:add_pcc_final(p);print('PCC final considerations:',p)
