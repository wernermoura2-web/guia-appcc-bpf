var IND_CFG=__CFG__;
function indGet(n){var f=this.getField(n);return f?String(f.value):'';}
function indSet(n,v){var f=this.getField(n);if(f)f.value=v;}
function indRisk(v){return v===null?'Pendente':v>=76?'BAIXO':v>50?'MÉDIO':'ALTO';}
function indSum(list){var e=0,m=0,pending=false,active=false;for(var i=0;i<list.length;i++){e+=list[i].e;m+=list[i].m;pending=pending||list[i].pending;active=true;}var v=!active||pending||!m?null:100*e/m;return {e:e,m:m,pending:pending,v:v};}
function indCalc(){
 var page={},process={},all={},codes={},summaries={};
 for(var k in IND_CFG.itens){var c=IND_CFG.itens[k],e=0,m=0,pending=false,no=false,na=0,notes=[];
  for(var j=0;j<c.frases.length;j++){var a=indGet.call(this,'ans_'+k+'_'+j),cat=indGet.call(this,'cat_'+k+'_'+j)||c.frases[j].cat,w=IND_CFG.pesos[cat]*c.frases[j].P;
   if(a==='A'){na++;continue;}m+=w;if(a==='S')e+=w;if(a==='N')no=true;if(!a)pending=true;
   var note=indGet.call(this,'note_'+k+'_'+j);if(a==='N'||note)notes.push((a==='N'?'NC ':'')+'F'+(j+1)+' | Indicador '+c.code+' | Coluna '+c.col+(note?': '+note:''));
  }
  var sk=c.page+'_'+c.code,summary=summaries[sk]||(summaries[sk]={cat:[],nc:[],p:[],ref:[]});for(var q=0;q<c.frases.length;q++){var ct=indGet.call(this,'cat_'+k+'_'+q)||c.frases[q].cat;if(summary.cat.indexOf(ct)<0)summary.cat.push(ct);if(summary.nc.indexOf(IND_CFG.pesos[ct])<0)summary.nc.push(IND_CFG.pesos[ct]);if(summary.p.indexOf(c.frases[q].P)<0)summary.p.push(c.frases[q].P);}if(summary.ref.indexOf(m)<0)summary.ref.push(m);
  var z={e:e,m:m,pending:pending},a=pending?'Pendente':na===c.frases.length?'N/A':no?'Não':'Sim';all[k]=z;
  (page[c.page]||(page[c.page]=[])).push(z);(process[c.proc]||(process[c.proc]=[])).push(z);(codes[c.page+'_'+c.code]||(codes[c.page+'_'+c.code]=[])).push(a);
  for(var b=0;b<4;b++){var choice=['S','N','A','F'][b],f=this.getField('b_'+k+'_'+choice);if(f)f.buttonSetCaption(choice==='F'?'F':(a===({S:'Sim',N:'Não',A:'N/A'})[choice]?'[X] ':'')+({S:'Sim',N:'Não',A:'NA'})[choice]);}
  if(c.page>=11){indSet.call(this,'obs_p'+(c.page+1)+'_'+c.code,notes.join('\n\n'));}
 }
 for(var sk in summaries){var sp=sk.split('_'),prefix='p'+(Number(sp[0])+1)+'_'+sp[1],sum=summaries[sk],cat=sum.cat.join('/'),nc=sum.nc.join('/');indSet.call(this,'classe_'+prefix,cat.length<11?cat:'Ver F');indSet.call(this,'criticidade_classe_'+prefix,nc.length<7?nc:'Ver F');indSet.call(this,'prob_classe_'+prefix,sum.p.join('/'));indSet.call(this,'pontuacao_'+prefix,sum.ref.join('/'));}
 for(var pk in codes){var arr=codes[pk],v=arr.indexOf('Pendente')>=0?'Pendente':arr.indexOf('Não')>=0?'Não':arr.every(function(x){return x==='N/A';})?'N/A':'Sim';var sp=pk.split('_');indSet.call(this,'res_p'+(Number(sp[0])+1)+'_'+sp[1],v);}
 for(var pg in page){var n=Number(pg)+1,z=indSum(page[pg]);indSet.call(this,'pct_resultado_p'+n,z.v===null?'':z.v.toFixed(2)+'%');indSet.call(this,'risco_resultado_p'+n,indRisk(z.v));
  for(var col=1;col<=4;col++){var selected=[];for(var key in all)if(IND_CFG.itens[key].page==pg&&IND_CFG.itens[key].col===col)selected.push(all[key]);var u=indSum(selected);indSet.call(this,'pct_p'+n+'c'+col,u.v===null?'':u.v.toFixed(2)+'%');indSet.call(this,'risk_p'+n+'c'+col,indRisk(u.v));}
 }
 var levels=[],complete=true;
 for(var pr in process){var z=indSum(process[pr]);indSet.call(this,'matriz_total_'+pr,indRisk(z.v));indSet.call(this,'matriz_final_'+pr,indRisk(z.v));if(z.v===null)complete=false;else levels.push(z.v>=76?1:z.v>50?2:3);}
 var level=complete?Math.max.apply(Math,levels):0;indSet.call(this,'risco_estabelecimento',level?'GRUPO '+level+' - '+['','BAIXO','MÉDIO','ALTO'][level]:'Pendente');
 for(var g=1;g<=3;g++)indSet.call(this,'classificacao_grupo_'+g,(level===g?'(X) ':'( ) ')+'Grupo '+g+' - Estabelecimento de '+['','Baixo','Médio','Alto'][g]+' Risco');
}
function marcarItem(k,a){var c=IND_CFG.itens[k];if(!c||a==='A'&&!c.allowNA)return;if(c.frases.length>1){abrirFrases.call(this,k);return;}indSet.call(this,'ans_'+k+'_0',a);indCalc.call(this);}
function abrirFrases(k){
 var doc=this,c=IND_CFG.itens[k];if(!c)return;
 for(var i=0;i<c.frases.length;i++){
  var phrase=c.frases[i],a=indGet.call(doc,'ans_'+k+'_'+i),cat=indGet.call(doc,'cat_'+k+'_'+i)||phrase.cat,note=indGet.call(doc,'note_'+k+'_'+i);
  var dlg={initialize:function(d){d.load({answ:a==='S'?'Sim':a==='N'?'Não':a==='A'?'NA':'',clss:cat,obsv:note});},commit:function(d){var r=d.store();a=r.answ;cat=r.clss;note=r.obsv;},description:{name:'Indicador '+c.code+' - F'+(i+1)+' / '+c.frases.length,elements:[{type:'view',align_children:'align_left',elements:[{type:'static_text',name:phrase.texto,width:540,height:100},{type:'static_text',name:phrase.ref,width:540,height:34},{type:'static_text',name:'APPCC '+cat+' | NC '+IND_CFG.pesos[cat]+' x P '+phrase.P,width:540},{type:'static_text',name:'Resposta: Sim, Não'+(c.allowNA?' ou NA':'')},{type:'edit_text',item_id:'answ',width:100},{type:'static_text',name:'APPCC: PPHO / PPR / PC / PPRO / PCC'},{type:'edit_text',item_id:'clss',width:100},{type:'static_text',name:'Observação da frase'},{type:'edit_text',item_id:'obsv',width:540,height:80,multiline:true},{type:'ok_cancel'}]}]}};
  if(app.execDialog(dlg)!=='ok')return;
  var answer=a==='Sim'?'S':a==='Não'?'N':a==='NA'&&c.allowNA?'A':'';
  if(!answer||!IND_CFG.pesos[cat]){app.alert('Resposta ou APPCC inválido. A frase foi mantida sem alteração.');i--;continue;}
  indSet.call(doc,'ans_'+k+'_'+i,answer);indSet.call(doc,'cat_'+k+'_'+i,cat);indSet.call(doc,'note_'+k+'_'+i,note);indCalc.call(doc);
 }
}
function limparPagina(page){if(app.alert('Limpar as respostas desta página?',2,2)!==4)return;for(var k in IND_CFG.itens)if(IND_CFG.itens[k].page===page)for(var j=0;j<IND_CFG.itens[k].frases.length;j++){indSet.call(this,'ans_'+k+'_'+j,'');indSet.call(this,'note_'+k+'_'+j,'');}indCalc.call(this);}
function anexarFoto(n){var f=this.getField(n);if(f)f.buttonImportIcon();}
function girarFoto(n){var f=this.getField(n);if(f)f.rotation=((f.rotation||0)+90)%360;}
function selecionarFonte(col,label){for(var j=0;j<2;j++){var f=this.getField('fonte_'+col+'_'+j);if(f)f.buttonSetCaption((label===(j?'Surgência':'Poço')?'[X] ':'')+(j?'Surgência':'Poço'));}}
indCalc.call(this);
