/* PDF work runs off the UI thread; fields and native F templates stay interactive. */
importScripts('pdf-lib.min.js');
let payload,CFG,window,document;
function unitName(p,c){return payload.units[p+':'+c]||('Unidade '+c);}
function setup(data){
 payload=data;CFG=data.cfg;
 window={InspectorOrientations:{catalog:()=>data.catalog,value:id=>data.guidance[id]||''}};
 const sections=data.documents.map(g=>({querySelector:()=>({textContent:g.title}),children:g.tables.flatMap(t=>[{tagName:'H3',textContent:t.title},{tagName:'TABLE',querySelectorAll:()=>t.rows.map(r=>({cells:r.cells.map(innerText=>({innerText}))}))}])}));
 document={getElementById:()=>({checked:data.docs}),querySelectorAll:()=>sections};
}
const A4=[595.28,841.89],margin=36,width=A4[0]-margin*2;
function printable(value){return String(value??'').replace(/☒/g,'X').replace(/☐/g,'[ ]').replace(/[–—]/g,'-').replace(/×/g,'x').replace(/[^\x20-\x7e\xa0-\xff\n]/g,' ');}
async function appendReports(pdf){
 const normal=await pdf.embedFont(PDFLib.StandardFonts.Helvetica),bold=await pdf.embedFont(PDFLib.StandardFonts.HelveticaBold);
 let page,y,annexPage=0,documentTable=0,documentProcess=0;
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
    if(fieldPrefix?.startsWith('documento_')&&index>0&&offset===0){for(let col=2;col<7;col++){const x=margin+cols.slice(0,col).reduce((a,b)=>a+b,0)+(cols[col]-9)/2;pdf.getForm().createCheckBox(fieldPrefix+'_'+index+'_'+col).addToPage(page,{x,y:y-height/2-4.5,width:9,height:9,borderWidth:.5});}}else if(fieldPrefix&&index>0&&offset===0){const form=pdf.getForm(),answerX=margin+cols[0],obsX=margin+cols.slice(0,-1).reduce((a,b)=>a+b,0);const answer=form.createDropdown(fieldPrefix+'_'+index+'_resposta');answer.addOptions(['','Sim','Não','NA']);answer.addToPage(page,{x:answerX+1,y:y-height+1,width:cols[1]-2,height:height-2,font:normal,borderWidth:0});answer.setFontSize(7);const observation=form.createTextField(fieldPrefix+'_'+index+'_observacao');observation.enableMultiline();observation.addToPage(page,{x:obsX+1,y:y-height+1,width:cols.at(-1)-2,height:height-2,font:normal,borderWidth:0});observation.setFontSize(7);}
    y-=height;offset+=count;
   }
  }y-=8;
 }
 const documents=document.getElementById('include-document-checklist')?.checked;
 if(documents)for(const section of document.querySelectorAll('#documents-print-copy .doc-process')){
  newPage(section.querySelector('h2')?.textContent||'Lista de documentos');
  documentProcess++;text('Envasadora:');page.drawText('Data:',{x:315,y:y+8,size:9,font:normal});for(const [name,x,w]of [['envasadora',90,218],['data',348,115]]){const field=pdf.getForm().createTextField('documentos_'+documentProcess+'_'+name);field.addToPage(page,{x,y:y+4,width:w,height:13,font:normal,borderWidth:0});field.setFontSize(9);field.setText(printable(payload.meta[name==='envasadora'?'empresa':'data']||''));}
  for(const node of section.children){if(node.tagName==='H3')text(node.textContent,10,true);if(node.tagName==='TABLE'){
   const body=[...node.querySelectorAll('tbody tr')].map(tr=>[...tr.cells].map(td=>td.innerText));
   table([['Item / referência','Documento ou registro','Entregue','S','N','Não possui','NA'],...body.map(c=>c.length===7?[c[0],c[1],'','','','','']:[c[0]||'',c[1]||'','','','','',''])],[.12,.54,.08,.04,.04,.09,.09],'documento_'+(++documentTable));
   const rows=payload.documents[documentProcess-1].tables[documentTable%2===1?0:1].rows;rows.forEach((r,i)=>r.states.forEach((on,j)=>{if(on)pdf.getForm().getCheckBox('documento_'+documentTable+'_'+(i+1)+'_'+(j+2)).check();}));
  }}
 }
 if(!payload.compact)return annexPage;
 newPage('Anexo F compacto - Respostas da inspeção');
 let itemIndex=0;
 for(const row of window.InspectorOrientations.catalog()){
  row.instances=row.instances.filter(x=>{const r=payload.answers[x.key][x.index];return r.a||r.obs;});if(!row.instances.length)continue;
  if(y<margin+100)newPage();
  text(row.process+' | '+(row.processId||row.code)+' ('+row.code+') | '+row.phraseLabels.join(' / '),10,true);
  text(row.requirement); const owner=CFG.itens[row.instances[0].key];if(owner.scoringGroups){const label='Pontuação APPCC: '+owner.scoringGroups.map(g=>'média de '+g.map(n=>'F'+n).join(', ')).join('; ')+'. NA fica fora do divisor; demais frases independentes.';text(label,8);}
  const guidance=window.InspectorOrientations.value(row.id);if(guidance)text('Orientação ao inspetor: '+guidance,8);
  const values=row.instances.map(instance=>{
   const c=CFG.itens[instance.key],f=payload.answers[instance.key][instance.index],nc=CFG.pesos[f.cat];
   let unit=unitName(c.page,c.col);if(c.page>=2&&c.page<=5)unit+=' / Captação '+(c.page-1);
   return [unit+' / F'+(instance.index+1),'',f.cat,nc,f.P,nc*f.P,Number((f.points||0).toFixed(6)),''];
  });
  table([['Unidade / F','Resposta','APPCC','NC','P','NC x P','Pontos obtidos','Observações'],...values],[.18,.09,.08,.03,.03,.07,.09,.43],'anexoF_'+(++itemIndex));
  row.instances.forEach((x,i)=>{const v=payload.answers[x.key][x.index],prefix='anexoF_'+itemIndex+'_'+(i+1);if(v.a)pdf.getForm().getDropdown(prefix+'_resposta').select(({S:'Sim',N:'Não',A:'NA'})[v.a]);pdf.getForm().getTextField(prefix+'_observacao').setText(printable(v.obs||''));});
 }
 for(const [index,note]of Object.entries(payload.notes||{})){if(String(note||'').trim()){if(y<margin+100)newPage();text('Observações gerais - página '+(Number(index)+1),10,true);text(note);}}
 return annexPage;
}

