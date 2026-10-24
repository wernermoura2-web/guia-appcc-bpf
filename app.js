'use strict';
const KEY='guia-appcc-bpf-v1',PAGES={0:'Captação',1:'Condução',2:'Reservatórios — Captação 1',3:'Reservatórios — Captação 2',4:'Reservatórios — Captação 3',5:'Reservatórios — Captação 4',6:'Recepção de embalagens / insumos',7:'Higienização de retornáveis e tampas',8:'Higienização de descartáveis e tampas',9:'Envase de retornáveis',10:'Envase de descartáveis',11:'Controle de qualidade',12:'Responsabilidade e manipuladores'},NAMES={'4.1':'Captação','4.2':'Condução','4.3':'Reservatórios','4.5':'Recepção','4.6':'Higienização','4.7':'Envase','4.10':'Qualidade','4.11':'Responsabilidade'},ORDER=Object.keys(NAMES),CATS=['PPR','PPHO','PC','PPRO','PCC'];
let S={meta:{},a:{},units:{},names:{},notes:{}},current='4.1',editing=null;
try{const loaded=JSON.parse(localStorage.getItem(KEY));if(loaded&&loaded.a)S={...S,...loaded};}catch(e){}
// Migração das antigas subdivisões da captação, preservando respostas e observações.
const CONFIG_VERSION='captacao-soma-20261024';
function migrateState(state){
 if(state.configurationVersion===CONFIG_VERSION)return state;
 state.a=state.a||{};state.legacyCaptacao=state.legacyCaptacao||{};
 function merge(parts){const values=parts.filter(Boolean),out={};
  if(values.some(r=>r.a==='N'))out.a='N';else if(parts.every(r=>r&&r.a==='S'))out.a='S';
  const notes=values.map((r,i)=>r.obs?('Bloco anterior '+(i+1)+': '+r.obs):'').filter(Boolean);if(notes.length)out.obs=notes.join('\n');
  return out;
 }
 for(const [k,c] of Object.entries(CFG.itens)){
  if(c.proc!=='4.1'||!state.a[k])continue;
  const old=state.a[k];state.legacyCaptacao[k]=JSON.parse(JSON.stringify(old));let next=old;
  if(c.code==='4.1.2'&&old[2]!==undefined)next={0:merge([old[0],old[1]]),1:{...old[2]}};
  if(c.code==='4.1.3'&&old[2]!==undefined)next={0:{...old[0]},1:merge([old[1],old[2]])};
  state.a[k]=next;for(let i=0;i<c.frases.length;i++)if(next[i])next[i].cat=c.frases[i].cat;
 }
 state.configurationVersion=CONFIG_VERSION;return state;
}
const CONDUCTION_VERSION='conducao-ppro-ppho-20261024';
function migrateConductionState(state){
 if(state.conductionVersion===CONDUCTION_VERSION)return state;
 state.a=state.a||{};state.legacyConducao=state.legacyConducao||{};
 for(const [k,c] of Object.entries(CFG.itens)){
  if(c.proc!=='4.2'||!state.a[k])continue;
  state.legacyConducao[k]=JSON.parse(JSON.stringify(state.a[k]));
  for(let i=0;i<c.frases.length;i++)if(state.a[k][i])state.a[k][i].cat=c.frases[i].cat;
 }
 state.conductionVersion=CONDUCTION_VERSION;return state;
}
const RESERVOIR_VERSION='reservatorios-ppro-pc-ppho-20261024';
function migrateReservoirState(state){
 if(state.reservoirVersion===RESERVOIR_VERSION)return state;
 state.a=state.a||{};state.legacyReservatorios=state.legacyReservatorios||{};
 for(const [k,c] of Object.entries(CFG.itens)){
  if(c.proc!=='4.3'||!state.a[k])continue;
  state.legacyReservatorios[k]=JSON.parse(JSON.stringify(state.a[k]));
  for(let i=0;i<c.frases.length;i++)if(state.a[k][i])state.a[k][i].cat=c.frases[i].cat;
 }
 state.reservoirVersion=RESERVOIR_VERSION;return state;
}
function migrateInspectionState(state){
 state.a=state.a||{};
 if(state.reservoirSentencesVersion!=='4.3.3-tres-4.3.4-duas-20261024'){
  state.legacyFrasesReservatorios=state.legacyFrasesReservatorios||{};
  function merge(parts,cat){const out={cat};if(parts.some(r=>r&&r.a==='N'))out.a='N';else if(parts.every(r=>r&&r.a==='S'))out.a='S';const notes=parts.filter(Boolean).map(r=>r.obs||'').filter(Boolean);if(notes.length)out.obs=notes.join('\n');return out;}
  for(const[k,c]of Object.entries(CFG.itens)){
   const old=state.a[k];if(!old)continue;
   if(c.code==='4.3.3'&&(old[3]||old[4])){state.legacyFrasesReservatorios[k]=JSON.parse(JSON.stringify(old));state.a[k]={0:merge([old[0],old[1]],c.frases[0].cat),1:{...old[2],cat:c.frases[1].cat},2:merge([old[3],old[4]],c.frases[2].cat)};}
   if(c.code==='4.3.4'&&old[0]&&!old[1]){state.legacyFrasesReservatorios[k]=JSON.parse(JSON.stringify(old));state.a[k][1]={a:old[0].a,cat:old[0].cat||c.frases[1].cat};}
  }
  state.reservoirSentencesVersion='4.3.3-tres-4.3.4-duas-20261024';
 }
 for(const[k,rs]of Object.entries(state.a))for(const[i,r]of Object.entries(rs))if(r.cat&&!CATS.includes(r.cat)){state.legacyAPPCCLabels=state.legacyAPPCCLabels||{};state.legacyAPPCCLabels[k+'#'+i]=r.cat;delete r.cat;}
 return state;
}
function migratePOPConductionState(state){
 if(state.popConductionVersion==='pop-429-ordem-20261024')return state;
 state.a=state.a||{};state.legacyPOPConducao=state.legacyPOPConducao||{};
 for(const[k,c]of Object.entries(CFG.itens))if(c.code==='4.2.9'&&state.a[k]){const old=state.a[k];state.legacyPOPConducao[k]=JSON.parse(JSON.stringify(old));const next={};if(old[1])next[0]={...old[1]};if(old[0])next[1]={...old[0]};state.a[k]=next;}
 state.popConductionVersion='pop-429-ordem-20261024';return state;
}
function migrateCurrentState(state){return migrateResponsibilityState(migratePOPConductionState(migrateStateBeforePOP(state)));}
function migrateStateBeforePOP(state){return migrateInspectionState(migrateReservoirState(migrateConductionState(migrateState(state))));}

