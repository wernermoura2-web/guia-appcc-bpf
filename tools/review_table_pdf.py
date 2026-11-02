from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor,white
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import simpleSplit
from xml.sax.saxutils import escape
from review_analysis import assessment

def build_review_table(path,rows,weights):
    c=canvas.Canvas(str(path),pagesize=A4);W,H=A4;M=30;BW=W-2*M
    blue=HexColor('#173f56');light=HexColor('#edf4f8');line=HexColor('#b4c8d4')
    c.setTitle('Revisão BPF/APPCC x Probabilidade — análise preenchida')
    def box(x,top,w,h):
        c.setFillColor(light);c.setStrokeColor(line);c.rect(x,top-h,w,h,fill=1,stroke=1)
    def p(t,x,top,w,size=6.6,bold=False,maxh=100):
        sty=ParagraphStyle('x',fontName='Helvetica-Bold' if bold else 'Helvetica',fontSize=size,leading=size*1.16,textColor=blue)
        while True:
            q=Paragraph(escape(str(t)).replace('\n','<br/>'),sty);_,hh=q.wrap(w,1000)
            if hh<=maxh or sty.fontSize<=5.2:break
            sty.fontSize-=.2;sty.leading=sty.fontSize*1.16
        q.drawOn(c,x,top-hh);return hh
    def band(t,top,h=14):
        c.setFillColor(blue);c.rect(M,top-h,BW,h,fill=1,stroke=0);c.setFillColor(white);c.setFont('Helvetica-Bold',7);c.drawString(M+5,top-h+4,t)
    def field(name,x,top,w,h=14,multi=False,value='',font=7):
        value=str(value).replace("—","-").replace("–","-")
        if multi and value:
            while True:
                lines=simpleSplit(value,'Helvetica',font,w-4)
                if len(lines)*font*1.2<=h-2 or font<=4.2:break
                font-=.2
            value='\n'.join(lines)
        c.acroForm.textfield(name=name,x=x,y=top-h,width=w,height=h,value=str(value).replace("—","-").replace("–","-"),fontName='Helvetica',fontSize=font,borderColor=line,borderWidth=.5,fillColor=white,textColor=blue,fieldFlags='multiline' if multi else '',forceBorder=True)
    process={'4.1':'CAPTAÇÃO','4.2':'CONDUÇÃO','4.3':'RESERVATÓRIOS','4.5':'RECEPÇÃO','4.6':'HIGIENIZAÇÃO','4.7':'ENVASE','4.10':'CONTROLE DE QUALIDADE','4.11':'RESPONSABILIDADE E MANIPULADORES'}
    groups=[('Tabela 1 - Triagem A-E',[('A','O perigo é significativo nesta frase?'),('B','Existe medida de controle prevista?'),('C','A etapa foi concebida para controlar o perigo?'),('D','O perigo pode atingir nível inaceitável?'),('E','Há barreira posterior comprovadamente eficaz?')]),('Tabela 2 - Tipo de controle F-I',[('F','Controle operacional de perigo significativo?'),('G','Procedimento operacional ou de higiene?'),('H','Condição básica, estrutura ou capacitação?'),('I','Controle específico de apoio e verificação?')]),('Decisão Q1-Q4',[('Q1','A medida é necessária neste passo?'),('Q2','A implementação está comprovada?'),('Q3','A falha compromete a segurança do produto?'),('Q4','Há limite crítico validado e monitoramento oportuno?')])]
    for n,(item,i,f) in enumerate(rows,1):
        tag=f"p{n:02d}";cat=f['cat'].replace('PPHO','POP');a=assessment(item,i,f)
        band('',819,24)
        c.setFillColor(white);c.setFont('Helvetica-Bold',8);c.drawString(M+5,809,'REVISÃO BPF/APPCC x PROBABILIDADE - ANÁLISE PREENCHIDA')
        c.setFillColor(white);c.setFont('Helvetica',6);c.drawString(M+5,798,'Água mineral natural e água natural | Guia Estadual - Rio de Janeiro')
        p('Revisor:',M,782,35,7);field(tag+'_revisor',M+39,785,240,18)
        p('Data:',M+290,782,25,7);field(tag+'_data',M+320,785,105,18)
        band(f"{process[item['proc']]} | ITEM {item['code']} | FRASE {i}",756,17)
        box(M,739,BW,86)
        p('Frase: '+f['texto'],M+5,734,BW-10,7,maxh=43)
        p('Procedimento sugerido: '+a['procedure'],M+5,687,BW-10,6.5)
        p('Revisão do nome do procedimento:',M+5,675,BW-10,6.4,bold=True);field(tag+'_procedimento',M+5,665,BW-10,10,value=a['procedure'],font=6.5)
        half=(BW-4)/2
        box(M,649,half,66);box(M+half+4,649,half,66)
        p('Evidências e orientação vigentes no guia',M+4,645,half-8,6.5,True)
        p(f['orientacao'],M+4,633,half-8,6.3,maxh=46)
        p('Revisão das evidências / orientação ao inspetor',M+half+8,645,half-8,6.4,True)
        field(tag+'_evidencias_revisao',M+half+8,631,half-8,44,True,value=f['orientacao'],font=6.1)
        cols=[M,M+BW*.25,M+BW*.42,M+BW*.75];widths=[BW*.25,BW*.17,BW*.33,BW*.25]
        for x,w,title in zip(cols,widths,['BPF/APPCC atual','P atual','BPF/APPCC - revisão','P - revisão']):box(x,579,w,33);p(title,x+4,575,w-8,6.3,True)
        p(f'{cat} (NC={weights[f["cat"]]})',cols[0]+4,562,widths[0]-8,8,True);p(f['P'],cols[1]+4,562,widths[1]-8,8,True)
        field(tag+'_appcc',cols[2]+4,564,widths[2]-8,14,value=a['cat']);field(tag+'_probabilidade',cols[3]+4,564,widths[3]-8,14,value=a['p'])
        band('ANÁLISE DO CONTROLE E COMPROVAÇÃO DA EXECUÇÃO',541)
        p('S = Sim | N = Não | NA = rota não percorrida/não aplicável | ND = não demonstrado. Respostas para revisão na unidade.',M,523,BW,6.2)
        for j,title in enumerate(['Perigo identificado no produto','Medida preventiva / controle']):
            x=M+j*(half+4);box(x,510,half,58);p(title,x+4,506,half-8,6.4,True);field(tag+('_perigo' if j==0 else '_controle'),x+4,493,half-8,37,True,value=a['hazard'] if j==0 else a['measure'],font=5.8)
        gw=(BW-8)/3
        for j,(title,questions) in enumerate(groups):
            x=M+j*(gw+4);box(x,448,gw,174);p(title,x+4,444,gw-8,6.4,True)
            rh=152/len(questions)
            for k,(letter,question) in enumerate(questions):
                top=429-k*rh;p(letter+' '+question,x+4,top,gw-29,5.8,True,maxh=15)
                answer,reason=(a['triage'] if j==0 else a['typeq'] if j==1 else a['decision'])[letter]
                field(tag+'_resposta_'+letter,x+gw-22,top+1,17,12,value=answer,font=6)
                p(reason,x+4,top-16,gw-8,5.3,maxh=rh-17)
        band('Tabela 3 - Requisitos de validação: confirmar por unidade e justificar NA',270)
        validation=['Eficácia','Critério / limite','Monitoramento','Correção','Destino do produto','Registros e verificação']
        for k,title in enumerate(validation):
            x=M+(k%3)*(gw+4);top=253-(k//3)*38;box(x,top,gw,35);p(title,x+4,top-4,gw-27,6.2,True);ans,reason=a['validation'][k];field(tag+'_validacao_'+str(k),x+gw-22,top-3,17,11,value=ans,font=6);p(reason,x+4,top-17,gw-8,5.3,maxh=17)
        p('Fonte: Guia Estadual BPF/APPCC atual, configuração adotada em 01/11/2026. A obrigação de controle não comprova sua execução.',M,173,BW,6.1)
        box(M,159,BW,27);p('Evidências das inspeções / documentos consultados',M+4,156,BW-8,6.3,True);field(tag+'_evidencias_inspecao',M+4,146,BW-8,11,True,value=a['evidence'],font=5.5)
        box(M,128,BW,38);p('Fundamento da classificação vigente e condição de confirmação',M+4,125,BW-8,6.3,True);p(a['foundation'],M+4,114,BW-8,5.8,maxh=21)
        box(M,86,BW,25);p('Observações e premissas da revisão',M+4,83,BW-8,6.3,True);field(tag+'_observacoes',M+4,74,BW-8,10,True,value=a['notes'],font=5)
        p('PPR (1): pré-requisitos. POP (2): procedimento operacional padronizado, inclusive higienização. PC (3): ponto de controle. PPRO (4): pré-requisito operacional. PCC (5): ponto crítico de controle. P: escala ordinal 1–5, independente da categoria. A proposta e as respostas da árvore precisam de confirmação na unidade.',M,52,BW,6.1,maxh=27)
        p('Uma frase por página A4 | Análise preenchida em 01/11/2026 | Confirmar na unidade',M,18,BW-50,6)
        c.setFont('Helvetica',7);c.setFillColor(blue);c.drawRightString(W-M,12,f'{n} / {len(rows)}');c.showPage()
    c.save()
