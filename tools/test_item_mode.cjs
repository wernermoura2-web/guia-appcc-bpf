const fs=require('fs'),vm=require('vm'),assert=require('assert/strict');
const nodes={};const ctx=vm.createContext({window:{APPCC_PAPER:true,APPCC_ORIGINAL_ITEMS:true,addEventListener(){}},document:{getElementById(id){return nodes[id]||(nodes[id]={textContent:'',innerHTML:''});}},localStorage:{getItem(){return null},setItem(){}},refreshPaper(){},console});
for(const f of ['config.js','process-display.js','app.js'])vm.runInContext(fs.readFileSync(f,'utf8'),ctx);
function run(s){return vm.runInContext(s,ctx)}
run("S={meta:{},a:{},units:{},names:{},notes:{}};for(const c of Object.values(CFG.itens))S.units['p'+c.page+'c'+c.col]=false;S.units.p0c1=true;for(const [k,c]of Object.entries(CFG.itens))if(c.page===0&&c.col===1){S.a[k]={};c.frases.forEach((f,i)=>S.a[k][i]={a:'S'});}");
assert.equal(run('pageResult(0,1)'),100);assert.equal(run('appccSimulation(0,1)'),100);
run("S.a['q_p1c1_4.1.1'][0].a='N'");assert.equal(run("score('q_p1c1_4.1.1').a"),'N');assert(Math.abs(run('pageResult(0,1)')-200/3)<1e-8);assert(run('appccSimulation(0,1)')>run('pageResult(0,1)'));
run("delete S.a['q_p1c1_4.1.1'][1]");assert.equal(run("score('q_p1c1_4.1.1').pending"),false);assert.equal(run('appccSimulation(0,1)'),null);
run("S.a['q_p1c1_4.1.1'][1]={a:'S'};constOriginal=pageResult(0,1);editing='q_p1c1_4.1.1';renderPhrases()");assert(nodes['phrase-body'].innerHTML.includes('disabled'));
run("editField('q_p1c1_4.1.1',0,'P',5)");assert.equal(run("rows('q_p1c1_4.1.1')[0].P"),3);
run("S.selfInspectionEditing=true;editField('q_p1c1_4.1.1',0,'cat','PCC');editField('q_p1c1_4.1.1',0,'NC',2);editField('q_p1c1_4.1.1',0,'P',5)");assert.equal(run("rows('q_p1c1_4.1.1')[0].NC"),2);assert.equal(run("rows('q_p1c1_4.1.1')[0].P"),5);assert.equal(run('pageResult(0,1)'),run('constOriginal'));assert(nodes['phrase-body'].innerHTML.includes('type="number"'));
run("editField('q_p1c1_4.1.1',0,'P',6)");assert.equal(run("rows('q_p1c1_4.1.1')[0].P"),5);
const saved=run('JSON.stringify(S)');run('S=JSON.parse('+JSON.stringify(saved)+')');assert.equal(run("rows('q_p1c1_4.1.1')[0].P"),5);
run('S.appccOverrides={};S.selfInspectionEditing=false');assert.equal(run("rows('q_p1c1_4.1.1')[0].P"),3);assert.equal(run("rows('q_p1c1_4.1.1')[0].cat"),'PPRO');assert.equal(run("S.a['q_p1c1_4.1.1'][0].a"),'N');
// Other guide entry points keep their existing APPCC calculation.
run('window.APPCC_ORIGINAL_ITEMS=false');assert.equal(run('pageResult(0,1)'),run('appccSimulation(0,1)'));
console.log('OK: item aggregation, original attendance, informative simulation, lock/unlock, NC/P 1–5, restore, JSON persistence, other guide unchanged.');
