"""Build public review references from the guide's current configuration."""
import json, math, re
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle, PageBreak, KeepTogether

ROOT=Path(__file__).resolve().parents[1]
if not (ROOT/'config.js').exists():
    ROOT=Path.cwd()
cfg_path=ROOT/'config.js'
if not cfg_path.exists():cfg_path=Path('tmp/calc-current-config.js')
cfg=json.loads(re.sub(r'^const CFG=','',cfg_path.read_text()).strip().rstrip(';'))
out=ROOT if (ROOT/'config.js').exists() else Path('tmp/reference-pdfs')
out.mkdir(parents=True,exist_ok=True)
items={}
for c in cfg['itens'].values():items.setdefault(c['code'],c)
rows=[(c,i+1,f) for c in items.values() for i,f in enumerate(c['frases'])]
assert len(rows)==76
blue=HexColor('#075a9c'); gray=HexColor('#526b7c'); border=HexColor('#aabfcc')
style=ParagraphStyle('text',fontName='Helvetica',fontSize=9,leading=12,textColor=HexColor('#193244'),spaceAfter=7)
small=ParagraphStyle('small',parent=style,fontSize=8,leading=10)
h2=ParagraphStyle('h2',parent=style,fontName='Helvetica-Bold',fontSize=12,leading=16,textColor=blue,spaceBefore=10)
def para(text,sty=style):return Paragraph(escape(text).replace('\n','<br/>'),sty)

path=out/'Tabela_Revisao_APPCC_IA_Probabilidade_Editavel.pdf'
c=canvas.Canvas(str(path),pagesize=A4);c.setTitle('Tabela de revisão BPF/APPCC - 01/11/2026')
W,H=A4;M=32;body=W-2*M
def text(text,x,y,width,sty=style):
    p=para(text,sty);_,hh=p.wrap(width,H);p.drawOn(c,x,y-hh);return hh
def field(name,label,x,y,w,h=24,multi=False):
    c.setFont('Helvetica',8);c.setFillColor(gray);c.drawString(x,y,label)
    c.acroForm.textfield(name=name,tooltip=label,x=x,y=y-h-5,width=w,height=h,value='',fontName='Helvetica',fontSize=9,borderColor=border,fillColor=white,textColor=HexColor('#193244'),borderWidth=.6,forceBorder=True,fieldFlags='multiline' if multi else '')
for page in range(math.ceil(len(rows)/2)):
    c.setFillColor(blue);c.setFont('Helvetica-Bold',14);c.drawString(M,H-35,'Tabela de revisão BPF/APPCC')
    text('Base do guia: 01/11/2026. PPR=1; POP=2; PC=3; PPRO=4; PCC=5. Campos de sugestão em branco.',M,H-47,body,small)
    field('revisor_'+str(page),'Revisor',M,H-77,body*.72,20)
    field('data_'+str(page),'Data',M+body*.75,H-77,body*.25,20)
    for j,(item,idx,f) in enumerate(rows[page*2:page*2+2]):
        top=H-123-j*326
        c.setStrokeColor(border);c.rect(M,top-311,body,311,fill=0)
        c.setFillColor(blue);c.setFont('Helvetica-Bold',10);c.drawString(M+10,top-18,f"Item {item['code']} - F{idx} | Atual: {f['cat'].replace('PPHO','POP')} | P={f['P']} | NC x P={cfg['pesos'][f['cat']]*f['P']}")
        hh=text(f['texto'],M+10,top-29,body-20,small)
        assert hh<95,(item['code'],hh)
        field(f'categoria_{page}_{j}','Categoria sugerida',M+10,top-129,body*.39,22)
        field(f'probabilidade_{page}_{j}','P sugerida (1 a 5)',M+body*.43,top-129,body*.25,22)
        field(f'perigo_medida_{page}_{j}','Perigo e medida de controle',M+10,top-170,body-20,37,True)
        field(f'fundamento_{page}_{j}','Fundamento da sugestão',M+10,top-223,body-20,30,True)
        field(f'inspetor_{page}_{j}','Frase ao inspetor',M+10,top-269,body-20,25,True)
    c.setFont('Helvetica',8);c.setFillColor(gray);c.drawRightString(W-M,20,f'01/11/2026 | Página {page+1} de 38');c.showPage()
