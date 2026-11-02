"""Sync existing editable PDF data without rebuilding its page layout."""
import json,re
from pathlib import Path
from pypdf import PdfReader,PdfWriter
from pypdf.generic import NameObject,TextStringObject,ArrayObject
cfg=json.loads(Path('config.js').read_text().removeprefix('const CFG=').strip().removesuffix(';'))
path=Path('Guia_APPCC_BPF.pdf');reader=PdfReader(path);writer=PdfWriter();writer.clone_document_from_reader(reader)
names=writer.root_object['/Names']['/JavaScript']['/Names'];count=0
for i in range(1,len(names),2):
 obj=names[i].get_object();raw=obj['/JS'].get_object();s=raw.get_data().decode() if hasattr(raw,'get_data') else str(raw)
 if 'var CFG=' not in s:continue
 start=s.index('var CFG=')+8;old,end=json.JSONDecoder().raw_decode(s[start:])
 for key,c in old['itens'].items():
  c['frases']=cfg['itens'][key]['frases']
  for prop in ['allowNA','template','editorPrefix','roleAlternatives','scoringGroups']:
   if prop in cfg['itens'][key]:c[prop]=cfg['itens'][key][prop]
 old['classificationRevision']=cfg['classificationRevision'];old['inspectorGuidanceVersion']=cfg['inspectorGuidanceVersion']
 s=s[:start]+json.dumps(old,ensure_ascii=True,separators=(',',':'))+s[start+end:]
 needle="+'\\nOrientação: '+c.frases[i].orientacao"
 if 'Fundamento da classificação:' not in s:
  s=s.replace(needle,"+'\\nBPF/APPCC: '+String(c.frases[i].cat).replace('PPHO','POP')+'\\nFundamento da classificação: '+(c.frases[i].fundamento||c.frases[i].consideracao||'')"+needle)
 if 'function migrarRegistrosCaptacao' not in s:
  migration="""function migrarRegistrosCaptacao(){var d=dados.call(this);if(d.capRecordsVersion==='captacao-registros-f3-20261101')return;d.legacyCapRecords=d.legacyCapRecords||{};for(var key in CFG.itens){if(CFG.itens[key].code!=='4.1.3'||!d.u[key])continue;var rs=d.u[key];if(!rs[2]&&rs[1]){d.legacyCapRecords[key]=JSON.parse(JSON.stringify(rs[1]));rs[1]={c:'PPR',a:'',o:'Revisar capacitação e registros separadamente; resposta conjunta anterior preservada no histórico.'};rs[2]={c:'PPR',a:'',o:'Confirmar registros de limpeza e desinfecção da captação.'};}}d.capRecordsVersion='captacao-registros-f3-20261101';gravar.call(this,d);}
"""
  s=s.replace('function iniciar(){try{',migration+'function iniciar(){try{migrarRegistrosCaptacao.call(this);')
 if 'function migrarPccHigienizacao' not in s:
  migration="""function migrarPccHigienizacao(){var d=dados.call(this);if(d.pccHigieneVersion==='pcc-higienizacao-condutividade-20261102')return;d.pccHigieneBackup=JSON.parse(JSON.stringify(d.u||{}));for(var key in CFG.itens){var c=CFG.itens[key];if(!d.u||!d.u[key])continue;if(c.code==='4.1.3'||c.code==='4.2.7'||c.code==='4.3.5'||c.code==='4.7.8'){if(d.u[key][0])d.u[key][0].c='PCC';}if(c.code==='4.7.8'&&d.u[key][1])d.u[key][1].c='PC';}d.pccHigieneVersion='pcc-higienizacao-condutividade-20261102';gravar.call(this,d);}
"""
  s=s.replace('function iniciar(){try{',migration+'function iniciar(){try{migrarPccHigienizacao.call(this);')
 core=Path('app.js').read_text().split('/* GROUP-SCORING-START */',1)[1].split('/* GROUP-SCORING-END */',1)[0]
 if 'var APPCCScoring=' not in s:s=core+'\n'+s
 if '/* mean-totals */' not in s:
  s=s.replace('/* role-alternatives */',"/* mean-totals */var averaged=APPCCScoring.totals(c,rs,CFG.pesos);num=averaged.earned;den=averaged.maximum;/* role-alternatives */")
  needle="put.call(this,'criticidade_'+cf,ncs.join('/'))"
  replacement="var allRows=[];for(var mi=0;mi<c.frases.length;mi++)allRows.push({a:'S',c:d.refs[cf]||c.frases[mi].cat});possible=APPCCScoring.totals(c,allRows,CFG.pesos).maximum;"+needle
  s=s.replace(needle,replacement)
 if 'function migrarRemocaoRegistroHigiene' not in s:
  fn="""function migrarRemocaoRegistroHigiene(){var d=dados.call(this);if(d.removedHygieneRecordVersion==='medias-frases-20261102')return;d.removedHygieneRecordHistory=d.removedHygieneRecordHistory||{};for(var key in CFG.itens)if(CFG.itens[key].code==='4.6.11'&&d.u[key]){var old=d.u[key];d.removedHygieneRecordHistory[key]=JSON.parse(JSON.stringify(old));d.u[key]=[old[0]||{},old[2]||{}];}d.removedHygieneRecordVersion='medias-frases-20261102';gravar.call(this,d);}
"""
  s=fn+s;s=s.replace('migrarRegistrosEmbalagens.call(this);','migrarRegistrosEmbalagens.call(this);migrarRemocaoRegistroHigiene.call(this);')
 obj[NameObject('/JS')]=TextStringObject(s);count+=1
