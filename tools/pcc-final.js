/* Shared by the browser forms and Acrobat. Preserve manually revised text. */
var PCCFinal=(function(){
 'use strict';
 function normalize(s){return String(s||'').replace(/\r\n?/g,'\n');}
 function synchronize(text,previous,current){
  text=normalize(text);previous=previous||{};
  Object.keys(previous).forEach(function(id){
   if(previous[id]===current[id])return;
   var old=normalize(previous[id]);
   // Remove only the former generated requirement, preserving review notes.
   if(current[id]&&current[id].indexOf(' Requisito avaliado: ')<0){
    var marker=old.indexOf(' Requisito avaliado: ');
    if(marker>=0){var stop=old.indexOf(' Constatação: ',marker);if(stop<0)stop=old.length;var obsolete=old.slice(marker,stop);text=text.replace(obsolete,'');old=old.slice(0,marker)+old.slice(stop);}
   }
   var at=text.indexOf(old);
   while(at>=0){
    var end=at+old.length;
    if((at===0||text.slice(at-2,at)==='\n\n')&&(end===text.length||text.slice(end,end+2)==='\n\n'))break;
    at=text.indexOf(old,at+1);
   }
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
  var text='Considerando que a frase '+(i+1)+', do '+label+c.code+', do processo '+process+', na unidade '+unit+', classificada como PCC, apresentou resultado insatisfatório.';
  if(r.obs)text+=' Constatação: '+r.obs;
  return text;
 }
 return {synchronize:synchronize,statement:statement};
})();
