"""Add read-only inspection guidance and F access without changing assessment data."""
import json,re,sys
from pathlib import Path
from pypdf import PdfReader,PdfWriter
from pypdf.generic import NameObject,TextStringObject,DictionaryObject,ArrayObject,NumberObject,FloatObject,DecodedStreamObject
ROOT=Path(__file__).resolve().parents[1]

def appearance(writer,obj,label,push=False,font_size=None):
 rect=obj['/Rect'];w=float(rect[2])-float(rect[0]);h=float(rect[3])-float(rect[1]);font=font_size if font_size is not None else 4.6
 fontobj=DictionaryObject({NameObject('/Type'):NameObject('/Font'),NameObject('/Subtype'):NameObject('/Type1'),NameObject('/BaseFont'):NameObject('/Helvetica'),NameObject('/Encoding'):NameObject('/WinAnsiEncoding')});fontref=writer._add_object(fontobj)
 def stream(selected=False):
  size=min(6,h*.47)if font_size is not None else 3.8;y=(h-size)/2
  commands=f'q 1 1 1 rg 0 0 {w} {h} re f 0 0 0 RG .3 w .2 .2 {w-.4} {h-.4} re S '
  if not push:
   commands+=f'1 {y} {size} {size} re S '
   if selected:commands+=f'1 {y} m {size+1} {y+size} l S 1 {y+size} m {size+1} {y} l S '
  x=(w-font*.6)/2 if push else size+2
  commands+=f'BT /Helv {font if not push or font_size is not None else 6} Tf 0 0 0 rg 1 0 0 1 {x} {(h-font)/2+1} Tm ({label}) Tj ET Q'
  s=DecodedStreamObject();s.set_data(commands.encode('cp1252'));s.update({NameObject('/Type'):NameObject('/XObject'),NameObject('/Subtype'):NameObject('/Form'),NameObject('/BBox'):ArrayObject([FloatObject(v)for v in [0,0,w,h]]),NameObject('/Resources'):DictionaryObject({NameObject('/Font'):DictionaryObject({NameObject('/Helv'):fontref})})});return writer._add_object(s)
 if push:obj[NameObject('/AP')]=DictionaryObject({NameObject('/N'):stream()})
 else:obj[NameObject('/AP')]=DictionaryObject({NameObject('/N'):DictionaryObject({NameObject('/Off'):stream(),NameObject('/Yes'):stream(True)})})

