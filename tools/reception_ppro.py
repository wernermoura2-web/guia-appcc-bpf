"""Synchronize the receipt rejection classification in the editable original PDF."""
import json,sys
from pathlib import Path
from pypdf import PdfReader,PdfWriter
from pypdf.generic import NameObject,TextStringObject

def patch(path):
 reader=PdfReader(path);writer=PdfWriter();writer.clone_document_from_reader(reader)
 names=writer.root_object['/Names']['/JavaScript']['/Names']
 for index in range(1,len(names),2):
  entry=names[index].get_object();obj=entry.get('/JS');s=obj.get_object().get_data().decode() if hasattr(obj.get_object(),'get_data') else str(obj)
  start=s.find('var CFG=')
  if start<0:continue
  cfg,end=json.JSONDecoder().raw_decode(s[start+len('var CFG='):])
  for c in cfg['itens'].values():
   if c['code']=='4.5.3':
    for f in c['frases']:
     if 'reprovados' in f['texto']:f['cat']='PPRO'
  for f in cfg.get('frases',{}).get('4.5.3',[]):
   if 'reprovados' in f['texto']:f['cat']='PPRO'
  s=s[:start]+'var CFG='+json.dumps(cfg,ensure_ascii=True,separators=(',',':'))+s[start+len('var CFG=')+end:]
  migration="""function migrarRecepcaoPPRO(){var d=dados.call(this);if(d.receptionPPROVersion==='recepcao-ppro-20261026')return;for(var k in CFG.itens){var c=CFG.itens[k];if(c.code!=='4.5.3')continue;delete d.refs[c.classField];if(d.u[k])for(var i=0;i<c.frases.length;i++)if(c.frases[i].texto.indexOf('reprovados')>=0&&d.u[k][i])d.u[k][i].c='PPRO';}d.receptionPPROVersion='recepcao-ppro-20261026';gravar.call(this,d);}\n"""
  if 'function migrarRecepcaoPPRO' not in s:s=migration+s;s=s.replace('migrarResponsabilidade.call(this);','migrarRecepcaoPPRO.call(this);migrarResponsabilidade.call(this);')
  entry[NameObject('/JS')]=TextStringObject(s)
 values={'classe_p7_4.5.3':'PPRO','criticidade_classe_p7_4.5.3':'4','pontuacao_p7_4.5.3':'60'}
 writer.update_page_form_field_values(None,values,auto_regenerate=False)
 for name,value in values.items():
  writer.get_fields()[name][NameObject('/DV')]=TextStringObject(value)
 out=Path(str(path)+'.recepcao.tmp')
 with out.open('wb') as f:writer.write(f)
 out.replace(path)
 assert PdfReader(path).get_fields()['classe_p7_4.5.3']['/V']=='PPRO'
if __name__=='__main__':
 for arg in sys.argv[1:]:patch(Path(arg));print('PPRO atualizado no PDF original:',arg)
