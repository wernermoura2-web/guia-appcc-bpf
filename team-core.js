/* Pure process merge used by the team guide. */
(function(root){'use strict';
const clone=x=>JSON.parse(JSON.stringify(x));
function validate(state,cfg){
 if(!state||state.schema!=='appcc-bpf-1'||!state.a||typeof state.a!=='object'||!state.meta)throw Error('Arquivo incompatível com o guia BPF/APPCC.');
 for(const [key,answers]of Object.entries(state.a)){const c=cfg.itens[key];if(!c)throw Error('O arquivo contém item desconhecido: '+key);for(const [i,r]of Object.entries(answers)){if(!c.frases[i]||!r||r.a&&!['S','N','A'].includes(r.a)||r.a==='A'&&!(c.frases[i].allowNA===undefined?c.allowNA:c.frases[i].allowNA))throw Error('Resposta inválida no item '+c.code);}}
 return true;
}
function merge(target,source,selected,cfg,paper){
 validate(source,cfg);
 if(!target.team?.id||source.team?.id!==target.team.id)throw Error('Código de inspeção diferente. Todos devem abrir o mesmo JSON inicial da equipe.');
 for(const key of ['empresa','endereco','data'])if(String(target.meta?.[key]||'').trim()!==String(source.meta?.[key]||'').trim())throw Error('Envasadora, endereço ou data diferentes do arquivo inicial. Confira a identificação antes de importar.');
 const known=new Set(Object.values(cfg.itens).map(c=>c.proc));if(!selected.length||selected.some(p=>p!=='gerais'&&!known.has(p)))throw Error('Selecione processos válidos.');
 const out=clone(target),pages=new Set(),keys=new Set(),units=new Set();
 for(const [key,c]of Object.entries(cfg.itens))if(selected.includes(c.proc)){keys.add(key);pages.add(c.page);units.add('p'+c.page+'c'+c.col);}
 if(selected.includes('gerais'))for(let p=13;p<paper.length;p++)pages.add(p);
 out.a=out.a||{};out.units=out.units||{};out.notes=out.notes||{};out.fields=out.fields||{};out.images=out.images||{};
 for(const key of keys){delete out.a[key];if(source.a[key])out.a[key]=clone(source.a[key]);if(out.appccOverrides)delete out.appccOverrides[key];if(source.appccOverrides?.[key]){out.appccOverrides=out.appccOverrides||{};out.appccOverrides[key]=clone(source.appccOverrides[key]);}}
 for(const u of units){delete out.units[u];if(source.units&&Object.hasOwn(source.units,u))out.units[u]=source.units[u];}
 for(const p of pages){delete out.notes[p];if(source.notes&&Object.hasOwn(source.notes,p))out.notes[p]=source.notes[p];}
 const fieldNames=new Set([...pages].flatMap(p=>paper[p].fields.map(f=>f.n)));
 for(const name of fieldNames){if(['envasadora','endereco','data'].includes(name))continue;delete out.fields[name];delete out.images[name];if(source.fields&&Object.hasOwn(source.fields,name))out.fields[name]=clone(source.fields[name]);if(source.images&&Object.hasOwn(source.images,name))out.images[name]=source.images[name];}
 if(selected.includes('4.1'))out.names=clone(source.names||{});
 if(selected.includes('gerais')){if(source.inspectors)out.inspectors=clone(source.inspectors);if(source.documentChecklist)out.documentChecklist=clone(source.documentChecklist);if(source.pccFinalGenerated)out.pccFinalGenerated=clone(source.pccFinalGenerated);}
 return out;
}
const api={validate,merge};if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.APPCC_TEAM_CORE=api;
})(typeof window==='undefined'?globalThis:window);