def patch(path):
 cfg=json.loads((ROOT/'config.js').read_text().strip()[10:-1]);reader=PdfReader(path);writer=PdfWriter();writer.clone_document_from_reader(reader)
 scripts=writer.root_object['/Names']['/JavaScript']['/Names'];found=False
 for index in range(1,len(scripts),2):
  obj=scripts[index].get_object();raw=obj['/JS'];s=raw.get_object().get_data().decode() if hasattr(raw.get_object(),'get_data') else str(raw);start=s.find('var CFG=')
  if start<0:continue
  old,end=json.JSONDecoder().raw_decode(s[start+8:]);fallback=old['itens']['q_p3c1_4.3.2'];template,prefix=fallback['template'],fallback['editorPrefix']
  for key,c in old['itens'].items():
   target=cfg['itens'][key];assert len(c['frases'])==len(target['frases'])
   for j,f in enumerate(c['frases']):f['orientacao']=target['frases'][j]['orientacao']
   c['inspectorGuidanceEnabled']=True
   if not c.get('template'):c['template']=template;c['editorPrefix']=prefix
  old['inspectorGuidanceVersion']=cfg['inspectorGuidanceVersion']
  s=s[:start]+'var CFG='+json.dumps(old,ensure_ascii=True,separators=(',',':'))+s[start+8+end:]
  oldtext="vals['ed_text_'+i]=quebrarLinhas('F'+(i+1)+' - '+c.frases[i].texto,528,10).join('\\r');"
  newtext="var tf=editorF.call(this,'ed_text_'+i);if(tf)tf.textSize=7.5;vals['ed_text_'+i]=quebrarLinhas('F'+(i+1)+' - '+c.frases[i].texto+'\\nOrientação ao inspetor: '+c.frases[i].orientacao,528,7.5).join('\\r');"
  assert oldtext in s;s=s.replace(oldtext,newtext)
  s=s.replace("if(!c||c.frases.length<2)return;","if(!c)return;")
  marker="f=editorF.call(this,'ed_context');"
  visibility="for(var slot=0;slot<7;slot++){var ns=['ed_panel_'+slot,'ed_text_'+slot,'ed_cat_'+slot,'ed_nc_'+slot,'ed_p_'+slot,'ed_score_'+slot,'ed_obs_'+slot,'ed_label_'+slot+'_APPCC','ed_label_'+slot+'_NC','ed_label_'+slot+'_P','ed_label_'+slot+'_NCxP','ed_b_'+slot+'_S','ed_b_'+slot+'_N','ed_b_'+slot+'_A'];for(var ni=0;ni<ns.length;ni++){var ff=editorF.call(this,ns[ni]);if(ff)ff.display=slot<rs.length&&(!(ns[ni].slice(-2)==='_A')||c.allowNA)?0:1;}}"
  assert marker in s;s=s.replace(marker,visibility+marker,1)
  obj[NameObject('/JS')]=TextStringObject(s);found=True
 assert found
 paper=json.loads((ROOT/'paper-data.js').read_text().split('=',1)[1].strip().rstrip(';'))
 form=writer.root_object['/AcroForm']['/Fields']
 for page_index,page in enumerate(writer.pages):
  annots=page.get('/Annots',ArrayObject());byname={str(a.get_object().get('/T','')):a.get_object() for a in annots};height=float(page.mediabox.height)
  for key,c in cfg['itens'].items():
   if c['page']!=page_index or len(c['frases'])!=1:continue
   names=[f'b_{key}_{ch}' for ch in ['S','N']+(['A']if c['allowNA']else [])];buttons=[byname[n]for n in names]
   left=min(float(a['/Rect'][0])for a in buttons);right=max(float(a['/Rect'][2])for a in buttons);bottom=float(buttons[0]['/Rect'][1]);top=float(buttons[0]['/Rect'][3]);width=(right-left)/(len(buttons)+1)
   for j,(name,obj)in enumerate(zip(names,buttons)):
    obj[NameObject('/Rect')]=ArrayObject([FloatObject(v)for v in [left+j*width+.2,bottom,left+(j+1)*width-.2,top]])
    appearance(writer,obj,{'S':'Sim','N':'Não','A':'NA'}[name[-1]])
   fname=f'b_{key}_F';f=DictionaryObject({NameObject('/Type'):NameObject('/Annot'),NameObject('/Subtype'):NameObject('/Widget'),NameObject('/FT'):NameObject('/Btn'),NameObject('/Ff'):NumberObject(65536),NameObject('/F'):NumberObject(4),NameObject('/T'):TextStringObject(fname),NameObject('/TU'):TextStringObject('F - requisito e orientação ao inspetor'),NameObject('/Rect'):ArrayObject([FloatObject(v)for v in [right-width+.2,bottom,right,top]]),NameObject('/P'):page.indirect_reference,NameObject('/A'):DictionaryObject({NameObject('/S'):NameObject('/JavaScript'),NameObject('/JS'):TextStringObject('abrirFrases.call(this,'+json.dumps(key)+');')})})
   appearance(writer,f,'F',True);ref=writer._add_object(f);annots.append(ref);form.append(ref);byname[fname]=f
   for name in names+[fname]:
    obj=byname[name];rect=obj['/Rect'];entry=next((x for x in paper[page_index]['fields']if x['n']==name),None)
    if entry is None:
     entry={'n':name,'type':'/Btn','ro':False,'multi':False,'push':True,'v':'','options':[],'label':'F','font':6};paper[page_index]['fields'].append(entry)
    entry.update(x=float(rect[0]),y=height-float(rect[3]),w=float(rect[2])-float(rect[0]),h=float(rect[3])-float(rect[1]))
  page[NameObject('/Annots')]=annots
 tmp=Path(str(path)+'.guidance.tmp')
 with tmp.open('wb')as f:writer.write(f)
 tmp.replace(path)
 (ROOT/'paper-data.js').write_text('const PAPER='+json.dumps(paper,ensure_ascii=False,separators=(',',':'))+';\n')
 check=PdfReader(path);fields=check.get_fields();assert len(check.pages)==22
 assert all('b_'+key+'_F' in fields for key in cfg['itens'])
 print('PASS: orientações em todos os processos, F para frases únicas e múltiplas, 22 páginas e campos preservados.')
if __name__=='__main__':patch(Path(sys.argv[1]))
