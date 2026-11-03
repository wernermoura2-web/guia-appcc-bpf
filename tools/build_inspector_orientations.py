"""Build the published inspector guidance from the current guide configuration."""
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether

NAMES={'4.1':'Captação','4.2':'Condução','4.3':'Reservatórios','4.5':'Recepção e armazenamento de insumos','4.6':'Higienização de embalagens e tampas','4.7':'Envase e fechamento','4.10':'Controle de qualidade','4.11':'Responsáveis e manipuladores'}

def scoring_note(item):
    if item['code']=='4.6.11':
        return 'F1: execução da higienização. F2: capacitação (antiga F3). A antiga F2 de registros deixou de ser pontuada separadamente; conferir os registros como evidência da execução da F1.'
    groups=item.get('scoringGroups',[])
    if not groups:return ''
    covered={n for group in groups for n in group}
    independent=[n+1 for n in range(len(item['frases'])) if n+1 not in covered]
    return 'Responder cada frase individualmente. Pontuação APPCC: '+'; '.join('média de '+', '.join('F'+str(n) for n in group) for group in groups)+'.'+(' Pontuação independente: '+', '.join('F'+str(n) for n in independent)+'.' if independent else '')+' NA fica fora do divisor, quando permitido e justificado. Não dispensar evidências de qualquer requisito por haver agrupamento.'

def build(root,cfg):
    root=Path(root)
    import json
    metadata=json.loads((root/'process-display-data.json').read_text())
    items={}
    for item in cfg['itens'].values():items.setdefault(item['code'],item)
    rows=sum(len(item['frases'])for item in items.values())
    blue=colors.HexColor('#075a9c');ink=colors.HexColor('#193244');muted=colors.HexColor('#526b7c')
    styles={
        'title':ParagraphStyle('title',fontName='Helvetica-Bold',fontSize=19,leading=23,textColor=blue,spaceAfter=12),
        'process':ParagraphStyle('process',fontName='Helvetica-Bold',fontSize=16,leading=20,textColor=blue,spaceAfter=12),
        'item':ParagraphStyle('item',fontName='Helvetica-Bold',fontSize=11,leading=14,textColor=blue,spaceBefore=12,spaceAfter=5),
        'phrase':ParagraphStyle('phrase',fontName='Helvetica-Bold',fontSize=9.2,leading=12,textColor=ink,spaceAfter=5),
        'body':ParagraphStyle('body',fontName='Helvetica',fontSize=9.2,leading=12.4,textColor=ink,spaceAfter=6),
        'small':ParagraphStyle('small',fontName='Helvetica',fontSize=8,leading=10.5,textColor=muted,spaceAfter=6),
        'note':ParagraphStyle('note',fontName='Helvetica',fontSize=9,leading=12,textColor=ink,backColor=colors.HexColor('#fff7e7'),borderPadding=7,spaceBefore=8,spaceAfter=12),
    }
    def p(text,style='body'):return Paragraph(escape(str(text)).replace('\n','<br/>'),styles[style])
    story=[p('Orientações aos inspetores','title'),p('Guia Estadual BPF/APPCC - versão-base vigente, alinhada à revisão de médias de 02/11/2026. '+str(rows)+' frases, organizadas por processo.','small'),p('Avaliar cada frase e registrar evidência objetiva: documento/registro, identificação, data, responsável, unidade ou circuito e constatação. Confrontar os documentos com a operação observada. A ausência de evidência deve ser registrada; não presumir que o controle foi executado.'),p('As médias alteram a pontuação APPCC informativa. O resultado BPF original continua por item: qualquer Não torna o item Não; Sim exige todas as frases aplicáveis atendidas. Usar NA somente quando permitido e justificado. Frases fora dos grupos pontuam separadamente.'),p('As orientações técnicas e os fundamentos de cada frase aparecem nas páginas seguintes. Edições pessoais salvas no aparelho são preservadas no editor; para incluí-las na impressão, usar “Imprimir todas juntas” na página de revisão das orientações.','small'),p('Grupos de média','item')]
    table_rows=[[p('Item','phrase'),p('Grupos com média','phrase'),p('Independentes','phrase')]]
    for item in items.values():
        groups=item.get('scoringGroups',[])
        if not groups:continue
        covered={n for g in groups for n in g};independent=[n+1 for n in range(len(item['frases']))if n+1 not in covered]
        table_rows.append([p(item['code'],'small'),p('; '.join(' + '.join('F'+str(n)for n in g)for g in groups),'small'),p(', '.join('F'+str(n)for n in independent)or'Nenhuma','small')])
    table=Table(table_rows,colWidths=[55,345,123],repeatRows=1,hAlign='LEFT')
    table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e5eff5')),('GRID',(0,0),(-1,-1),.4,colors.HexColor('#b5c7d3')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
    story.extend([table,Spacer(1,10),p('4.6.11: '+scoring_note(items['4.6.11']),'note')])
    current=None
    for item in items.values():
        if item['proc']!=current:
            story.extend([PageBreak(),p(item['proc']+' - '+NAMES[item['proc']],'process')]);current=item['proc']
        meta=metadata.get(str(item['page'])+':'+item['code'],{})
        heading=item['code']+(' - '+meta.get('title','') if meta.get('title')else'')
        group_note=scoring_note(item)
        lead=[p(heading,'item')]
        if group_note:lead.append(p(group_note,'note'))
        for index,f in enumerate(item['frases'],1):
            cat=f['cat'].replace('PPHO','POP');weight=cfg['pesos'][f['cat']]*f['P']
            block=[p('F'+str(index)+' | '+cat+' | NC='+str(cfg['pesos'][f['cat']])+' | P='+str(f['P'])+' | NC × P bruto='+str(weight),'phrase'),p('Requisito: '+f['texto']),p('Orientação ao inspetor: '+f.get('orientacao','')),p('Fundamento da classificação: '+f.get('fundamento',f.get('consideracao','')),'small')]
            if f.get('ref'):block.append(p('Referência: '+f['ref'],'small'))
            if index==1:block=lead+block
            block.append(Spacer(1,7));story.append(KeepTogether(block))
    def footer(canvas,doc):
        canvas.setFont('Helvetica',8);canvas.setFillColor(muted);canvas.drawString(36,22,'Guia Estadual BPF/APPCC | Orientações aos inspetores');canvas.drawRightString(A4[0]-36,22,str(doc.page))
    output=root/'Orientacoes_Aos_Inspetores_Atualizadas.pdf'
    SimpleDocTemplate(str(output),pagesize=A4,leftMargin=36,rightMargin=36,topMargin=34,bottomMargin=38,title='Orientações aos inspetores - Guia Estadual BPF/APPCC').build(story,onFirstPage=footer,onLaterPages=footer)
    print('Orientações aos inspetores:',rows,'frases;',output.name)

if __name__=='__main__':
    import json
    root=Path(__file__).resolve().parents[1]
    cfg=json.loads((root/'config.js').read_text()[10:].strip().rstrip(';'))
    build(root,cfg)
