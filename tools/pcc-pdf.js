function PCC_FINAL_UPDATE(){
 if(this.__pccFinalBusy)return;this.__pccFinalBusy=true;
 try{
  var left=this.getField('consideracoes_finais'),right=this.getField('consideracoes_finais_col2'),meta=this.getField('pcc_final_generated');if(!left||!meta)return;
  var stored={};try{stored=JSON.parse(meta.valueAsString||'{}');}catch(e){}
  var current={},cfg=typeof IND_CFG!=='undefined'?IND_CFG:CFG;
  var data=typeof IND_CFG==='undefined'?dados.call(this):null;
  var processNames={'4.1':'Captação','4.2':'Condução','4.3':'Reservatórios','4.5':'Recepção','4.6':'Higienização','4.7':'Envase','4.10':'Qualidade','4.11':'Responsabilidade'};
  for(var k in cfg.itens){var c=cfg.itens[k],rr=data?registros.call(this,k,data):null;
   for(var i=0;i<c.frases.length;i++){
    var a=rr?rr[i].a:indGet.call(this,'ans_'+k+'_'+i),cat=rr?rr[i].c:(indGet.call(this,'cat_'+k+'_'+i)||c.frases[i].cat),obs=rr?rr[i].o:indGet.call(this,'note_'+k+'_'+i);
    if(a!=='N'||cat!=='PCC')continue;
    var unit=rr?nomeUnidade.call(this,c):('Coluna '+c.col);
    current[k+'#'+i]=PCCFinal.statement(c,{texto:c.frases[i].texto,obs:obs},i,unit,processNames[c.proc]||c.proc);
   }
  }
  var text=String(left.valueAsString||'')+(right&&right.valueAsString?((stored.version?'':'\n\n')+right.valueAsString):'');
  var result=PCCFinal.synchronize(text,stored.generated,current);
  // Split at a paragraph boundary without losing any part of the text.
  var at=result.text.indexOf('\n\n',1800);if(at<0)at=result.text.length;
  left.readonly=false;left.value=result.text.slice(0,at);left.textSize=8;
  if(right){right.readonly=false;right.value=result.text.slice(at);right.textSize=8;}
  meta.value=JSON.stringify({version:1,generated:result.generated});
 }finally{this.__pccFinalBusy=false;}
}
if(typeof indCalc==='function'){
 var PCC_ORIGINAL_INDCALC=indCalc;
 indCalc=function(){PCC_ORIGINAL_INDCALC.apply(this,arguments);PCC_FINAL_UPDATE.call(this);};
}else if(typeof recalcularTudo==='function'){
 var PCC_ORIGINAL_CALC=recalcularTudo;
 recalcularTudo=function(){PCC_ORIGINAL_CALC.apply(this,arguments);PCC_FINAL_UPDATE.call(this);};
}
PCC_FINAL_UPDATE.call(this);
