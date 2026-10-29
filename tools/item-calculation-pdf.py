"""Use original item attendance; retain APPCC points as read-only simulation."""
from pathlib import Path
from pypdf import PdfReader,PdfWriter
from pypdf.generic import NameObject,NumberObject,TextStringObject
import re
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'Guia_APPCC_BPF.pdf'
r=PdfReader(source);w=PdfWriter();w.clone_document_from_reader(r)
a=w.root_object['/Names']['/JavaScript']['/Names']
for i in range(1,len(a),2):
 o=a[i].get_object();s=o['/JS'].get_object();s=s.get_data().decode() if hasattr(s,'get_data') else str(s)
 if 'function avaliar(' not in s:continue
 old="return {active:active,complete:active&&!pending,a:pending?'':!den?'A':hasNo?'N':'S',peso:num,num:num,den:den,rows:rs};"
 new="var answer=hasNo?'N':pending?'':!den?'A':'S';return {active:active,complete:active&&(hasNo||!pending),a:answer,peso:num,num:num,den:den,itemNum:answer==='S'?1:0,itemDen:den?1:0,rows:rs};"
 assert old in s;s=s.replace(old,new)
 s=s.replace('den+=z.den;num+=z.num;','den+=z.itemDen;num+=z.itemNum;')
 s=s.replace("(it.den?pctTexto(100*it.num/it.den):'N/A')","(it.itemDen?pctTexto(100*it.itemNum/it.itemDen):'N/A')")
 s=re.sub(r'function mudarAPPCC\(cf,novo\)\{.*?\}\nfunction recuperarEditor', 'function mudarAPPCC(cf,novo){return;}\nfunction recuperarEditor',s,count=1,flags=re.S)
 s=re.sub(r'function registrarClasseFrase\(i,v\)\{.*?\}\nfunction marcarFrase', 'function registrarClasseFrase(i,v){return;}\nfunction marcarFrase',s,count=1,flags=re.S)
 s=s.replace("if(f&&CFG.pesos[f.valueAsString])rs[i].c=f.valueAsString;",'')
 s=s.replace("if(ind!==undefined&&ind!==null&&CFG.pesos[cat])rs[ind].c=cat;",'')
 s=s.replace("' | NC x P satisfatório = '","' | APPCC informativo: '")
 s=s.replace("var rf=editorF.call(this,'ed_resumo');", "var rf=editorF.call(this,'ed_resumo');")
 o[NameObject('/JS')]=TextStringObject(s)
locked=0
# Includes the hidden templates that Acrobat spawns for F.
for obj in w._objects:
 if not isinstance(obj,dict):continue
 name=str(obj.get('/T',''))
 if re.search(r'(^classe_|^criticidade_classe_|^prob_classe_|^pontuacao_|^pont_result_|ed_(cat|nc|p|score)_\d+)',name):
  obj[NameObject('/Ff')]=NumberObject(int(obj.get('/Ff',0))|1);locked+=1
# Print a compact note in each process page, below the observations.
import io
from reportlab.pdfgen import canvas
buf=io.BytesIO();cv=canvas.Canvas(buf,pagesize=(595.32,841.92))
for pg in range(len(w.pages)):
 if pg<13:
  cv.setFillColorRGB(1,1,1);cv.rect(36,21,520,18,fill=1,stroke=0)
  cv.setFillColorRGB(.15,.2,.25);cv.setFont('Helvetica',6)
  cv.drawString(40,32,'APPCC definido e pontuação: apenas informativos; simulação de como seria se aplicado.')
  cv.drawString(40,24,'Média oficial por item: Sim = 1; Não = 0; NA excluído. Uma frase Não torna o item Não.')
 cv.showPage()
cv.save();buf.seek(0)
for p,overlay in zip(w.pages,PdfReader(buf).pages):p.merge_page(overlay)
tmp=source.with_suffix('.tmp.pdf');w.write(tmp)
check=PdfReader(tmp);assert len(check.pages)==len(r.pages)
assert set(r.get_fields())<=set(check.get_fields())
for n,f in check.get_fields().items():
 if n.startswith('classe_') or re.search(r'ed_cat_\d+',n):assert int(f.get('/Ff',0))&1,n
assert locked>100
source.write_bytes(tmp.read_bytes());tmp.unlink()
print('PDF:',len(check.pages),'pages;',locked,'APPCC fields locked')
