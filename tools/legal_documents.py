"""Enforce document-delivery dependencies in an editable guide PDF."""
import os,re,sys
from pathlib import Path
from pypdf import PdfReader,PdfWriter
from pypdf.generic import NameObject,NumberObject,TextStringObject,DictionaryObject

SCRIPT=r'''
function LEGAL_DOCS_SET(index,status){
 var answer=this.getField('doc_legal_'+index+'_atende');
 var situation=this.getField('doc_legal_'+index+'_situacao');
 if(!answer||!situation)return;
 var value=status===undefined?situation.value:status;
 var allowed=String(value||'').toLowerCase()==='entregue';
 if(!allowed)answer.value='';
 answer.readonly=!allowed;
 answer.fillColor=allowed?color.white:color.ltGray;
}
for(var LEGAL_DOCS_I=1;LEGAL_DOCS_I<=8;LEGAL_DOCS_I++)LEGAL_DOCS_SET.call(this,LEGAL_DOCS_I);
'''

def lock_legal_docs(path):
 path=Path(path);reader=PdfReader(path);writer=PdfWriter();writer.clone_document_from_reader(reader)
 nodes=[];seen=set()
 def visit(ref):
  obj=ref.get_object()
  identity=id(obj)
  if identity in seen:return
  seen.add(identity);nodes.append(obj)
  for child in obj.get('/Kids',[]):visit(child)
 for ref in writer.root_object['/AcroForm']['/Fields']:visit(ref)
 for page in writer.pages:
  for ref in page.get('/Annots',[]):visit(ref)
 def action(obj,key,code):
  aa=obj.get('/AA')
  aa=DictionaryObject(aa.get_object()) if aa else DictionaryObject()
  before=aa.get(key)
  old=str(before.get_object().get('/JS','')) if before else ''
  aa[NameObject(key)]=DictionaryObject({NameObject('/S'):NameObject('/JavaScript'),NameObject('/JS'):TextStringObject(old+'\n'+code)})
  obj[NameObject('/AA')]=aa
 for obj in nodes:
  name=str(obj.get('/T',''))
  if not name and obj.get('/Parent'):name=str(obj['/Parent'].get_object().get('/T',''))
  match=re.fullmatch(r'doc_legal_(\d+)_(situacao|atende)',name)
  if not match:continue
  i,kind=match.groups()
  if kind=='situacao':
   action(obj,'/V',f'LEGAL_DOCS_SET.call(this,{i},event.value);')
   action(obj,'/Bl',f'LEGAL_DOCS_SET.call(this,{i});')
  else:
   obj[NameObject('/Ff')]=NumberObject(int(obj.get('/Ff',0))|1)
   obj[NameObject('/V')]=TextStringObject('');obj[NameObject('/DV')]=TextStringObject('')
   action(obj,'/V',f"if(String(this.getField('doc_legal_{i}_situacao').value).toLowerCase()!=='entregue'){{event.rc=false;event.value='';}}")
 # Replace the legacy initialization rule as well: reopening a saved PDF
 # must not restore an automatic "NÃO" for an undelivered document.
 names=writer.root_object.get('/Names',{}).get('/JavaScript',{}).get('/Names',[])
 for index in range(1,len(names),2):
  act=names[index].get_object();source=str(act.get('/JS',''))
  source=source.replace("else if(v==='Não entregue'){a.value='NÃO';", "else if(v==='Não entregue'){a.value='';")
  act[NameObject('/JS')]=TextStringObject(source)
 writer.add_js(SCRIPT)
 temp=path.with_name(path.name+'.legal-docs.tmp')
 with temp.open('wb') as stream:writer.write(stream)
 os.replace(temp,path)
 check=PdfReader(path);fields=check.get_fields()
 for i in range(1,9):
  name=f'doc_legal_{i}_atende'
  assert fields[name]['/Ff']&1
  assert not fields[name].get('/V')
  assert '/V' in fields[f'doc_legal_{i}_situacao']['/AA']
  widgets=[ref.get_object() for page in check.pages for ref in page.get('/Annots',[]) if ref.get_object().get('/T')==name]
  assert widgets and all(int(widget.get('/Ff',0))&1 for widget in widgets)
 return path

if __name__=='__main__':
 for name in sys.argv[1:]:
  print('Updated delivery dependencies:',lock_legal_docs(name))
