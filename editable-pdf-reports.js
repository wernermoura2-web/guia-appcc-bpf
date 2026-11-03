/* Download prebuilt blank forms without generating PDF fields in the browser. */
(()=>{
 const link=document.querySelector('a[download]');
 if(!link)return;
 const toggle=document.getElementById('include-document-checklist');
 function update(){const name=toggle?.checked?'Guia_APPCC_BPF_Em_Branco_Todos_F_Documentos.pdf':'Guia_APPCC_BPF_Em_Branco_Todos_F.pdf';link.href=name+'?v=formulario-f-20261103';link.download=name;}
 toggle?.addEventListener('change',update);update();
})();

/* Export current answers as an AcroForm, retaining native F actions. */
window.exportEditableInspection=async function(){
 const button=document.getElementById('paper-print'),status=document.getElementById('paper-status');
 if(button.disabled)return;button.disabled=true;
 try{
  refreshPaper();save();window.DocumentChecklistAnnex?.prepare();
  const values={},answers={},units={},native={u:{},refs:{},generated:{},manual:{},full:{},det:{}};
  for(const page of PAPER)for(const f of page.fields)values[f.n]=f.type==='/Btn'&&!f.push?(String(fieldValue(f)).startsWith('☒')?'Yes':'Off'):fieldValue(f);
  for(const [key,c]of Object.entries(CFG.itens)){
   answers[key]=rows(key);const totals=APPCCScoring.totals(c,answers[key],CFG.pesos);answers[key].forEach((r,i)=>{r.points=S.units['p'+c.page+'c'+c.col]===false?0:(totals.contributions[i]?.earned||0);});native.u[key]=answers[key].map(r=>({c:r.cat,a:r.a||'',o:r.obs||''}));native.det[key]=true;
   units[c.page+':'+c.col]=unitName(c.page,c.col);
  }
  Object.assign(native,{capRecordsVersion:'captacao-registros-f3-20261101',hygieneRecordsVersion:'higienizacao-registros-f2-20261101',individualPhrasesVersion:'frases-individuais-20261101',pccHigieneVersion:'pcc-higienizacao-condutividade-20261102',qualityDetailsVersion:'cq-parametros-20261101',qualityReportsVersion:'laudos-cq05-tres-frases-20261102',qualityVersion:'controle-qualidade-ppro-20261024',removedHygieneRecordVersion:'medias-frases-20261102',reservoirSplitVersion:'reservatorio-f4-f5-f6-20261101',responsibilityVersion:'responsabilidade-ppho-ppro-20261024',responsibleDetailsVersion:'responsabilidade-conselhos-20261101'});
  const documents=[...document.querySelectorAll('#documents-print-copy .doc-process')].map(section=>({title:section.querySelector('h2').textContent,tables:[...section.querySelectorAll('table')].map(table=>({title:table.previousElementSibling.textContent,rows:[...table.querySelectorAll('tbody tr')].filter(tr=>tr.cells.length===7).map(tr=>({cells:[...tr.cells].map(td=>td.innerText),states:[...tr.cells].slice(2).map(td=>td.innerText.trim()==='X')}))}))}));
  const catalog=window.InspectorOrientations.catalog(),guidance=Object.fromEntries(catalog.map(r=>[r.id,window.InspectorOrientations.value(r.id)]));
  status.textContent='Preparando PDF preenchível com os dados da inspeção…';
  const worker=new Worker('editable-inspection-worker.js?v=formulario-f-20261103');
  const bytes=await new Promise((resolve,reject)=>{worker.onmessage=e=>{worker.terminate();e.data.error?reject(Error(e.data.error)):resolve(e.data.bytes);};worker.onerror=e=>{worker.terminate();reject(Error(e.message));};worker.postMessage({cfg:CFG,values,answers,units,native,catalog,guidance,meta:S.meta,notes:S.notes,images:S.images,paper:PAPER,documents,docs:!!document.getElementById('include-document-checklist')?.checked,compact:!!document.getElementById('paper-include-guidance')?.checked});});
  const url=URL.createObjectURL(new Blob([bytes],{type:'application/pdf'})),link=document.createElement('a');link.href=url;link.download='Guia_APPCC_BPF_Inspecao_Editavel.pdf';link.click();setTimeout(()=>URL.revokeObjectURL(url),60000);
  status.textContent='PDF preenchível gerado com os dados e anexos selecionados.';
 }catch(error){status.textContent='Não foi possível gerar o PDF: '+error.message;alert(status.textContent);}
 finally{button.disabled=false;}
};
