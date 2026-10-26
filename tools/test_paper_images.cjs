const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
const root=path.join(__dirname,'..'),source=fs.readFileSync(path.join(root,'paper.js'),'utf8'),model=fs.readFileSync(path.join(root,'paper-data.js'),'utf8');const ctx=vm.createContext({});
vm.runInContext(model+'\n'+source.match(/function paperImageSource\(page,index\)\{[^\n]*\}/)[0],ctx);
const images=vm.runInContext('PAPER.map((p,i)=>paperImageSource(p,i).split("?")[0])',ctx),pages=vm.runInContext('PAPER',ctx);
assert.equal(images[12],pages[12].image,'Responsibility must use the generated image, not the legacy WebP');assert.equal(images.length,22);images.forEach(name=>assert(fs.existsSync(path.join(root,name)),name));
assert(fs.readFileSync(path.join(root,'sw-appcc.js'),'utf8').includes("'"+images[12]+"'"),'Current page 13 must be available offline');console.log('PASS image selection: current responsibility overview, all 22 pages available and offline page 13 cached');
