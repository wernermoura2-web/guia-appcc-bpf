(()=>{'use strict';
 const api=window.InspectorOrientations;if(!api)return;
 const $=id=>document.getElementById(id),catalog=api.catalog();let displayedCount=catalog.length;
 const create=(tag,className,text)=>{const el=document.createElement(tag);if(className)el.className=className;if(text!==undefined)el.textContent=text;return el;};
 function message(text,error=false){$('save-status').textContent=text;$('save-status').classList.toggle('error',error);}
 function updateSummary(){const edited=api.count();$('result-count').textContent=`${displayedCount} de ${catalog.length} orientações · ${edited} ${edited===1?'revisada':'revisadas'}`;$('restore-all').disabled=!edited;$('undo-recovery').hidden=!api.hasRecovery();return edited;}
 function recover(action,success){try{action();render();message(success);}catch(error){message('Não foi possível recuperar o texto: '+error.message,true);}}
 function render(){
  const proc=$('process-filter').value,query=$('search').value.trim().toLocaleLowerCase('pt-BR');
  const rows=catalog.filter(row=>(!proc||row.proc===proc)&&(!query||[row.code,row.process,row.requirement,api.value(row.id)].join(' ').toLocaleLowerCase('pt-BR').includes(query)));
  const fragment=document.createDocumentFragment();let current=null;
  rows.forEach((row,n)=>{
   if(row.proc!==current){fragment.appendChild(create('h2','process-title',row.process));current=row.proc;}
   const card=create('article','guidance-card'),heading=create('div','card-heading'),title=create('h3','',`${api.guide==='original'?'Item':'Indicador'} ${row.code} · ${row.phraseLabels.join(' / ')}`),badge=create('span','edited','Revisada');badge.hidden=!api.changed(row.id);heading.append(title,badge);card.appendChild(heading);
   card.appendChild(create('p','requirement',row.requirement));
   if(row.references.length||row.sourceTexts.length){const details=create('details','reference');details.appendChild(create('summary','','Referências e texto de origem'));for(const text of [...row.sourceTexts,...row.references])details.appendChild(create('p','',text));card.appendChild(details);}
   const label=create('label','','Orientação ao inspetor'),textarea=create('textarea');textarea.id='orientacao-'+n;textarea.value=api.value(row.id);label.htmlFor=textarea.id;card.append(label,textarea);
   const footer=create('div','card-footer'),restore=create('button','','Recuperar original');restore.type='button';restore.disabled=!api.changed(row.id);restore.onclick=()=>recover(()=>api.restore(row.id),'Texto original recuperado. Você pode desfazer a recuperação.');footer.append(restore,create('small','','O requisito acima não é alterado pela revisão.'));card.appendChild(footer);
   textarea.addEventListener('input',()=>{try{api.set(row.id,textarea.value);badge.hidden=!api.changed(row.id);restore.disabled=!api.changed(row.id);updateSummary();message('Orientação salva neste aparelho. A revisão já está disponível no F do guia online.');}catch(error){message('Não foi possível salvar a orientação: '+error.message,true);}});
   fragment.appendChild(card);
  });
  $('guidance-list').replaceChildren(fragment);$('empty-results').hidden=rows.length>0;
  displayedCount=rows.length;updateSummary();
 }
 function renderPrint(){
  const report=$('print-report'),fragment=document.createDocumentFragment();fragment.appendChild(create('h1','',`Orientações aos inspetores — ${api.title}`));fragment.appendChild(create('p','report-meta',`${catalog.length} orientações · ${api.count()} ${api.count()===1?'revisada':'revisadas'} · ${new Intl.DateTimeFormat('pt-BR',{dateStyle:'short',timeStyle:'short',timeZone:'America/Sao_Paulo'}).format(new Date())}`));
  let proc=null,section;
  for(const row of catalog){
   if(proc!==row.proc){section=create('section','report-process');section.appendChild(create('h2','',row.process));fragment.appendChild(section);proc=row.proc;}
   const article=create('article','report-row');article.appendChild(create('h3','',`${api.guide==='original'?'Item':'Indicador'} ${row.code} · ${row.phraseLabels.join(' / ')}`));article.appendChild(create('p','',row.requirement));const p=create('p','guidance-text');p.append(create('strong','','Orientação ao inspetor: '),document.createTextNode(api.value(row.id)||'Orientação não preenchida.'));article.appendChild(p);if(row.references.length)article.appendChild(create('p','report-reference',row.references.join(' · ')));section.appendChild(article);
  }
  report.replaceChildren(fragment);
 }
 $('guide-name').textContent=api.title;document.title='Orientações aos inspetores — '+api.title;
 const processes=new Map(catalog.map(row=>[row.proc,row.process]));for(const [value,text]of processes){const option=create('option','',text);option.value=value;$('process-filter').appendChild(option);}
 $('process-filter').addEventListener('change',render);$('search').addEventListener('input',render);
 $('restore-all').onclick=()=>recover(()=>api.restoreAll(),'Textos originais recuperados. Use “Desfazer recuperação” para voltar à sua revisão.');
 $('undo-recovery').onclick=()=>recover(()=>api.undoRecovery(),'Sua revisão anterior foi recuperada.');
 $('print-all').onclick=()=>{renderPrint();window.print();};window.addEventListener('beforeprint',renderPrint);
 $('export-guidance').onclick=()=>{try{const blob=new Blob([JSON.stringify(api.snapshot(),null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=create('a');a.href=url;a.download='Orientacoes_Inspetores_'+(api.guide==='original'?'Original':'Revisao')+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);message('Cópia das orientações preparada para salvar.');}catch(error){message(error.message,true);}};
 $('import-guidance').addEventListener('change',async event=>{const file=event.target.files?.[0];if(!file)return;try{api.importData(JSON.parse(await file.text()));render();message('Cópia aberta. As orientações estão disponíveis para revisão e impressão.');}catch(error){message('Não foi possível abrir a cópia: '+error.message,true);}finally{event.target.value='';}});
 window.addEventListener('storage',e=>{if(e.key===api.storageKey||e.key===null)render();});window.addEventListener('pageshow',()=>{api.reload();render();});
 render();
})();
