(()=>{'use strict';
 const api=window.InspectorOrientations,button=document.getElementById('paper-print');if(!api||!button)return;
 const make=(tag,text)=>{const el=document.createElement(tag);if(text!==undefined)el.textContent=text;return el;};
 const label=make('label'),check=make('input');check.type='checkbox';check.id='paper-include-guidance';check.checked=new URLSearchParams(location.search).get('anexos')==='1';label.className='screen-only guidance-print-option';label.append(check,document.createTextNode('Incluir anexo F compacto — somente linhas preenchidas, até 40 páginas'));button.closest('.tools').after(label);
 const report=make('section');report.id='guidance-annex';report.setAttribute('aria-label','Anexo dos F — respostas e observações');document.body.appendChild(report);
 function tableFor(row,instances){
  const table=make('table');table.className='annex-metrics';const head=make('thead'),tr=make('tr'),body=make('tbody');
  for(const title of ['Unidade / F','Resposta','APPCC','NC','P','NC × P','Pontos obtidos','Observações da frase / complemento manual']){const th=make('th');if(title==='Pontos obtidos')th.append(make('span','Pontos'),make('span','obtidos'));else th.textContent=title;tr.appendChild(th);}head.appendChild(tr);table.append(head,body);
  for(const instance of instances){
   const c=CFG.itens[instance.key],r=rows(instance.key)[instance.index],active=S.units['p'+c.page+'c'+c.col]!==false,record=make('tr');record.className='annex-evaluation';record.dataset.key=instance.key;record.dataset.index=instance.index;
   let unit=unitName(c.page,c.col);if(c.page<=1&&S.names?.[c.col])unit+=' — '+S.names[c.col];if(c.page>=2&&c.page<=5)unit+=' · Captação '+(c.page-1)+(S.names?.[c.page-1]?' — '+S.names[c.page-1]:'');
   const allowed=c.frases[instance.index].allowNA??c.allowNA,nc=CFG.pesos[r.cat],weight=nc*r.P;
   const answers=({S:'☒ Sim',N:'☒ Não',A:'☒ NA'}[r.a]||'—');
   for(const value of [unit+'\nF'+(instance.index+1)+(active?'':' · Unidade não utilizada'),answers,r.cat,nc,r.P,weight,active&&r.a==='S'?weight:0])record.appendChild(make('td',String(value??'')));
   const obs=make('td');obs.className='annex-observation';obs.appendChild(make('div',r.obs||''));const line=make('div');line.className='annex-write-line';if(!String(r.obs||'').trim())obs.appendChild(line);record.appendChild(obs);body.appendChild(record);
  }return table;
 }
 function articleFor(row,instances){
  const item=make('article');item.className='annex-row';item.append(make('h3',row.process+' · '+(row.processId?row.processId+' · ':'')+(api.guide==='original'?'Item ':'Indicador ')+row.code+' · '+row.phraseLabels.join(' / ')),make('p',row.requirement));
  if(row.references.length){const ref=make('p','Referência normativa: '+row.references.join(' · '));ref.className='annex-reference';item.appendChild(ref);}
  item.appendChild(tableFor(row,instances));return item;
 }
 function paginate(blocks){
  // Measure the actual text in A4 content boxes. Reduce uniformly only when needed,
  // retaining every answer and every character instead of clipping the last pages.
  report.classList.add('annex-measuring');let scale=1,pages=[];
  for(let attempt=0;attempt<30;attempt++){
   report.replaceChildren();pages=[];let content,sheet;
   function newPage(){sheet=make('section');sheet.className='annex-page';content=make('div');content.className='annex-page-content';content.style.width=(182/scale)+'mm';content.style.zoom=String(scale);content.style.left=(14/scale)+'mm';content.style.top=(14/scale)+'mm';sheet.appendChild(content);report.appendChild(sheet);pages.push(sheet);}
   newPage();let fits=true;
   for(const block of blocks){content.appendChild(block);if(content.getBoundingClientRect().height>sheet.getBoundingClientRect().height*262/297){content.removeChild(block);if(content.children.length)newPage();content.appendChild(block);if(content.getBoundingClientRect().height>sheet.getBoundingClientRect().height*262/297){fits=false;break;}}}
   if(fits&&pages.length<=40)break;
   scale*=fits?Math.min(.95,Math.sqrt(38/pages.length)):.85;
   if(attempt===29)throw Error('Não foi possível paginar o anexo.');
  }
  report.dataset.pages=String(pages.length);report.dataset.scale=String(scale);
  pages.forEach((page,i)=>{const footer=make('div','Anexo F · '+(i+1)+' de '+pages.length);footer.className='annex-footer';page.appendChild(footer);});report.classList.remove('annex-measuring');
 }
 function prepare(){
  report.replaceChildren();document.body.classList.toggle('with-guidance-annex',check.checked);if(!check.checked)return;
  const filledRows=api.catalog().map(row=>({...row,instances:row.instances.filter(instance=>{const r=rows(instance.key)[instance.index];return ['S','N','A'].includes(r.a)||String(r.obs||'').trim().length>0;})})).filter(row=>row.instances.length);
  const notePages=[...new Set(Object.values(CFG.itens).map(c=>c.page))].filter(page=>String(S.notes?.[page]||'').trim());
  if(!filledRows.length&&!notePages.length){document.body.classList.toggle('with-guidance-annex',false);return;}
  api.reload();const intro=make('div');intro.className='annex-intro';intro.append(make('h1','Anexo dos F — Respostas e observações'),make('p',api.title+' · '+new Intl.DateTimeFormat('pt-BR',{dateStyle:'short',timeZone:'America/Sao_Paulo'}).format(new Date())));
  if(S.meta?.empresa)intro.appendChild(make('p','Estabelecimento: '+S.meta.empresa));if(S.meta?.data)intro.appendChild(make('p','Inspeção: '+S.meta.data));
  intro.appendChild(make('p','Somente linhas preenchidas. NC = criticidade; P = probabilidade; NC × P = peso. Pontos obtidos: peso das respostas Sim em unidades utilizadas. A linha na coluna de observações permite complemento manual.'));const blocks=[intro];
  // One complete requirement and source reference per group of units.
  for(const row of filledRows)for(let offset=0;offset<row.instances.length;offset+=8)blocks.push(articleFor(row,row.instances.slice(offset,offset+8)));
  for(const page of notePages){const note=make('section');note.className='annex-general-note';note.append(make('h3','Observações gerais — '+(PAGES[page]||'Página '+(page+1))),make('p',S.notes[page]));blocks.push(note);}
  paginate(blocks);
 }
 check.addEventListener('change',prepare);window.addEventListener('beforeprint',prepare);prepare();
})();
