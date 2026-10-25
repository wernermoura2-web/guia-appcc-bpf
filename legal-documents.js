/* A legal document can only be evaluated after it has been delivered. */
window.LegalDocuments=(()=>{
 'use strict';
 const answer=/^doc_legal_(\d+)_atende$/;
 function delivered(fields,name){
  const match=name.match(answer);
  return !match||String(fields['doc_legal_'+match[1]+'_situacao']||'').trim().toLowerCase()==='entregue';
 }
 function clean(fields){
  let changed=false;
  for(let i=1;i<=8;i++){
   const name='doc_legal_'+i+'_atende';
   if(!delivered(fields,name)&&fields[name]){delete fields[name];changed=true;}
  }
  return changed;
 }
 return {isAnswer:name=>answer.test(name),allowed:delivered,clean};
})();
