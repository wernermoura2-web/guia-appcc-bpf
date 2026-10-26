"""Stack all CQ and responsibility answers vertically in their existing cells."""
from pathlib import Path
import json,sys
from pypdf import PdfReader,PdfWriter
from pypdf.generic import NameObject,ArrayObject,FloatObject
from inspector_guidance import appearance
ROOT=Path(__file__).resolve().parents[1]

def patch(path):
 cfg=json.loads((ROOT/'config.js').read_text().strip()[10:-1]);paper=json.loads((ROOT/'paper-data.js').read_text().split('=',1)[1].strip().rstrip(';'))
 before=json.loads(json.dumps(paper))
 reader=PdfReader(path);writer=PdfWriter();writer.clone_document_from_reader(reader);count=0
 for pgindex in [11,12]:
  page=writer.pages[pgindex];height=float(page.mediabox.height);widgets={str(a.get_object().get('/T','')):a.get_object()for a in page['/Annots']};fields={f['n']:f for f in paper[pgindex]['fields']}
  for key,c in cfg['itens'].items():
   if c['page']!=pgindex:continue
   obs=fields[f'obs_p{pgindex+1}_{c["code"]}'];weight=fields['peso_'+key]
   choices=['S','N']+(['A']if c['allowNA']else[])+['F'];names=['b_'+key+'_'+ch for ch in choices]
   top=weight['y']+weight['h']+2;bottom=obs['y']+obs['h']-1;available=bottom-top
   gap=6 if pgindex==12 else 2.5 if len(names)==3 else 2
   button_height=min(18 if pgindex==12 else 12,(available-gap*(len(names)-1))/len(names))
   assert button_height>=8,(key,button_height)
   total=button_height*len(names)+gap*(len(names)-1);start=top+(available-total)/2
   for j,(name,ch)in enumerate(zip(names,choices)):
    f=fields[name];y=start+j*(button_height+gap);font=min(8.5 if pgindex==12 else 7.5,button_height*.72)
    f.update(x=528.25,y=y,w=49,h=button_height,font=font)
    obj=widgets[name];obj[NameObject('/Rect')]=ArrayObject([FloatObject(v)for v in [f['x'],height-y-button_height,f['x']+f['w'],height-y]])
    appearance(writer,obj,{'S':'Sim','N':'Não','A':'NA','F':'F'}[ch],ch=='F',font_size=font)
   ordered=[fields[n]for n in names]
   assert all(abs(f['x']-ordered[0]['x'])<.01 for f in ordered)
   assert all(b['y']-a['y']-a['h']>=gap-.01 for a,b in zip(ordered,ordered[1:]))
   assert ordered[0]['y']>=top-.01 and ordered[-1]['y']+ordered[-1]['h']<=bottom+.01
   count+=1
 for pi,pg in enumerate(paper):
  for fi,f in enumerate(pg['fields']):
   if not f['n'].startswith(('b_q_p12','b_q_p13')):assert f==before[pi]['fields'][fi],f['n']
 temp=Path(str(path)+'.vertical.tmp')
 with temp.open('wb')as out:writer.write(out)
 temp.replace(path);(ROOT/'paper-data.js').write_text('const PAPER='+json.dumps(paper,ensure_ascii=False,separators=(',',':'))+';\n')
 check=PdfReader(path);fields=check.get_fields();assert len(check.pages)==22
 for pgindex in [11,12]:
  for f in paper[pgindex]['fields']:
   if f['n'].startswith('b_q_'):
    assert f['n']in fields;r=next(a.get_object()['/Rect']for a in check.pages[pgindex]['/Annots']if a.get_object().get('/T')==f['n']);assert abs(float(r[0])-f['x'])<.01;assert abs(float(r[3])-(float(writer.pages[pgindex].mediabox.height)-f['y']))<.01
 print(f'PASS: {count} grupos na vertical, espaçados, sem sobreposição e sem alterar observações ou dados.')
if __name__=='__main__':patch(Path(sys.argv[1]))