assert count==1
# Remove the protocol/literature appendix; preserve the 22 inspection pages.
if len(writer.pages)>22:
 assert any('Protocolo' in (pg.extract_text() or '') or 'Literatura' in (pg.extract_text() or '') for pg in writer.pages[22:])
 for i in range(len(writer.pages)-1,21,-1):writer.remove_page(i)
def possible_score(c):
 groups=[[n-1 for n in g]for g in c.get('scoringGroups',[])];used={i for g in groups for i in g};groups +=[[i]for i in range(len(c['frases']))if i not in used]
 return sum(sum(cfg['pesos'][c['frases'][i]['cat']]*c['frases'][i].get('P',c.get('P',1))for i in g)/len(g)for g in groups)
fields=writer.get_fields();values={}
for cf in {c['classField'] for c in cfg['itens'].values()}:
 c=next(c for c in cfg['itens'].values() if c['classField']==cf);fs=c['frases'];unique=lambda xs:list(dict.fromkeys(xs))
 vals={cf:'/'.join(unique([f['cat'].replace('PPHO','POP') for f in fs])),'criticidade_'+cf:'/'.join(unique([str(cfg['pesos'][f['cat']]) for f in fs])),'pontuacao_'+cf[7:]:str(round(possible_score(c),8)).rstrip('0').rstrip('.') if possible_score(c)%1 else str(int(possible_score(c)))}
 values.update({k:v for k,v in vals.items() if k in fields})
for pg in writer.pages:
 for a in pg.get('/Annots',[]):
  o=a.get_object();n=str(o.get('/T',''))
  if n in values:
   o[NameObject('/DV')]=TextStringObject(values[n])
   if o.get('/FT')=='/Ch':
    opts=o.get('/Opt',ArrayObject())
    if values[n] not in [str(v) for v in opts]:opts.append(TextStringObject(values[n]));o[NameObject('/Opt')]=opts
 relevant={str(a.get_object().get('/T','')):values[str(a.get_object().get('/T',''))] for a in pg.get('/Annots',[]) if str(a.get_object().get('/T','')) in values}
 if relevant:writer.update_page_form_field_values(pg,relevant,auto_regenerate=False)
with path.open('wb') as f:writer.write(f)
result=PdfReader(path);assert len(result.pages)==22
actual=result.get_fields();assert len(actual)==len(fields)
for k,v in values.items():assert str(actual[k]['/V'])==v
print('PDF sincronizado:',len(result.pages),'páginas;',len(actual),'campos preservados.')

