/* Keep editable base fields and append the selected inspection reports. */
(()=>{
'use strict';
const link=document.querySelector('a[download][href*="Guia_APPCC_BPF.pdf"]');
if(!link)return;
const A4=[595.28,841.89],margin=36,width=A4[0]-margin*2;
function printable(value){return String(value??'').replace(/☒/g,'X').replace(/☐/g,'[ ]').replace(/[–—]/g,'-').replace(/×/g,'x').replace(/[^\x20-\x7e\xa0-\xff\n]/g,' ');}
async function appendReports(pdf){
 const normal=await pdf.embedFont(PDFLib.StandardFonts.Helvetica),bold=await pdf.embedFont(PDFLib.StandardFonts.HelveticaBold);
 let page,y,annexPage=0;
 function newPage(title){page=pdf.addPage(A4);y=A4[1]-margin;annexPage++;page.drawText('Anexos da inspeção - '+annexPage,{x:margin,y:20,size:8,font:normal});if(title)text(title,12,true);}
 function lines(value,font,size,max){
  const result=[];for(const paragraph of printable(value).split('\n')){
   let line='';for(const word of paragraph.split(/\s+/).filter(Boolean)){if(font.widthOfTextAtSize((line?line+' ':'')+word,size)<=max){line+=(line?' ':'')+word;continue;}
    if(line){result.push(line);line='';}
    let chunk='';for(const char of word){if(chunk&&font.widthOfTextAtSize(chunk+char,size)>max){result.push(chunk);chunk='';}chunk+=char;}line=chunk;
   }result.push(line);
  }return result;
 }
 function text(value,size=9,strong=false){
  const font=strong?bold:normal;for(const line of lines(value,font,size,width)){if(y<margin+size*1.3)newPage();page.drawText(line,{x:margin,y:y-size,size,font});y-=size*1.3;}y-=4;
 }
 function table(rowValues,fractions,fieldPrefix){
  const size=7.2,pad=3,cols=fractions.map(f=>f*width);
  for(const [index,values]of rowValues.entries()){
   const font=index===0?bold:normal,cells=values.map((v,i)=>lines(v,font,size,cols[i]-pad*2));
   const maxLines=Math.max(...cells.map(c=>c.length));let offset=0;
   while(offset<maxLines){
    if(y<margin+size*1.3+pad*2)newPage();
    const count=Math.min(maxLines-offset,Math.max(1,Math.floor((y-margin-pad*2)/(size*1.3))));
    const height=count*size*1.3+pad*2;let x=margin;
    cells.forEach((cell,i)=>{page.drawRectangle({x,y:y-height,width:cols[i],height,borderWidth:.4,borderColor:PDFLib.rgb(.65,.7,.75),...(index===0?{color:PDFLib.rgb(.93,.95,.97)}:{})});cell.slice(offset,offset+count).forEach((line,j)=>page.drawText(line,{x:x+pad,y:y-pad-size-j*size*1.3,size,font}));x+=cols[i];});
    if(fieldPrefix&&index>0&&offset===0){const form=pdf.getForm(),answerX=margin+cols[0],obsX=margin+cols.slice(0,-1).reduce((a,b)=>a+b,0);const answer=form.createDropdown(fieldPrefix+'_'+index+'_resposta');answer.addOptions(['','Sim','Não','NA']);answer.addToPage(page,{x:answerX+1,y:y-height+1,width:cols[1]-2,height:height-2,font:normal,borderWidth:0});answer.setFontSize(7);const observation=form.createTextField(fieldPrefix+'_'+index+'_observacao');observation.enableMultiline();observation.addToPage(page,{x:obsX+1,y:y-height+1,width:cols.at(-1)-2,height:height-2,font:normal,borderWidth:0});observation.setFontSize(7);}
    y-=height;offset+=count;
   }
  }y-=8;
 }
 const documents=document.getElementById('include-document-checklist')?.checked;
 if(documents)for(const section of document.querySelectorAll('#documents-print-copy .doc-process')){
  newPage(section.querySelector('h2')?.textContent||'Lista de documentos');
  text('Envasadora: ____________________________________ | Data: ____/____/________');
  for(const node of section.children){if(node.tagName==='H3')text(node.textContent,10,true);if(node.tagName==='TABLE'){
   const body=[...node.querySelectorAll('tbody tr')].map(tr=>[...tr.cells].map(td=>td.innerText));
   table([['Item / referência','Documento ou registro','Entregue','S','N','Não possui','NA'],...body.map(c=>c.length===7?[c[0],c[1],'','','','','']:[c[0]||'',c[1]||'','','','','',''])],[.12,.54,.08,.04,.04,.09,.09]);
  }}
 }
 newPage('Anexo F completo - Em branco');
 text('Todos os itens e unidades. Preencha as respostas e observações nos campos editáveis.');
 let itemIndex=0;
 for(const row of window.InspectorOrientations.catalog()){
  if(y<margin+100)newPage();
  text(row.process+' | '+(row.processId||row.code)+' ('+row.code+') | '+row.phraseLabels.join(' / '),10,true);
  text(row.requirement);
  const guidance=window.InspectorOrientations.value(row.id);if(guidance)text('Orientação ao inspetor: '+guidance,8);
  const values=row.instances.map(instance=>{
   const c=CFG.itens[instance.key],f=c.frases[instance.index],nc=CFG.pesos[f.cat];
   let unit=unitName(c.page,c.col);if(c.page>=2&&c.page<=5)unit+=' / Captação '+(c.page-1);
   return [unit+' / F'+(instance.index+1),'',f.cat,nc,f.P,nc*f.P,'',''];
  });
  table([['Unidade / F','Resposta','APPCC','NC','P','NC x P','Pontos obtidos','Observações'],...values],[.18,.09,.08,.03,.03,.07,.09,.43],'anexoF_'+(++itemIndex));
 }
 return annexPage;
}
let busy=false;
link.addEventListener('click',async event=>{
 event.preventDefault();if(busy)return;busy=true;const status=document.getElementById('paper-status');link.setAttribute('aria-busy','true');
 try{
  save();window.DocumentChecklistAnnex?.prepare();window.GuidanceAnnex?.prepare();
  status.textContent='Preparando PDF editável em branco com todos os F…';
  if(!window.PDFLib)throw Error('O componente PDF não carregou. Atualize a página e tente novamente.');
  const response=await fetch(link.href,{cache:'no-cache'});if(!response.ok)throw Error('Não foi possível carregar o PDF editável.');
  const pdf=await PDFLib.PDFDocument.load(await response.arrayBuffer());
  const pages=await appendReports(pdf);const bytes=await pdf.save();
  const url=URL.createObjectURL(new Blob([bytes],{type:'application/pdf'})),download=document.createElement('a');
  download.href=url;download.download='Guia_APPCC_BPF_Em_Branco_Todos_F.pdf';download.click();setTimeout(()=>URL.revokeObjectURL(url),60000);
  status.textContent='PDF editável preparado com '+pages+' páginas de anexos em branco, incluindo todos os F.';
 }catch(error){status.textContent='Falha ao gerar PDF: '+error.message;alert(status.textContent);}
 finally{busy=false;link.removeAttribute('aria-busy');}
});
window.EditablePDFReports={appendReports};
})();
