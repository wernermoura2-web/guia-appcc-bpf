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
assert len(rows)==112
blue=HexColor('#075a9c'); gray=HexColor('#526b7c'); border=HexColor('#aabfcc')
style=ParagraphStyle('text',fontName='Helvetica',fontSize=9,leading=12,textColor=HexColor('#193244'),spaceAfter=7)
small=ParagraphStyle('small',parent=style,fontSize=8,leading=10)
h2=ParagraphStyle('h2',parent=style,fontName='Helvetica-Bold',fontSize=12,leading=16,textColor=blue,spaceBefore=10)
def para(text,sty=style):return Paragraph(escape(text).replace('\n','<br/>'),sty)

from review_table_pdf import build_review_table
build_review_table(out/'Tabela_Revisao_APPCC_IA_Probabilidade_Editavel.pdf',rows,cfg['pesos'])

W,H=A4;M=32
pcc=[r for r in rows if r[2]['cat']=='PCC'];assert len(pcc)==9
story=[para('Avaliação preliminar dos PCC',ParagraphStyle('title',parent=h2,fontSize=18,leading=22)),para('Revisão de 02/11/2026 - alinhada às classificações adotadas no guia atual.'),para('O guia adota nove frases únicas como PCC. As mesmas frases podem aparecer em mais de uma linha de produção. A classificação deve ser confirmada para o processo real, com perigo, medida de controle, limite crítico validado, monitoramento, correção, destino do produto e registros definidos.'),para('As orientações e os fundamentos abaixo são os vigentes no guia. Não se atribui um limite numérico sem a validação específica do processo.')]
for item,i,f in pcc:
    story.extend([para(f"{item['code']} - F{i} | PCC | P={f['P']} | NC=5",h2),para(f['texto']),para('Fundamento da classificação: '+f.get('fundamento',f.get('consideracao',''))),para('Orientação ao inspetor: '+f['orientacao'])])
    if item['code']=='4.6.8':story.append(para('Condição de confirmação: identificar a etapa efetiva de descontaminação das tampas. A frase geral de proteção, isoladamente, não estabelece um PCC mensurável.'))
    if item['code']=='4.10.4':story.append(para('Condição de confirmação: verificar retenção física ou sistêmica do lote até a decisão de liberação. Ensaios por amostragem são verificação; sua realização isolada não demonstra eliminação do perigo em todo o lote.'))
story.extend([para('Higienização e comprovação da eficácia',h2),para('Captação, condução, reservatórios e sala de envase: manter as medidas adicionais de controle adotadas no guia, com critérios documentados de liberação por análises microbiológicas e/ou ATP, conforme o processo. ATP verifica condições de limpeza e não equivale a um resultado microbiológico. Na classificação atual, a higienização da captação (4.1.3 F1), condução (4.2.7 F1) e reservatórios (4.3.5 F1) e a higienização da sala e equipamentos de envase (4.7.8 F1) são PCC. No envase, abranger reservatório/pulmão, conexões, tubulações, mangueiras e bicos. Condutividade em linha é medida complementar ao monitoramento validado do enxágue; não substitui controle específico de saneante ou microbiologia; POP e registros de rotina permanecem identificados como POP ou PPR nas frases correspondentes.'),para('Desmonte dos equipamentos de envase — PC de apoio',h2),para('4.7.8 F2: PC (NC=3, P=3) de apoio ao PCC de higienização 4.7.8 F1. Verificar desmonte conforme necessidade e frequência validadas, acesso às superfícies, inspeção, remontagem higiênica e liberação no PCC; não é um PCC independente.'),para('Enxágue de embalagens descartáveis',h2),para('Manter a orientação complementar de verificar filtro microbiológico no ar comprimido das sopradoras de pré-formas, sua especificação, manutenção, troca e registros. Essa verificação complementa a avaliação do enxágue e não cria uma nova frase PCC.'),para('Registro mínimo por PCC',h2),para('Identificação do perigo e da etapa; justificativa da classificação; validação da medida e dos limites; parâmetro, método, frequência e responsável pelo monitoramento; registros; bloqueio e destino dos lotes afetados; correção, ação corretiva, verificação e autorização de liberação.'),para('Fonte: configuração e orientações do Guia Estadual BPF/APPCC, revisão bpf-appcc-adotado-20261101. Esta avaliação não altera as respostas das inspeções nem substitui a validação na envasadora.',small)])
def footer(can,doc):
    can.setFont('Helvetica',8);can.setFillColor(gray);can.drawString(M,22,'Guia Estadual BPF/APPCC - revisão 02/11/2026');can.drawRightString(W-M,22,str(doc.page))
grouped=[];block=[]
for flow in story:
    is_heading=isinstance(flow,Paragraph) and flow.style.name=='h2'
    if is_heading and block:grouped.append(KeepTogether(block));block=[]
    if is_heading or block:block.append(flow)
    else:grouped.append(flow)
if block:grouped.append(KeepTogether(block))
SimpleDocTemplate(str(out/'Avaliacao_Preliminar_PCC_Guia_Estadual.pdf'),pagesize=A4,rightMargin=M,leftMargin=M,topMargin=30,bottomMargin=40).build(grouped,onFirstPage=footer,onLaterPages=footer)
print(json.dumps({'phrases':len(rows),'pcc':len(pcc),'output':str(out)}))

# Keep the terminology consistent in the existing decision-tree handouts.
import fitz
for name in ['Arvore_Decisao_APPCC.pdf','APPCC_Fluxogramas_Passos_1_2_3.pdf']:
    target=out/name
    if not target.exists():continue
    doc=fitz.open(target);changed=False
    for page in doc:
        hits=page.search_for('PPHO')
        if not hits:continue
        for rect in hits:page.add_redact_annot(rect,fill=(1,1,1))
        page.apply_redactions(images=0,graphics=0)
        for rect in hits:
            page.insert_text((rect.x0,rect.y1-rect.height*.19),'POP',fontsize=rect.height*.7,fontname='helv',color=(0,0,0))
        changed=True
    if changed:
        temp=target.with_suffix('.new.pdf');doc.save(temp,garbage=4,deflate=True);doc.close();temp.replace(target)
    else:doc.close()

from current_materials import build
build(out,cfg,rows)
