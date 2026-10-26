(()=>{'use strict';
 const api=window.InspectorOrientations,button=document.getElementById('paper-print');if(!api||!button)return;
 const make=(tag,text)=>{const el=document.createElement(tag);if(text!==undefined)el.textContent=text;return el;};
 const label=make('label'),check=make('input');check.type='checkbox';check.id='paper-include-guidance';check.checked=new URLSearchParams(location.search).get('anexos')==='1';label.className='screen-only guidance-print-option';label.append(check,document.createTextNode('Incluir páginas dos F como anexo (requisitos e orientações aos inspetores)'));button.closest('.tools').after(label);
 const report=make('section');report.id='guidance-annex';report.setAttribute('aria-label','Anexo dos F — orientações aos inspetores');document.body.appendChild(report);
 function prepare(){
  report.replaceChildren();document.body.classList.toggle('with-guidance-annex',check.checked);if(!check.checked)return;
  api.reload();report.append(make('h1','Anexo dos F — Orientações aos inspetores'),make('p',api.title+' · Textos vigentes neste aparelho · '+new Intl.DateTimeFormat('pt-BR',{dateStyle:'short',timeZone:'America/Sao_Paulo'}).format(new Date())));
  let proc=null,section;for(const row of api.catalog()){
   if(proc!==row.proc){section=make('section');section.className='annex-process';section.appendChild(make('h2',row.process));report.appendChild(section);proc=row.proc;}
   const item=make('article');item.className='annex-row';item.append(make('h3',(api.guide==='original'?'Item ':'Indicador ')+row.code+' · '+row.phraseLabels.join(' / ')),make('p',row.requirement));
   const text=make('p'),strong=make('strong','Orientação ao inspetor: ');text.append(strong,document.createTextNode(api.value(row.id)||'Orientação não preenchida.'));item.appendChild(text);
   if(row.references.length){const refs=make('p','Referência normativa: '+row.references.join(' · '));refs.className='annex-reference';item.appendChild(refs);}section.appendChild(item);
  }
 }
 check.addEventListener('change',prepare);window.addEventListener('beforeprint',prepare);prepare();
})();
