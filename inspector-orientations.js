/* Per-guide edits of inspection guidance. Requirements and answers stay separate. */
(()=>{'use strict';
 if(typeof CFG==='undefined')return;
 const guide=Object.values(CFG.itens).some(c=>String(c.code).includes('.'))?'original':'revision';
 const storageKey='guia-appcc-'+guide+'-orientacoes-v1',backupKey=storageKey+'-recuperacao';
 const schema='orientacoes-inspetor-v1',names={'4.1':'Captação','4.2':'Condução','4.3':'Reservatórios','4.5':'Recepção de embalagens e insumos','4.6':'Higienização de embalagens e tampas','4.7':'Envase e fechamento','4.10':'Controle de qualidade','4.11':'Responsáveis e manipuladores'};
 const idFor=(c,i)=>JSON.stringify([String(c.proc),String(c.code),c.frases[i].texto]);
 const byId=new Map();
 for(const [key,c]of Object.entries(CFG.itens))c.frases.forEach((f,i)=>{
  const id=idFor(c,i);let row=byId.get(id);
  if(!row){row={id,proc:c.proc,process:names[c.proc]||c.proc,code:String(c.code),title:c.title||'',requirement:f.texto,base:f.orientacao||'',page:c.page,index:i,phraseLabels:[],references:[],sourceTexts:[],instances:[]};byId.set(id,row);}
  if(!row.phraseLabels.includes('F'+(i+1)))row.phraseLabels.push('F'+(i+1));
  if(f.ref&&!row.references.includes(f.ref))row.references.push(f.ref);
  if(f.sourceTexto&&!row.sourceTexts.includes(f.sourceTexto))row.sourceTexts.push(f.sourceTexto);
  row.instances.push({key,index:i});
 });
 const catalog=[...byId.values()].sort((a,b)=>a.page-b.page||a.code.localeCompare(b.code,'pt-BR',{numeric:true})||a.index-b.index);
 const empty=()=>({schema,guide,updatedAt:null,overrides:{}});
 function validate(data){
  if(!data||data.schema!==schema||data.guide!==guide||!data.overrides||typeof data.overrides!=='object'||Array.isArray(data.overrides))throw Error('Esta cópia não pertence às orientações deste guia.');
  const overrides=Object.create(null);
  for(const [id,value]of Object.entries(data.overrides)){if(typeof value!=='string')throw Error('Há uma orientação inválida nesta cópia.');overrides[id]=value;}
  return {schema,guide,updatedAt:typeof data.updatedAt==='string'?data.updatedAt:null,overrides};
 }
 function read(key){try{const raw=localStorage.getItem(key);return raw?validate(JSON.parse(raw)):null;}catch{return null;}}
 let state=read(storageKey)||empty();
 const own=(object,key)=>Object.prototype.hasOwnProperty.call(object,key);
 function emit(){if(typeof window.dispatchEvent==='function'&&typeof Event==='function')window.dispatchEvent(new Event('inspector-orientations-change'));}
 function write(overrides){const next={schema,guide,updatedAt:new Date().toISOString(),overrides};localStorage.setItem(storageKey,JSON.stringify(next));state=next;emit();return next;}
 function backup(){localStorage.setItem(backupKey,JSON.stringify(state));}
 function value(id){const row=byId.get(id);return own(state.overrides,id)?state.overrides[id]:(row?.base||'');}
 const api={guide,storageKey,title:guide==='original'?'Guia original':'Guia de revisão',catalog:()=>catalog,
  get:(c,i)=>value(idFor(c,i)),value,
  changed:id=>own(state.overrides,id),count:()=>catalog.filter(r=>own(state.overrides,r.id)).length,
  set(id,text){if(!byId.has(id)||typeof text!=='string')throw Error('Orientação não encontrada.');const next={...state.overrides};if(text===byId.get(id).base)delete next[id];else next[id]=text;return write(next);},
  restore(id){if(!byId.has(id))throw Error('Orientação não encontrada.');backup();const next={...state.overrides};delete next[id];return write(next);},
  restoreAll(){backup();return write({});},hasRecovery:()=>!!read(backupKey),
  undoRecovery(){const previous=read(backupKey);if(!previous)throw Error('Não há recuperação para desfazer.');write(previous.overrides);localStorage.removeItem(backupKey);emit();},
  snapshot:()=>JSON.parse(JSON.stringify(state)),
  importData(data){const valid=validate(data);backup();return write(valid.overrides);},
  reload(){state=read(storageKey)||empty();emit();}
 };
 window.InspectorOrientations=api;
 window.addEventListener?.('storage',e=>{if(e.key===storageKey||e.key===null){state=read(storageKey)||empty();emit();}});
 window.addEventListener?.('pageshow',()=>{state=read(storageKey)||empty();});
})();
