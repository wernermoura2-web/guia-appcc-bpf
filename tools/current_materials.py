"""Publish calculation and decision references from the current guide only."""
from html.parser import HTMLParser
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.platypus import SimpleDocTemplate,Paragraph,Table,TableStyle,Spacer,PageBreak
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

def build(root,cfg,rows):
 styles=getSampleStyleSheet();styles.add(ParagraphStyle('small',fontSize=7,leading=9));styles['BodyText'].fontSize=9;styles['BodyText'].leading=12
 def p(t,style='BodyText'):return Paragraph(escape(t),styles[style])
 def table(data):
  n=max(map(len,data));width=(A4[0]-60)/n
  data=[[p(v,'small')for v in row]+[p('','small')]*(n-len(row))for row in data]
  t=Table(data,colWidths=[width]*n,repeatRows=1,hAlign='LEFT');t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#dcebf3')),('GRID',(0,0),(-1,-1),.4,colors.HexColor('#9eb9c8')),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]));return t
 def footer(c,d):c.setFont('Helvetica',8);c.drawString(30,20,'Guia BPF/APPCC | 01/11/2026 | Captação e reservatórios: frases individualizadas');c.drawRightString(A4[0]-30,20,str(d.page))
 def pdf(name,story):SimpleDocTemplate(str(root/name),pagesize=A4,leftMargin=30,rightMargin=30,topMargin=30,bottomMargin=38).build(story,onFirstPage=footer,onLaterPages=footer)
 class Content(HTMLParser):
  def __init__(self):super().__init__();self.story=[];self.capture=None;self.text=[];self.inmain=False;self.rows=None;self.row=None
  def handle_starttag(self,tag,attrs):
   if tag=='main':self.inmain=True
   if not self.inmain:return
   if tag=='table':self.rows=[]
   if tag=='tr':self.row=[]
   if tag in ['h1','h2','h3','p','summary','th','td']:self.capture=tag;self.text=[]
   if tag=='br':self.text.append(' ')
  def handle_data(self,data):
   if self.capture:self.text.append(data)
  def handle_endtag(self,tag):
   if tag==self.capture:
    text=''.join(self.text).strip()
    if tag in ['th','td']:self.row.append(text)
    elif text:self.story.extend([p(text,'Heading1'if tag=='h1'else'Heading2'if tag in ['h2','h3','summary']else'BodyText'),Spacer(1,6)])
    self.capture=None
   if tag=='tr'and self.row is not None:self.rows.append(self.row);self.row=None
   if tag=='table':self.story.extend([table(self.rows),Spacer(1,12)]);self.rows=None
   if tag=='main':self.inmain=False
 parser=Content();parser.feed((root/'calculo-atual.html').read_text());pdf('Calculos_APPCC_BPF.pdf',parser.story)
 story=[p('Árvore de decisão e classificações vigentes','Title'),p('Referência de revisão: 88 frases do guia atual. A classificação adotada exige confirmação das condições reais da unidade. PC é categoria de apoio usada neste guia.'),p('1. Identificar o perigo e a medida','Heading2'),p('Identificar a etapa, a exposição, a consequência da falha e a medida concreta. Verificar se o perigo é significativo e se existe controle posterior comprovadamente eficaz.'),p('2. Distinguir os controles','Heading2'),table([['Categoria','Critério de avaliação'],['PPR','Condição básica e suporte: estrutura, pessoal, capacitação e registros.'],['POP','Procedimento operacional padronizado de rotina, inclusive higienização.'],['PC','Controle específico de apoio e verificação, conforme a convenção do guia.'],['PPRO','Controle operacional de perigo significativo, com critério de ação e monitoramento oportuno.'],['PCC','Etapa crítica com limite validado, monitoramento oportuno, correções e controle do produto afetado.']]),p('3. Confirmar antes de concluir','Heading2'),p('Demonstrar eficácia, critério ou limite, método e frequência de monitoramento, responsáveis, correções, destino do produto e registros. Informação ausente mantém a conclusão pendente. Análise microbiológica ou ATP só deve ser usada conforme protocolo e aplicação; ATP não equivale a ensaio microbiológico.'),p('Controles individualizados','Heading2'),p('4.2.7 e 4.3.5: F1 higienização, F2 registros e F3 capacitação. 4.7.4: F1 piso, F2 ralo, F3 luminárias e F4 ventilação. 4.7.5: F1 acesso, F2 lavatório/torneira, F3 sabonete/antisséptico, F4 secagem e F5 execução da higiene das mãos.'),p('Separação do item 4.6.11','Heading2'),p('F1: execução da higienização das embalagens (POP). F2: registros da limpeza e desinfecção (PPR). F3: capacitação dos executores (PPR).'),p('Separação do item 4.3.3','Heading2'),p('F1: extravasor protegido. F2: esvaziamento inferior. F3: verificação, troca e registros dos elementos filtrantes. F4: filtro de ar microbiológico. F5: válvula de retenção ou fecho hídrico. F6: torneira específica de amostragem.'),p('Separação do item 4.1.3','Heading2'),p('F1: higienização e controles adicionais de liberação (PPRO). F2: capacitação comprovada dos executores (PPR). F3: registros datados da limpeza e desinfecção (PPR). A ausência do registro não demonstra, por si, que o perigo foi eliminado ou que existe um PCC.'),PageBreak(),p('Classificações e fundamentos por frase','Heading1')]
 data=[['Item / frase','Categoria / P','Fundamento da classificação']]
 for c,i,f in rows:data.append([c['code']+' F'+str(i),f['cat'].replace('PPHO','POP')+' / '+str(f['P']),f.get('fundamento',f.get('consideracao',''))])
 story.append(table(data));pdf('Arvore_Decisao_APPCC.pdf',story)
 print('Memória PDF e árvore alinhadas às 88 frases vigentes.')
