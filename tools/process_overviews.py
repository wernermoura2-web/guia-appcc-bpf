"""CQ-style process summaries; preserve the canonical fields, JS and note rectangles."""
from pathlib import Path
import json,sys,fitz
from pypdf import PdfReader
from PIL import Image
from process_metadata import apply
ROOT=Path(__file__).resolve().parents[1]
def patch(path):
 cfg=apply(json.loads((ROOT/'config.js').read_text().split('=',1)[1].strip().rstrip(';')),ROOT)
 paper=json.loads((ROOT/'paper-data.js').read_text().split('=',1)[1].strip().rstrip(';'))
 before=PdfReader(path);before_fields=before.get_fields();signature={k:(v.get('/FT'),v.get('/V'))for k,v in before_fields.items()}
 doc=fitz.open(path);blue=(.86,.91,.94);pale=(.94,.96,.97);line=(.52,.6,.65)
 for page in range(13):
  pg=doc[page];entries={c['code']:c for c in cfg['itens'].values()if c['page']==page};codes=list(entries)
  limit=min(f['y'] for f in paper[page]['fields']if f['n'].startswith('obs_gerais'))-19 if page<11 else 775
  starts=[]
  for code in codes:
   rects=[r for r in pg.search_for(code)if r.x0<61 and r.y0<limit and (r.y0>550 if page>=11 else True)]
   if not rects:raise ValueError(('Description code not found',page,code))
   starts.append(max(r.y0 for r in rects))
  top=min(starts)-(2 if page>=11 else 9);assert top<limit
  # No live widgets may be touched by the overview.
  assert not any(f['x']<581 and f['x']+f['w']>14 and f['y']<limit and f['y']+f['h']>top for f in paper[page]['fields']if not f['n'].startswith('b_')or f['y']>=0),(page,top,limit)
  pg.add_redact_annot(fitz.Rect(14,top,581,limit),fill=(1,1,1));pg.apply_redactions(images=0,graphics=1,text=0)
  height=min(30,(limit-top)/len(codes));y=top
  for code in codes:
   c=entries[code];r=fitz.Rect(14,y,581,y+height);pg.draw_rect(r,color=line,width=.4);pg.draw_rect((14,y,60,y+height),color=line,fill=pale,width=.4)
   assert pg.insert_textbox((15,y+2,59,y+height-1),c['processId']+'\n'+code,fontsize=6,fontname='hebo',align=1)>=0,(page,code)
   title=c['title']+" - consultar F."
   assert pg.insert_textbox((63,y+2,579,y+height-1),title,fontsize=7,fontname='hebo')>=0,(page,code,title)
   refs='Referência normativa: '+c['frases'][0]['ref']
   assert pg.insert_textbox((63,y+12,579,y+height-1),refs,fontsize=6,fontname='helv')>=0,(page,code,refs)
   y+=height
  print(f'Overview page {page+1}: {len(codes)} codes; note fields unchanged')
 temp=Path(str(path)+'.overview.tmp');doc.save(temp,garbage=0,deflate=True);doc.close();temp.replace(path)
 check=PdfReader(path);after_fields=check.get_fields();assert len(check.pages)==22;assert signature=={k:(v.get('/FT'),v.get('/V'))for k,v in after_fields.items()}
 doc=fitz.open(path)
 for page in range(13):
  pg=doc[page];pix=pg.get_pixmap(matrix=fitz.Matrix(1.6,1.6),annots=False);dest=ROOT/paper[page]['image'];image=Image.frombytes('RGB',[pix.width,pix.height],pix.samples)
  image.save(dest,**({'quality':92}if dest.suffix=='.webp'else{}))
 print('PASS 22 pages, native scripts and canonical fields retained; 13 backgrounds updated')
if __name__=='__main__':patch(Path(sys.argv[1]))