function migrateResponsibilityState(state){
 if(state.responsibilityVersion==='responsabilidade-ppho-ppro-20261024')return state;
 state.a=state.a||{};state.legacyResponsabilidade=state.legacyResponsabilidade||{};
 for(const[k,c]of Object.entries(CFG.itens))if(c.proc==='4.11'&&state.a[k]){
  state.legacyResponsabilidade[k]=JSON.parse(JSON.stringify(state.a[k]));
  for(let i=0;i<c.frases.length;i++)if(state.a[k][i])state.a[k][i].cat=c.frases[i].cat;
 }
 state.responsibilityVersion='responsabilidade-ppho-ppro-20261024';return state;
}
S=migrateCurrentState(S);
try{localStorage.setItem(KEY,JSON.stringify(S));}catch(e){}
const esc=v=>String(v??'').replace(/[&<>"']/g,x=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[x]));
function save(){try{localStorage.setItem(KEY,JSON.stringify(S));document.getElementById('saved').textContent='Salvo neste aparelho.';}catch(e){document.getElementById('saved').textContent='Não foi possível salvar neste aparelho. Use Salvar JSON.';}}
function rows(k){const c=CFG.itens[k];return c.frases.map((f,i)=>({...f,...(S.a[k]?.[i]||{}),texto:f.texto,codigo:'F'+(i+1)}));}
function score(k){
 const c=CFG.itens[k],rr=rows(k);if(S.units['p'+c.page+'c'+c.col]===false)return {active:false,earned:0,maximum:0,w:0};
 const applicable=rr.filter(r=>r.a!=='A'),earned=applicable.filter(r=>r.a==='S').reduce((sum,r)=>sum+CFG.pesos[r.cat]*r.P,0),maximum=applicable.reduce((sum,r)=>sum+CFG.pesos[r.cat]*r.P,0);
 const cats=[...new Set(applicable.map(r=>r.cat))],nc=[...new Set(applicable.map(r=>CFG.pesos[r.cat]))],ps=[...new Set(applicable.map(r=>r.P))];
 return {active:true,pending:rr.some(r=>!r.a),a:!applicable.length?'A':applicable.some(r=>r.a==='N')?'N':rr.some(r=>!r.a)?undefined:'S',earned,maximum,w:earned,cat:cats.join('/'),nc:nc.join('/'),p:ps.join('/')};
}
function consolidate(ss){
 const active=ss.filter(x=>x.active);if(!active.length)return {active:false,earned:0,maximum:0,w:0};
 const earned=active.reduce((sum,x)=>sum+x.earned,0),maximum=active.reduce((sum,x)=>sum+x.maximum,0),pending=active.some(x=>x.pending);
 return {active:true,pending,a:pending?undefined:!maximum?'A':active.some(x=>x.a==='N')?'N':'S',earned,maximum,w:earned};
}
function attendance(ss){const z=consolidate(ss);return !z.active||z.pending||!z.maximum?null:100*z.earned/z.maximum;}
function risk(v){return v===null?null:v>=76?1:v>50?2:3;}
function badge(v){let r=risk(v);return r?'<span class="'+['','low','med','high'][r]+'">'+v.toLocaleString('pt-BR',{maximumFractionDigits:2})+'% · '+['','Baixo','Médio','Alto'][r]+'</span>':'<span class="pending">Pendente / não avaliado</span>';}
function pageResult(page,col){return attendance(Object.keys(CFG.itens).filter(k=>CFG.itens[k].page===page&&(col===undefined||CFG.itens[k].col===col)).map(score));}
function processResult(proc){return attendance(Object.keys(CFG.itens).filter(k=>CFG.itens[k].proc===proc).map(score));}
function answerButtons(k,i,disabled=false){let c=CFG.itens[k],r=rows(k)[i],choices=['S','N',...(c.allowNA?['A']:[])];return '<div class="answers">'+choices.map(a=>'<button type="button" class="answer '+(r.a===a?'selected':'')+'" aria-pressed="'+(r.a===a)+'" '+(disabled?'disabled':'')+' onclick="answer(\''+k+'\','+i+',\''+a+'\')">'+({S:'Sim',N:'Não',A:'N/A'}[a])+'</button>').join('')+'</div>';}
function answer(k,i,a){let c=CFG.itens[k];if(a==='A'&&!c.allowNA)return;if(!S.a[k])S.a[k]={};S.a[k][i]={...(S.a[k][i]||{}),a};save();if(editing)renderPhrases();else if(window.APPCC_PAPER)refreshPaper();else render();}
function editField(k,i,name,value){if(!S.a[k])S.a[k]={};S.a[k][i]={...(S.a[k][i]||{}),[name]:value};save();if(name==='cat'){if(editing)renderPhrases();else if(window.APPCC_PAPER)refreshPaper();else render();}}
function unitName(page,col){return page>=2&&page<=5?'Reservatório '+col:page===6?['Retornáveis','Descartáveis','Rótulos','Saneantes'][col-1]:page===7||page===8?(col===4?'Tampas':'Linha '+col):page===9||page===10?'Linha '+col:page>=11?'Avaliação':'Captação '+col;}
function render(){document.getElementById('nav').innerHTML=ORDER.map(p=>'<button class="'+(p===current?'active':'')+'" onclick="current=\''+p+'\';render()">'+p+' '+NAMES[p]+'</button>').join('');let global=ORDER.map(processResult),known=global.filter(x=>x!==null);document.getElementById('global').textContent='Classificação do estabelecimento: '+(global.some(x=>x===null)?'Pendente':'Grupo '+Math.max(...known.map(risk)));let html='<section class="card"><h2>'+current+' · '+NAMES[current]+'</h2>'+badge(processResult(current))+'</section>';let pages=[...new Set(Object.values(CFG.itens).filter(c=>c.proc===current).map(c=>c.page))];for(let pg of pages){let keys=Object.keys(CFG.itens).filter(k=>CFG.itens[k].page===pg),cols=[...new Set(keys.map(k=>CFG.itens[k].col))],codes=[...new Set(keys.map(k=>CFG.itens[k].code))];html+='<section class="card"><h3>'+PAGES[pg]+'</h3><div class="scroll"><table><thead><tr><th>Item</th>'+cols.map(col=>'<th>'+unitName(pg,col)+(pg<11?'<label><input type="checkbox" '+(S.units['p'+pg+'c'+col]!==false?'checked':'')+' onchange="S.units[\'p'+pg+'c'+col+'\']=this.checked;save();render()"> Avaliada</label>':'')+(pg<6?'<input aria-label="Nome da captação '+col+'" value="'+esc(S.names[pg>=2&&pg<=5?pg-1:col]||'')+'" onchange="S.names['+(pg>=2&&pg<=5?pg-1:col)+']=this.value;save()">':'')+'</th>').join('')+'<th>Resultado</th></tr></thead><tbody>';for(let code of codes){let kk=keys.filter(k=>CFG.itens[k].code===code);html+='<tr><th>'+code+'<div class="item-description">'+CFG.itens[kk[0]].frases.map((f,i)=>'<p><strong>F'+(i+1)+'</strong> - '+esc(f.texto)+'</p>').join('')+'</div></th>';for(let col of cols){let k=kk.find(k=>CFG.itens[k].col===col);if(!k){html+='<td>Não aplicável</td>';continue;}let c=CFG.itens[k],z=score(k);html+='<td><span class="weight">'+(z.active?'Σ Sim: '+z.earned+' / '+z.maximum:'Não avaliada')+'</span>'+(c.frases.length>1?'<span>'+({S:'Sim',N:'Não',A:'N/A'}[z.a]||'Pendente')+'</span> <button class="answer" onclick="openPhrases(\''+k+'\')">F</button>':singleCell(k))+'</td>';}let z=consolidate(kk.map(score));html+='<td>'+({S:'Sim',N:'Não',A:'N/A'}[z.a]||'Pendente')+(z.active?' · Σ Sim: '+z.earned+' / '+z.maximum:'')+'</td></tr>';}html+='<tr><th>Índice (%) / risco</th>'+cols.map(col=>'<td>'+badge(pageResult(pg,col))+'</td>').join('')+'<td>'+badge(pageResult(pg))+'</td></tr></tbody></table></div><h3>Observações gerais</h3><textarea aria-label="Observações gerais" onchange="S.notes['+pg+']=this.value;save()">'+esc(S.notes[pg]||'')+'</textarea><div class="notes">'+esc(keys.flatMap(k=>rows(k).filter(r=>r.obs||r.a==='N').map(r=>(r.a==='N'?'NC ':'')+r.codigo+' | '+CFG.itens[k].code+' · '+unitName(pg,CFG.itens[k].col)+(r.obs?': '+r.obs:''))).join('\n\n'))+'</div></section>'; }html+='<section class="card"><h3>Matriz dos oito processos</h3><table><tr><th>Processo</th><th>Resultado</th></tr>'+ORDER.map(p=>'<tr><td>'+NAMES[p]+'</td><td>'+badge(processResult(p))+'</td></tr>').join('')+'</table></section>';document.getElementById('main').innerHTML=html;}
function openPhrases(k){editing=k;renderPhrases();document.getElementById('phrases').showModal();}
function renderPhrases(){let c=CFG.itens[editing];document.getElementById('phrase-title').textContent='Item '+c.code+' · '+unitName(c.page,c.col);document.getElementById('phrase-body').innerHTML=rows(editing).map((r,i)=>'<section class="phrase"><strong>'+r.codigo+' - '+esc(r.texto)+'</strong><div class="fields"><label>APPCC<select onchange="editField(\''+editing+'\','+i+',\'cat\',this.value)">'+CATS.map(cat=>'<option '+(cat===r.cat?'selected':'')+'>'+cat+'</option>').join('')+'</select></label><span>NC '+CFG.pesos[r.cat]+' × P '+r.P+' = '+(CFG.pesos[r.cat]*r.P)+'</span></div>'+answerButtons(editing,i)+'<label>Observação<textarea oninput="editField(\''+editing+'\','+i+',\'obs\',this.value)">'+esc(r.obs||'')+'</textarea></label></section>').join('');}
function initInteractive(){const scale=document.getElementById('nc-scale');if(scale)scale.textContent='NC: '+CATS.map(cat=>cat+' '+CFG.pesos[cat]).join(' · ')+'. Captação: denominador dinâmico conforme o APPCC de cada frase; 57 na configuração inicial. Índice = Σ(NC × P das frases Sim) ÷ Σ(NC × P das frases aplicáveis) × 100. Baixo ≥76%; médio >50% e <76%; alto ≤50%.';document.getElementById('back').onclick=()=>document.getElementById('phrases').close();document.getElementById('phrases').onclose=()=>{editing=null;render();};document.querySelectorAll('[data-meta]').forEach(el=>{el.value=S.meta[el.dataset.meta]||'';el.oninput=()=>{S.meta[el.dataset.meta]=el.value;save();};});document.getElementById('export').onclick=()=>{let url=URL.createObjectURL(new Blob([JSON.stringify({schema:'appcc-bpf-1',...S},null,2)],{type:'application/json'})),a=document.createElement('a');a.href=url;a.download='Guia_APPCC_BPF.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};document.getElementById('import').onchange=async e=>{try{let s=migrateCurrentState(JSON.parse(await e.target.files[0].text()));if(s.schema!=='appcc-bpf-1'||!s.a||!s.meta)throw Error('Formato incompatível com este guia.');for(let [k,rs] of Object.entries(s.a)){if(!CFG.itens[k])throw Error('Item desconhecido');for(let [i,r] of Object.entries(rs)){if(!CFG.itens[k].frases[i]||(r.a&&!['S','N','A'].includes(r.a))||(r.cat&&!CATS.includes(r.cat))||(r.a==='A'&&!CFG.itens[k].allowNA))throw Error('Resposta inválida');if(r.P!==undefined)throw Error('Probabilidade não pode ser alterada pelo arquivo');}}if(!confirm('Substituir o preenchimento atual pelo arquivo?'))return;S={meta:{},a:{},units:{},names:{},notes:{},...s};save();location.reload();}catch(err){alert(err.message);}};document.getElementById('reset').onclick=()=>{if(confirm('Limpar o preenchimento deste guia? Salve seu JSON antes.')){localStorage.removeItem(KEY);location.reload();}};render();
}
if(!window.APPCC_PAPER)initInteractive();
function printGuide(){save();let w=window.open('./html.appcc.pdf.html?print=1','_blank');if(!w)location.href='./html.appcc.pdf.html?print=1';}

function singleCell(k){let r=rows(k)[0];return '<strong>'+r.codigo+' - '+esc(r.texto)+'</strong><label>APPCC<select onchange="editField(\''+k+'\',0,\'cat\',this.value)">'+CATS.map(cat=>'<option '+(cat===r.cat?'selected':'')+'>'+cat+'</option>').join('')+'</select></label><span class="weight">NC '+CFG.pesos[r.cat]+' × P '+r.P+' = '+CFG.pesos[r.cat]*r.P+'</span>'+answerButtons(k,0)+'<textarea aria-label="Observação do item" onchange="editField(\''+k+'\',0,\'obs\',this.value)">'+esc(r.obs||'')+'</textarea>';}


