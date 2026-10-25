/* Shared by the browser forms and Acrobat. Preserve manually revised text. */
var PCCFinal=(function(){
 'use strict';
 function normalize(s){return String(s||'').replace(/\r\n?/g,'\n');}
 function synchronize(text,previous,current){
  text=normalize(text);previous=previous||{};
  Object.keys(previous).forEach(function(id){
   if(previous[id]===current[id])return;
   var old=normalize(previous[id]),at=text.indexOf(old);
   // An edited paragraph belongs to the reviewer and must not be overwritten.
   if(at>=0)text=text.slice(0,at)+(current[id]||'')+text.slice(at+old.length);
  });
  Object.keys(current).forEach(function(id){
   if(Object.prototype.hasOwnProperty.call(previous,id))return;
   if(text.indexOf(current[id])<0)text+=(text.trim()?'\n\n':'')+current[id];
  });
  return {text:text.replace(/\n{3,}/g,'\n\n').trim(),generated:current};
 }
 function statement(c,r,i,unit,process){
  var label=/^\d+$/.test(c.code)?'indicador ':'item ';
  var text='Considerando que a frase '+(i+1)+', do '+label+c.code+', do processo '+process+', na unidade '+unit+', classificada como PCC, apresentou resultado insatisfatório. Requisito avaliado: '+r.texto;
  if(r.obs)text+=' Constatação: '+r.obs;
  return text;
 }
 return {synchronize:synchronize,statement:statement};
})();