self.onmessage=async e=>{try{
 setup(e.data);const response=await fetch('Guia_APPCC_BPF.pdf?v=formulario-f-20261103');if(!response.ok)throw Error('Falha ao carregar o formulário.');
 const pdf=await PDFLib.PDFDocument.load(await response.arrayBuffer()),form=pdf.getForm(),font=await pdf.embedFont(PDFLib.StandardFonts.Helvetica);
 const byName=new Map(form.getFields().map(f=>[f.getName(),f]));
 for(const [name,value]of Object.entries(payload.values)){
  const f=byName.get(name);if(!f)continue;
  if(f instanceof PDFLib.PDFTextField)f.setText(printable(value));
  else if(f instanceof PDFLib.PDFDropdown){const v=printable(value);if(f.getOptions().includes(v))f.select(v);}
  else if(f instanceof PDFLib.PDFCheckBox){value==='Yes'?f.check():f.uncheck();}
  else if(f instanceof PDFLib.PDFButton&&/^b_q_/.test(name)){
   for(const w of f.acroField.getWidgets())w.getOrCreateAppearanceCharacteristics().setCaptions({normal:printable(value)});f.defaultUpdateAppearances(font);
  }
 }
 form.getTextField('dados_frases').setText(JSON.stringify(payload.native).replace(/[\u0100-\uffff]/g,c=>'\\u'+c.charCodeAt(0).toString(16).padStart(4,'0')));
 await appendReports(pdf);
 for(const f of form.getFields())if(f.needsAppearancesUpdate())f.defaultUpdateAppearances(font);
 for(const [name,data]of Object.entries(payload.images||{})){const pi=payload.paper.findIndex(p=>p.fields.some(f=>f.n===name));if(pi<0)continue;const field=payload.paper[pi].fields.find(f=>f.n===name),page=pdf.getPage(pi),img=await (/^data:image\/png/.test(data)?pdf.embedPng(data):pdf.embedJpg(data)),scale=Math.min(field.w/img.width,field.h/img.height),w=img.width*scale,h=img.height*scale;page.drawImage(img,{x:field.x+(field.w-w)/2,y:page.getHeight()-field.y-field.h+(field.h-h)/2,width:w,height:h});}
 const bytes=await pdf.save({updateFieldAppearances:false});self.postMessage({bytes},[bytes.buffer]);
 }catch(error){self.postMessage({error:error.message});}};
