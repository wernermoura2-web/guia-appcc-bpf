(()=>{'use strict';
 const api=window.InspectorOrientations,button=document.getElementById('paper-print');if(!api||!button)return;
 const make=(tag,text)=>{const el=document.createElement(tag);if(text!==undefined)el.textContent=text;return el;};
 const label=make('label'),check=make('input');check.type='checkbox';check.id='paper-include-guidance';check.checked=new URLSearchParams(location.search).get('anexos')==='1';label.className='screen-only guidance-print-option';label.append(check,document.createTextNode('Incluir páginas dos F como anexo (somente linhas preenchidas)'));button.closest('.tools').after(label);
 const report=make('section');report.id='guidance-annex';report.setAttribute('aria-label','Anexo dos F — orientações aos inspetores');document.body.appendChild(report);
 function prepare(){
  report.replaceChildren();document.body.classList.toggle('with-guidance-annex',check.checked);if(!check.checked)return;
  const filledRows=api.catalog().map(row=>({...row,instances:row.instances.filter(instance=>{const r=rows(instance.key)[instance.index];return ['S','N','A'].includes(r.a)||String(r.obs||'').trim().length>0;})})).filter(row=>row.instances.length);
  const notePages=[...new Set(Object.values(CFG.itens).map(c=>c.page))].filter(page=>String(S.notes?.[page]||'').trim());
  if(!filledRows.length&&!notePages.length){document.body.classList.toggle('with-guidance-annex',false);return;}
  api.reload();report.append(make('h1','Anexo dos F — Orientações aos inspetores'),make('p',api.title+' · Textos vigentes neste aparelho · '+new Intl.DateTimeFormat('pt-BR',{dateStyle:'short',timeZone:'America/Sao_Paulo'}).format(new Date())));
  if(S.meta?.empresa)report.appendChild(make('p','Estabelecimento: '+S.meta.empresa));
  if(S.meta?.data)report.appendChild(make('p','Data da inspeção: '+S.meta.data));
  report.appendChild(make('p','Somente linhas com resposta marcada ou observação escrita. Sim, Não e NA indicam a resposta registrada. NC = criticidade; P = probabilidade; NC × P = peso; pontos obtidos = peso das respostas Sim em unidades utilizadas. Os espaços em branco permitem complementação manual.'));
  let proc=null,section;for(const row of filledRows){
   if(proc!==row.proc){section=make('section');section.className='annex-process';section.appendChild(make('h2',row.process));report.appendChild(section);proc=row.proc;}
   const item=make('article');item.className='annex-row';item.append(make('h3',(api.guide==='original'?'Item ':'Indicador ')+row.code+' · '+row.phraseLabels.join(' / ')),make('p',row.requirement));
   const text=make('p'),strong=make('strong','Orientação ao inspetor: ');text.append(strong,document.createTextNode(api.value(row.id)||'Orientação não preenchida.'));item.appendChild(text);
   if(row.references.length){const refs=make('p','Referência normativa: '+row.references.join(' · '));refs.className='annex-reference';item.appendChild(refs);}
   for(const instance of row.instances){
    const c=CFG.itens[instance.key],r=rows(instance.key)[instance.index],active=S.units['p'+c.page+'c'+c.col]!==false;
    const block=make('section');block.className='annex-evaluation';block.dataset.key=instance.key;block.dataset.index=instance.index;
    let unit=unitName(c.page,c.col);if(c.page<=1&&S.names?.[c.col])unit+=' — '+S.names[c.col];if(c.page>=2&&c.page<=5)unit+=' · Captação '+(c.page-1)+(S.names?.[c.page-1]?' — '+S.names[c.page-1]:'');
    block.appendChild(make('h4',(api.guide==='original'?'Item ':'Indicador ')+c.code+' · '+unit+' · F'+(instance.index+1)+(active?'':' · Unidade não utilizada')));
    const table=make('table');table.className='annex-metrics';const head=make('thead'),body=make('tbody'),headers=make('tr'),values=make('tr');
    const allowed=c.frases[instance.index].allowNA??c.allowNA,nc=CFG.pesos[r.cat],weight=nc*r.P;
    const answers=['S','N',...(allowed||r.a==='A'?['A']:[])].map(a=>(r.a===a?'☒ ':'☐ ')+({S:'Sim',N:'Não',A:'NA'}[a])).join('   ');
    for(const [title,value]of [['Resposta',answers],['APPCC',r.cat],['NC',nc],['P',r.P],['NC × P',weight],['Pontos obtidos',active&&r.a==='S'?weight:0]]){headers.appendChild(make('th',title));values.appendChild(make('td',String(value??'')));}
    head.appendChild(headers);body.appendChild(values);table.append(head,body);block.appendChild(table);
    const obs=make('div');obs.className='annex-observation';obs.append(make('strong','Observações da frase: '),make('p',r.obs||'Sem observações registradas.'));block.appendChild(obs);
    const manual=make('div');manual.className='annex-manual';manual.appendChild(make('span','Anotações / complemento manual:'));for(let i=0;i<2;i++){const line=make('div');line.className='annex-write-line';manual.appendChild(line);}block.appendChild(manual);item.appendChild(block);
   }
   section.appendChild(item);
  }
  for(const page of notePages){if(!S.notes?.[page])continue;const note=make('section');note.className='annex-general-note';note.append(make('h2','Observações gerais — '+(PAGES[page]||'Página '+(page+1))),make('p',S.notes[page]));report.appendChild(note);}
 }
 check.addEventListener('change',prepare);window.addEventListener('beforeprint',prepare);prepare();
})();
