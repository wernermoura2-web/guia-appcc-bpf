/* Separate the two guides without deleting any existing answers or backups. */
(()=>{'use strict';
const original='guia-appcc-bpf-v1',revision='guia-appcc-revisao-legislativa-v1';
try{
 const raw=localStorage.getItem(original);if(!raw)return;
 const state=JSON.parse(raw);
 if(!state?.indicatorVersion?.startsWith('legislacao-indicadores-'))return;
 if(!localStorage.getItem(revision))localStorage.setItem(revision,raw);
 if(document.currentScript?.dataset.guide!=='original')return;
 const restored={...state,a:state.legacyBeforeIndicators?.answers||{}};
 delete restored.indicatorVersion;
 if(state.legacyBeforeIndicators?.configurationVersion)restored.configurationVersion=state.legacyBeforeIndicators.configurationVersion;
 localStorage.setItem('guia-appcc-legislativa-antes-separacao',raw);
 localStorage.setItem(original,JSON.stringify(restored));
}catch(error){console.warn('O preenchimento anterior foi preservado.',error);}
})();
