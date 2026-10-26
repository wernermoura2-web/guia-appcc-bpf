const fs=require('fs'),vm=require('vm'),assert=require('assert'),path=require('path');
const root=path.join(__dirname,'..'),config=fs.readFileSync(path.join(root,'config.js'),'utf8'),cfg=JSON.parse(config.trim().slice(10,-1));const elements={};
const ctx=vm.createContext({document:{getElementById:id=>elements[id]||(elements[id]={})},window:{APPCC_PAPER:true},localStorage:{getItem:()=>null,setItem:()=>{}},console});
vm.runInContext(config+'\n'+fs.readFileSync(path.join(root,'app.js'),'utf8'),ctx);
for(const [key,c]of Object.entries(cfg.itens)){
 assert(c.frases.every(f=>f.orientacao));vm.runInContext(`editing=${JSON.stringify(key)};S.a[editing]={0:{a:'N',obs:'Observação preservada'}};renderPhrases();`,ctx);
 const html=elements['phrase-body'].innerHTML;assert(html.includes('Observação preservada'));assert.equal((html.match(/Orientação ao inspetor:/g)||[]).length,c.frases.length);
 for(const f of c.frases)assert(html.includes(f.orientacao));
}
console.log('PASS: orientações no F de todos os processos do original, com notas e respostas preservadas.');
