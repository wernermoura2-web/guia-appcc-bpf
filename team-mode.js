/* Team menu: common inspection file, selective imports and local audit. */
(()=>{'use strict';if(!window.APPCC_TEAM)return;
const core=window.APPCC_TEAM_CORE,clone=x=>JSON.parse(JSON.stringify(x));
S.team=S.team||{};S.team.id=S.team.id||crypto.randomUUID();S.team.imports=S.team.imports||[];save();
const host=document.querySelector('.paper-workspace'),panel=document.createElement('section');
panel.className='card screen-only team-panel';panel.innerHTML='<h2>Trabalho em grupo — BPF/APPCC</h2><p>Compartilhe o mesmo JSON inicial. Cada fiscal preenche seus processos e envia o arquivo ao responsável pela consolidação.</p><div class="tools" id="team-tools"></div><p id="team-status" role="status"></p>';
host.prepend(panel);const toolsBox=panel.querySelector('.tools');
function button(label,fn){const b=document.createElement('button');b.type='button';b.textContent=label;b.onclick=fn;return b;}
const dialog=document.createElement('dialog');dialog.className='team-dialog';dialog.setAttribute('aria-label','Trabalho em equipe');document.body.append(dialog);
const importer=document.createElement('dialog');importer.className='team-dialog';importer.setAttribute('aria-label','Importar processos');document.body.append(importer);
const picker=document.createElement('input');picker.type='file';picker.accept='.json,application/json';picker.multiple=true;picker.hidden=true;document.body.append(picker);
function download(filename){save();const a=document.createElement('a'),url=URL.createObjectURL(new Blob([JSON.stringify({schema:'appcc-bpf-1',...S},null,2)],{type:'application/json'}));a.href=url;a.download=filename;a.click();setTimeout(()=>URL.revokeObjectURL(url),10000);}
function showTeam(){
 dialog.replaceChildren();const h=document.createElement('h2');h.textContent='Trabalho em equipe — BPF/APPCC';dialog.append(h);
 const code=document.createElement('p');code.textContent='Código comum: '+S.team.id;dialog.append(code);
 const list=document.createElement('ol');
 for(const text of ['Preencha Envasadora, Endereço e Data no guia.','Gere o arquivo inicial e envie o MESMO JSON a todos os integrantes.','Cada colega abre Trabalho em grupo e usa Abrir preenchimento para carregar esse JSON.','Você continua neste guia: gerar o JSON inicial não apaga seu trabalho.','Pessoa 1: captação, condução e reservatórios. Pessoa 2 (consolidação): controle de qualidade, responsáveis e dados gerais. Pessoa 3: recepção, higienização e envase. A equipe pode combinar outra divisão.','Cada colega usa Salvar arquivo e envia seu JSON ao responsável.','O responsável usa Importar processos e marca somente os processos recebidos. Pode selecionar vários JSONs de uma vez.','Depois completa fotos, rótulos, observações, medidas e responsáveis e salva o arquivo consolidado.']){const li=document.createElement('li');li.textContent=text;list.append(li);}dialog.append(list);
 const note=document.createElement('p');note.textContent='Abrir preenchimento restaura o guia inteiro. Importar processos substitui apenas os processos escolhidos. Não use Novo / limpar tudo depois de abrir o JSON inicial.';dialog.append(note);
 const actions=document.createElement('div');actions.className='tools';actions.append(button('Gerar arquivo inicial da equipe',()=>{if(!S.meta.empresa?.trim()||!S.meta.endereco?.trim()||!S.meta.data?.trim()){alert('Preencha envasadora, endereço e data antes de gerar o arquivo inicial.');return;}download('Guia_APPCC_Equipe_Inicial.json');}),button('Importar processos',()=>{dialog.close();picker.click();}),button('Fechar',()=>dialog.close()));dialog.append(actions);
 const heading=document.createElement('h3');heading.textContent='Arquivos incorporados';dialog.append(heading);
 if(!S.team.imports.length){const p=document.createElement('p');p.textContent='Nenhum arquivo incorporado.';dialog.append(p);}else{const ul=document.createElement('ul');for(const row of S.team.imports){const li=document.createElement('li');li.textContent=row.file+' — '+row.processes.map(p=>p==='gerais'?'Dados gerais':NAMES[p]).join(', ')+' — '+new Date(row.date).toLocaleString('pt-BR');ul.append(li);}dialog.append(ul);}
 const manual=document.createElement('a');manual.href='manual-equipe.html';manual.textContent='Ler manual da equipe';dialog.append(manual);dialog.showModal();
}
toolsBox.append(button('Trabalho em equipe',showTeam),button('Importar processos',()=>picker.click()));
const oldFiles=document.getElementById('paper-export').closest('.guide-control-group');
const saveButton=document.getElementById('paper-export');saveButton.textContent='Salvar arquivo';saveButton.onclick=()=>download('Guia_APPCC_Equipe.json');
const label=document.getElementById('paper-import').closest('label');label.firstChild.textContent='Abrir preenchimento';
const print=document.getElementById('paper-print');print.textContent='Imprimir / PDF';
const fresh=document.getElementById('paper-new');fresh.textContent='Novo / limpar tudo';fresh.onclick=()=>{if(confirm('Limpar o preenchimento do trabalho em grupo? Salve o JSON antes.')){localStorage.removeItem(KEY);location.reload();}};
toolsBox.append(saveButton,label,print,fresh);
if(oldFiles){panel.append(document.getElementById('saved'));oldFiles.remove();}
document.querySelector('header h1').textContent='Guia BPF/APPCC — Trabalho em grupo';
const fileInput=document.getElementById('paper-import'),originalOpen=fileInput.onchange;
fileInput.onchange=async event=>{const file=event.target.files?.[0];if(!file)return;try{const state=JSON.parse(await file.text());core.validate(state,CFG);if(!state.team?.id)throw Error('Use o JSON inicial gerado no menu Trabalho em equipe.');await originalOpen(event);}catch(e){alert(e.message);fileInput.value='';}};
async function checkpoint(state){return new Promise((resolve,reject)=>{const req=indexedDB.open('guia-appcc-equipe-importacoes-v1',1);req.onupgradeneeded=()=>req.result.createObjectStore('copies',{autoIncrement:true});req.onerror=()=>reject(Error('Não foi possível guardar a cópia anterior. A importação não foi aplicada.'));req.onsuccess=()=>{const db=req.result,tx=db.transaction('copies','readwrite'),store=tx.objectStore('copies');store.add({date:new Date().toISOString(),state:clone(state)});const keys=store.getAllKeys();keys.onsuccess=()=>keys.result.slice(0,-5).forEach(k=>store.delete(k));tx.oncomplete=()=>{db.close();resolve();};tx.onerror=()=>{db.close();reject(Error('Não foi possível guardar a cópia anterior. A importação não foi aplicada.'));};};});}
picker.onchange=async()=>{
 if(!picker.files.length)return;
 try{
  const files=await Promise.all([...picker.files].map(async file=>({name:file.name,state:JSON.parse(await file.text())})));
  for(const file of files){core.validate(file.state,CFG);if(file.state.team?.id!==S.team.id)throw Error('O arquivo '+file.name+' não pertence ao mesmo código de inspeção.');for(const key of ['empresa','endereco','data'])if(String(file.state.meta[key]||'').trim()!==String(S.meta[key]||'').trim())throw Error('Identificação diferente em '+file.name+'. Confira os dados do arquivo inicial.');file.state=migrateAdoptedClassification(migrateCurrentState(file.state));}
  importer.replaceChildren();const h=document.createElement('h2');h.textContent='Importar processos';importer.append(h);const intro=document.createElement('p');intro.textContent='Selecione os processos a incorporar de cada arquivo. Os processos selecionados serão substituídos por inteiro; os demais serão preservados.';importer.append(intro);
  const choices=[];
  for(const file of files){const fs=document.createElement('fieldset'),legend=document.createElement('legend');legend.textContent=file.name;fs.append(legend);
   for(const p of [...ORDER,'gerais']){const lab=document.createElement('label');lab.className='team-choice';const input=document.createElement('input');input.type='checkbox';input.value=p;const count=Object.entries(CFG.itens).filter(([k,c])=>c.proc===p).reduce((n,[k])=>n+Object.values(file.state.a[k]||{}).filter(a=>a.a).length,0);lab.append(input,document.createTextNode(p==='gerais'?'Dados gerais, observações, fotos, rótulos e responsáveis':NAMES[p]+' ('+count+' respostas)'));fs.append(lab);choices.push({input,file,process:p});}importer.append(fs);}
  const status=document.createElement('p');status.setAttribute('role','status');importer.append(status);const apply=button('Importar processos selecionados',async()=>{apply.disabled=true;try{const selected=choices.filter(c=>c.input.checked);if(!selected.length)throw Error('Selecione ao menos um processo.');const used=new Set();for(const row of selected){if(used.has(row.process))throw Error('O mesmo processo foi selecionado em mais de um arquivo. Escolha apenas uma origem por processo.');used.add(row.process);}
    let next=clone(S);for(const file of files){const ps=selected.filter(r=>r.file===file).map(r=>r.process);if(!ps.length)continue;next=core.merge(next,file.state,ps,CFG,PAPER);next.team.imports.push({file:file.name,date:new Date().toISOString(),processes:ps});}
    await checkpoint(S);localStorage.setItem(KEY,JSON.stringify(next));S=next;save();refreshPaper();importer.close();document.getElementById('team-status').textContent='Importação concluída: '+selected.length+' processo(s)/conjunto(s). Os demais foram preservados.';
   }catch(e){status.textContent=e.message;}finally{apply.disabled=false;}});
  const actions=document.createElement('div');actions.className='tools';actions.append(apply,button('Cancelar',()=>importer.close()));importer.append(actions);importer.showModal();
 }catch(e){alert(e.message);}finally{picker.value='';}
};
})();
