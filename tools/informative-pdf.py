from pathlib import Path
from pypdf import PdfReader,PdfWriter
from pypdf.generic import NameObject,NumberObject,TextStringObject
root=Path(__file__).resolve().parents[1];p=root/'Guia_APPCC_BPF.pdf';r=PdfReader(p);w=PdfWriter();w.clone_document_from_reader(r)
a=w.root_object['/Names']['/JavaScript']['/Names']
for i in range(1,len(a),2):
 o=a[i].get_object();s=o['/JS'].get_object();s=s.get_data().decode() if hasattr(s,'get_data') else str(s)
 if 'function avaliar(' not in s:continue
 marker='function recalcularTudo(){'
 fn="""function simularAPPCC(keys,d){var num=0,den=0,active=false;for(var i=0;i<keys.length;i++){var z=avaliar.call(this,keys[i],d);if(!z.active)continue;active=true;for(var j=0;j<z.rows.length;j++)if(!z.rows[j].a)return null;num+=z.num;den+=z.den;}return active&&den?100*num/den:null;}
function simulacaoTexto(pct,isPercent){return '(APPCC: '+(pct===null?'Pendente':isPercent?pctTexto(pct):nomeRisco(risco('',pct)))+')';}
"""
 assert marker in s;s=s.replace(marker,fn+marker)
 s=s.replace("put.call(this,'pct_'+g,q.pct!==null?pctTexto(q.pct):q.na?'N/A':'');put.call(this,'risk_'+g,q.pending?'Pendente':q.na?'N/A':q.pct!==null?nomeRisco(risco(cfg.proc,q.pct)):'');", "var sim=simularAPPCC.call(this,keys,d);put.call(this,'pct_'+g,(q.pct!==null?pctTexto(q.pct):q.na?'N/A':'')+'\\r'+simulacaoTexto(sim,true));put.call(this,'risk_'+g,(q.pending?'Pendente':q.na?'N/A':q.pct!==null?nomeRisco(risco(cfg.proc,q.pct)):'')+'\\r'+simulacaoTexto(sim,false));")
 s=s.replace("put.call(this,'pct_resultado_p'+pp,q.pct!==null?pctTexto(q.pct):q.na?'N/A':'');put.call(this,'risco_resultado_p'+pp,q.pending?'Pendente':q.na?'N/A':q.pct!==null?nomeRisco(risco(proc,q.pct)):'');", "var simkeys=[];for(var sk in CFG.itens)if(CFG.itens[sk].page===Number(page))simkeys.push(sk);var sim=simularAPPCC.call(this,simkeys,d);put.call(this,'pct_resultado_p'+pp,(q.pct!==null?pctTexto(q.pct):q.na?'N/A':'')+'\\r'+simulacaoTexto(sim,true));put.call(this,'risco_resultado_p'+pp,(q.pending?'Pendente':q.na?'N/A':q.pct!==null?nomeRisco(risco(proc,q.pct)):'')+'\\r'+simulacaoTexto(sim,false));")
 o[NameObject('/JS')]=TextStringObject(s)
for obj in w._objects:
 if not isinstance(obj,dict):continue
 n=str(obj.get('/T',''))
 if n.startswith(('pct_','risk_','risco_resultado_')):
  obj[NameObject('/Ff')]=NumberObject(int(obj.get('/Ff',0))|4097);obj[NameObject('/DA')]=TextStringObject('/Helv 5.2 Tf 0 g')
tmp=p.with_suffix('.tmp.pdf');w.write(tmp);check=PdfReader(tmp);assert len(check.pages)==22;p.write_bytes(tmp.read_bytes());tmp.unlink();print('PDF: official item result + APPCC simulation')