c.save()

pcc=[r for r in rows if r[2]['cat']=='PCC'];assert len(pcc)==5
story=[para('Avaliação preliminar dos PCC',ParagraphStyle('title',parent=h2,fontSize=18,leading=22)),para('Revisão de 01/11/2026 - alinhada às classificações adotadas no guia atual.'),para('O guia adota cinco frases únicas como PCC. As mesmas frases podem aparecer em mais de uma linha de produção. A classificação deve ser confirmada para o processo real, com perigo, medida de controle, limite crítico validado, monitoramento, correção, destino do produto e registros definidos.'),para('As orientações e os fundamentos abaixo são os vigentes no guia. Não se atribui um limite numérico sem a validação específica do processo.')]
for item,i,f in pcc:
    story.extend([para(f"{item['code']} - F{i} | PCC | P={f['P']} | NC=5",h2),para(f['texto']),para('Fundamento da classificação: '+f.get('fundamento',f.get('consideracao',''))),para('Orientação ao inspetor: '+f['orientacao'])])
    if item['code']=='4.6.8':story.append(para('Condição de confirmação: identificar a etapa efetiva de descontaminação das tampas. A frase geral de proteção, isoladamente, não estabelece um PCC mensurável.'))
    if item['code']=='4.10.4':story.append(para('Condição de confirmação: verificar retenção física ou sistêmica do lote até a decisão de liberação. Ensaios por amostragem são verificação; sua realização isolada não demonstra eliminação do perigo em todo o lote.'))
story.extend([para('Higienização e comprovação da eficácia',h2),para('Captação, condução, reservatórios e sala de envase: manter as medidas adicionais de controle adotadas no guia, com critérios documentados de liberação por análises microbiológicas e/ou ATP, conforme o processo. ATP verifica condições de limpeza e não equivale a um resultado microbiológico. Na classificação atual, essas medidas de higienização são PPRO; POP e registros de rotina permanecem identificados como POP ou PPR nas frases correspondentes.'),para('Enxágue de embalagens descartáveis',h2),para('Manter a orientação complementar de verificar filtro microbiológico no ar comprimido das sopradoras de pré-formas, sua especificação, manutenção, troca e registros. Essa verificação complementa a avaliação do enxágue e não cria uma nova frase PCC.'),para('Registro mínimo por PCC',h2),para('Identificação do perigo e da etapa; justificativa da classificação; validação da medida e dos limites; parâmetro, método, frequência e responsável pelo monitoramento; registros; bloqueio e destino dos lotes afetados; correção, ação corretiva, verificação e autorização de liberação.'),para('Fonte: configuração e orientações do Guia Estadual BPF/APPCC, revisão bpf-appcc-adotado-20261101. Esta avaliação não altera as respostas das inspeções nem substitui a validação na envasadora.',small)])
def footer(can,doc):
    can.setFont('Helvetica',8);can.setFillColor(gray);can.drawString(M,22,'Guia Estadual BPF/APPCC - revisão 01/11/2026');can.drawRightString(W-M,22,str(doc.page))
grouped=[];block=[]
for flow in story:
    is_heading=isinstance(flow,Paragraph) and flow.style.name=='h2'
    if is_heading and block:grouped.append(KeepTogether(block));block=[]
    if is_heading or block:block.append(flow)
    else:grouped.append(flow)
if block:grouped.append(KeepTogether(block))
SimpleDocTemplate(str(out/'Avaliacao_Preliminar_PCC_Guia_Estadual.pdf'),pagesize=A4,rightMargin=M,leftMargin=M,topMargin=30,bottomMargin=40).build(grouped,onFirstPage=footer,onLaterPages=footer)
print(json.dumps({'phrases':len(rows),'pcc':len(pcc),'output':str(out)}))
