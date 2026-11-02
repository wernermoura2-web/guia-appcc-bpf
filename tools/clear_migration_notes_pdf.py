"""Remove system migration notices while preserving inspector observations."""
from pathlib import Path
import re,json
from pypdf import PdfReader,PdfWriter
from pypdf.generic import NameObject,TextStringObject
R=Path(__file__).resolve().parents[1];p=R/'Guia_APPCC_BPF.pdf'
w=PdfWriter();w.clone_document_from_reader(PdfReader(p))
scripts=w.root_object['/Names']['/JavaScript']['/Names']
for i in range(1,len(scripts),2):
 obj=scripts[i].get_object();raw=obj['/JS'].get_object();s=raw.get_data().decode()if hasattr(raw,'get_data')else str(raw)
 if 'var CFG='not in s or 'function limparAvisosMigracao' in s:continue
 notices=list(dict.fromkeys(re.findall(r"o:'((?:Revisar|Confirmar)[^']*)'",s)))
 assert len(notices)>=5,notices
 fn="function limparAvisosMigracao(){var d=dados.call(this),changed=false,notices="+json.dumps(notices,ensure_ascii=False)+";for(var key in d.u){var rows=d.u[key];for(var j=0;j<rows.length;j++){var row=rows[j];if(row&&notices.indexOf(row.o)>=0){row.o=row.o.indexOf('Revisar capacitação e registros separadamente;')===0&&d.legacyCapRecords&&d.legacyCapRecords[key]?d.legacyCapRecords[key].o||'':'';changed=true;}}}if(changed)gravar.call(this,d);}\n"
 s=s.replace('function iniciar(){',fn+'function iniciar(){').replace('atualizarObservacoes.call(this)','limparAvisosMigracao.call(this);atualizarObservacoes.call(this)')
 obj[NameObject('/JS')]=TextStringObject(s)
with p.open('wb')as f:w.write(f)
print('Avisos automáticos removidos das observações; histórico preservado.')
