/* Group inspection controls without changing assessment or print contents. */
(()=>{
 const host=document.querySelector('.paper-workspace'),card=host?.querySelector('.card.screen-only');
 if(!card)return;
 const old=[...card.children],oldIds=new Map([...card.querySelectorAll('[id]')].map(el=>[el.id,el])),pick=id=>document.getElementById(id)||oldIds.get(id);
 card.classList.add('guide-controls');
 card.replaceChildren();
 const intro=document.createElement('div');intro.className='guide-intro';
 intro.innerHTML='<div><h2>Preencher inspeção</h2><p>Identifique a envasadora, escolha o processo e responda aos itens pelo botão F.</p></div><a href="index.html">← Menu do guia</a>';card.append(intro);
 if(!window.APPCC_TEAM){const teamTools=document.createElement('div');teamTools.className='tools';teamTools.setAttribute('aria-label','Trabalho em grupo');const link=document.createElement('a');link.href='equipe.html';link.className='button';link.textContent='Trabalho em grupo';teamTools.append(link);const help=document.createElement('span');help.className='muted';help.textContent='Abrir o menu da equipe para compartilhar o JSON e reunir os processos da inspeção.';teamTools.append(help);card.append(teamTools);}
 function group(title,text){const section=document.createElement('section');section.className='guide-control-group';const h=document.createElement('h3');h.textContent=title;section.append(h);if(text){const p=document.createElement('p');p.className='muted';p.textContent=text;section.append(p);}card.append(section);return section;}
 function tools(section){const t=document.createElement('div');t.className='tools';section.append(t);return t;}
 const identity=group('1. Dados da inspeção'),grid=document.createElement('div');grid.className='guide-identity-grid';identity.append(grid);
 const inputs={};
 for(const [key,title,type]of [['empresa','Envasadora','text'],['endereco','Endereço','text'],['data','Data da inspeção','date']]){
  const label=document.createElement('label');label.textContent=title;
  const input=document.createElement('input');input.type=type;input.setAttribute('aria-label',title);inputs[key]=input;
  label.append(input);grid.append(label);
  input.addEventListener('input',()=>{S.meta[key]=key==='data'?inspectionDateText(input.value):input.value;save();refreshPaper();});
 }
 const idTools=tools(identity);
 for(const node of old.flatMap(el=>[...el.querySelectorAll('button')]).filter(el=>/Cadastrar/.test(el.textContent)))idTools.append(node);
 const clear=document.createElement('button');clear.type='button';clear.textContent='Limpar envasadora, endereço e data';clear.className='guide-secondary';
 clear.onclick=()=>{for(const key of ['empresa','endereco','data'])S.meta[key]='';for(const key of ['envasadora','endereco','data'])delete S.fields[key];save();refreshPaper();pick('guide-identification-status').textContent='Envasadora, endereço e data limpos.';};idTools.append(clear);
 const notice=document.createElement('p');notice.id='guide-identification-status';notice.className='muted';notice.setAttribute('role','status');identity.append(notice);
 const fill=group('2. Avaliação dos processos');fill.append(pick('paper-risk'));
 const hint=document.createElement('p');hint.textContent='Use F para consultar frases, orientações e fundamentos e registrar as respostas. Uma resposta Não torna o item Não; Sim exige todas as frases aplicáveis atendidas.';fill.append(hint);
 const finalButton=old.flatMap(el=>[...el.querySelectorAll('button')]).find(el=>/Revisar considerações/.test(el.textContent));if(finalButton)tools(fill).append(finalButton);
 const output=group('3. Impressão'),outTools=tools(output);
 for(const el of old.flatMap(el=>[...el.querySelectorAll('a,button')]).filter(el=>el.id==='paper-print'||el.hasAttribute('download')))outTools.append(el);
 for(const el of old.filter(el=>el.classList.contains('doc-append-toggle')||el.querySelector('#include-document-checklist')||el.querySelector('#include-guidance-annex')))output.append(el);
 // The guidance script may use a different identifier; retain its labelled toggle.
 for(const el of old.filter(el=>el.classList.contains('guidance-print-option')))if(!card.contains(el))output.append(el);
 const files=group('4. Salvar ou retomar preenchimento'),fileTools=tools(files);
 for(const id of ['paper-export','paper-new'])fileTools.append(pick(id));
 const importLabel=pick('paper-import').closest('label');fileTools.insertBefore(importLabel,pick('paper-new'));files.append(pick('saved'));
 const advanced=document.createElement('details');advanced.className='guide-advanced';advanced.innerHTML='<summary>Configurações de BPF/APPCC e critérios de cálculo</summary>';card.append(advanced);
 const advancedTools=tools(advanced);advancedTools.append(pick('appcc-edit-mode'),pick('appcc-restore'));
 advanced.append(pick('appcc-mode-status'));
 const explanation=document.createElement('p');explanation.className='muted';explanation.textContent='Atendimento = itens Sim ÷ itens aplicáveis × 100. Sim vale 1, Não vale 0 e NA fica fora da conta. BPF/APPCC, NC, P e pontos são informativos e não alteram a média oficial.';advanced.append(explanation);
 card.append(pick('paper-status'));
 const backup=host.querySelector('.backup-panel');if(backup){const details=document.createElement('details');details.className='card screen-only guide-backups';details.innerHTML='<summary>Cópias de segurança automáticas</summary>';backup.before(details);details.append(backup);backup.classList.remove('card');}
 function sync(){for(const [key,input]of Object.entries(inputs))if(document.activeElement!==input)input.value=key==='data'?inspectionDateISO(S.meta.data):S.meta[key]||'';}
 const refresh=refreshPaper;refreshPaper=function(){const result=refresh.apply(this,arguments);sync();return result;};sync();
})();
