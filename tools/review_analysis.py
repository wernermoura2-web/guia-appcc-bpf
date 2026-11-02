"""Technical pre-analysis; no unit-specific implementation or validation is presumed."""
PROCEDURES={
'4.1.1':'Conservação, drenagem e limpeza do entorno da captação','4.1.2':'Integridade da casa de proteção e coleta de amostras','4.1.3':'POP de higienização da captação e controle da liberação',
'4.2.2':'Qualificação dos materiais e conservação da canalização','4.2.7':'POP de higienização e liberação da canalização','4.2.8':'Desmonte, inspeção e correção da canalização','4.2.9':'POP de higienização da canalização',
'4.3.2':'Qualificação dos materiais e conservação do reservatório','4.3.3':'Proteção sanitária, filtragem de ar e manutenção do reservatório','4.3.4':'Inspeção interna e correção de falhas do reservatório','4.3.5':'POP de higienização e liberação do reservatório','4.3.6':'POP de higienização do reservatório',
'4.5.2':'Separação dos fluxos na recepção de insumos','4.5.3':'Inspeção, aceitação e reprovação dos insumos','4.5.4':'Avaliação individual e rejeição de embalagens retornáveis','4.5.6':'Segregação, devolução e destino dos insumos reprovados','4.5.8':'POP de recepção de embalagens',
'4.6.3':'Enxágue desinfetante automático de embalagens de primeiro uso','4.6.4':'POP de pré-lavagem de embalagens retornáveis','4.6.5':'Limpeza e desinfecção automáticas das embalagens retornáveis','4.6.6':'Enxágue, controle e teste de resíduos químicos','4.6.7':'Controle da água e do enxágue final das embalagens','4.6.8':'Descontaminação e proteção sanitária das tampas','4.6.9':'Transferência protegida e imediata das embalagens ao envase','4.6.10':'Controle da passagem de embalagens para a sala de envase','4.6.11':'POP de limpeza e desinfecção de embalagens e capacitação','4.6.12':'POP de higienização das embalagens',
'4.7.1':'Envase automático, fechamento e integridade da vedação','4.7.2':'Conservação e POP de higiene da sala de envase','4.7.3':'Controle da integração da gasificação à linha de envase','4.7.4':'Drenagem, ventilação e controle ambiental da sala de envase','4.7.5':'Controle de acesso e POP de higiene das mãos','4.7.6':'POP de troca e uso exclusivo de uniformes','4.7.8':'POP de higienização, desmonte e liberação da sala e equipamentos de envase',
'4.10.1':'Programa documentado de controle de qualidade','4.10.2':'Qualificação do laboratório e dos ensaios','4.10.3':'Verificação microbiológica e de contaminantes químicos','4.10.4':'Plano de amostragem, retenção e liberação de lotes','4.10.5':'Verificação da equivalência da água envasada com a fonte','4.10.6':'Investigação de desvios, correções e registros','4.12.6':'Qualificação e certificado por carga de dióxido de carbono',
'4.11.1':'Supervisão e capacitação dos manipuladores','4.11.2':'Designação e atribuições da responsabilidade pela industrialização','4.11.3':'Capacitação do responsável pela industrialização','4.11.4':'Gestão dos certificados de capacitação'}
HAZARDS={
'4.1.1':'B/F: ingresso de microrganismos e partículas por águas pluviais, sujidades, vetores e falhas no entorno.',
'4.1.2':'B/F: entrada de contaminantes por falhas de vedação, infiltrações ou ponto de coleta inadequado.',
'4.1.3':'B/Q: persistência de microrganismos e biofilme; possível resíduo de saneante após higienização.',
'4.2.2':'B/Q/F: biofilme em superfícies deterioradas; migração química, corrosão e desprendimento de partículas.',
'4.2.7':'B/Q: biofilme e microrganismos na canalização; resíduos químicos após limpeza e desinfecção.',
'4.2.8':'B/F: persistência de biofilme, incrustações e partículas em trechos sem acesso ou com falhas de conservação.',
'4.2.9':'B/Q: higienização inadequada ou não reprodutível; sobrevivência microbiana e resíduos de saneantes.',
'4.3.2':'B/Q/F: biofilme, migração química, corrosão ou partículas de material inadequado/deteriorado.',
'4.3.3':'B/F: entrada de microrganismos e partículas por ar, extravasor, retorno de fluxo ou elementos filtrantes ineficazes.',
'4.3.4':'B/F: biofilme, incrustações e falhas internas não detectadas ou não corrigidas.',
'4.3.5':'B/Q: microrganismos e biofilme no reservatório; resíduo químico e recontaminação após limpeza.',
'4.3.6':'B/Q: execução inconsistente da higienização e liberação de reservatório sem condições demonstradas.',
'4.5.2':'B/Q/F: contaminação cruzada entre embalagens retornadas e insumos limpos.',
'4.5.3':'B/Q/F: introdução de insumos contaminados ou fora de especificação; uso de saneante inadequado.',
'4.5.4':'B/Q/F: embalagens com sujidade, resíduo químico, odor, corpo estranho ou defeito que inviabilize higienização/vedação.',
'4.5.6':'B/Q/F: uso acidental ou reincorporação de insumos reprovados ao processo.',
'4.5.8':'B/Q/F: recepção sem critérios uniformes de inspeção, reprovação e destino das embalagens.',
'4.6.3':'B: sobrevivência de microrganismos na embalagem de primeiro uso e sua transferência à água.',
'4.6.4':'B/Q/F: sujidades e matéria orgânica que prejudicam a limpeza e a desinfecção posteriores.',
'4.6.5':'B: persistência de sujidade e microrganismos na embalagem; matéria orgânica pode reduzir a eficácia do desinfetante.',
'4.6.6':'Q: resíduos de detergentes e desinfetantes transferidos da embalagem para a água.',
'4.6.7':'B/Q: recontaminação por água de enxágue inadequada e permanência de resíduos químicos.',
'4.6.8':'B: contaminação microbiológica transferida pelas tampas ao gargalo e à água; avaliar perigos químicos do processo adotado.',
'4.6.9':'B/F: recontaminação de embalagens higienizadas durante espera e transporte ao envase.',
'4.6.10':'B/F: recontaminação por manuseio, passagem aberta, pessoas, vetores e partículas.',
'4.6.11':'B/Q: falhas de execução da limpeza/desinfecção e do preparo dos produtos, por procedimento ou capacitação inadequados.',
'4.6.12':'B/Q: parâmetros e execução da higienização sem padronização ou documentação atualizada.',
'4.7.1':'B/F: contaminação no envase e ingresso de contaminantes por falha de fechamento ou vedação.',
'4.7.2':'B/F: contaminação ambiental por superfícies deterioradas, sujidades e dificuldade de higienização.',
'4.7.3':'B/Q: contaminação na incorporação de CO2 ou em conexões externas à linha protegida.',
'4.7.4':'B/F: condensação, respingos, acúmulo de água e transporte de partículas para áreas de contato.',
'4.7.5':'B/F: transferência de contaminantes pelas mãos e acesso indevido à sala de envase.',
'4.7.6':'B/F: transporte de sujidades e microrganismos por uniformes utilizados fora da sala de envase.',
'4.7.8':'B/Q/F: biofilme, microrganismos, resíduos de saneante e partículas em equipamentos e ambiente de envase.',
'4.10.1':'B/Q/F: falhas do programa de controle que permitem não detectar água, embalagem ou CO2 fora de especificação.',
'4.10.2':'B/Q: resultado analítico inválido ou não confiável e decisão de liberação inadequada.',
'4.10.3':'B/Q: contaminantes microbiológicos ou químicos não detectados ou avaliados com critérios inadequados.',
'4.10.4':'B/Q: liberação de lote fora dos critérios de aceitação por amostragem, análise ou decisão inadequadas.',
'4.10.5':'Q/B: alteração da composição ou do circuito de origem não detectada pelo controle de equivalência.',
'4.10.6':'B/Q: manutenção em uso ou liberação de produto potencialmente inseguro após desvio não tratado.',
'4.12.6':'Q/B: contaminantes no dióxido de carbono incorporado à água; falta de rastreabilidade por carga.',
'4.11.1':'B/Q/F: práticas inadequadas por manipuladores sem supervisão ou capacitação efetiva.',
'4.11.2':'B/Q/F: ausência de atribuição e atuação responsável sobre controles que protegem o produto.',
'4.11.3':'B/Q/F: decisão ou execução inadequadas por responsável sem capacitação demonstrada.',
'4.11.4':'B/Q/F: impossibilidade de comprovar a formação e rastrear a capacitação exigida para funções críticas.'}

def assessment(item,index,f):
    code=item['code'];cat=f['cat'].replace('PPHO','POP');significant=cat in ('PPRO','PCC');pcc=cat=='PCC'
    hazard=HAZARDS[code]
    if code=='4.10.3':hazard=('Q: substâncias químicas acima dos limites do Anexo I da RDC 717/2022.' if index==15 else 'B: '+f.get('parameter','contaminação microbiológica')+' no '+f.get('monitoringPoint','produto envasado')+' não detectada por controle inadequado.')
    if code in ['4.2.7','4.3.5'] and index==2:hazard='B/Q: execução não rastreável por ausência de registros de higienização.'
    if code in ['4.2.7','4.3.5'] and index==3:hazard='B/Q: execução incorreta da higienização por pessoal sem capacitação demonstrada.'
    if code=='4.7.4':hazard={1:'B: empoçamento e respingos de água por escoamento inadequado.',2:'B: retorno de contaminantes pelo ralo sem sifão ou tampa funcional.',3:'F: fragmentos de luminária ou vidro por quebra sem proteção.',4:'B: condensação e contaminação ambiental por ventilação inadequada.'}[index]
    if code=='4.7.5':hazard={1:'B/F: ingresso de contaminantes por acesso não controlado.',2:'B: contaminação das mãos por acionamento manual ou lavatório inadequado.',3:'B: higiene das mãos ineficaz por ausência de sabonete ou antisséptico.',4:'B: recontaminação das mãos no sistema de secagem.',5:'B: transferência de microrganismos por higiene inadequada das mãos.'}[index]
    if code=='4.6.11' and index==2:hazard='B/Q: falhas de execução não rastreáveis por ausência de registros da limpeza e desinfecção.'
    if code=='4.6.11' and index==3:hazard='B/Q: execução incorreta por pessoal sem capacitação demonstrada.'
    if code=='4.3.3':hazard={1:'B/F: ingresso de contaminantes por extravasor desprotegido.',2:'B: estagnação e higienização incompleta por drenagem inadequada.',3:'B: filtros deteriorados ou fora da frequência de verificação e troca.',4:'B: ingresso de microrganismos pelo ar sem barreira microbiológica íntegra.',5:'B: retorno de contaminantes por falha da retenção ou fecho hídrico.',6:'B: amostra contaminada ou não representativa por ponto de coleta inadequado.'}[index]
    if code=='4.1.3' and index==2:hazard='B/Q: execução incorreta da higienização por pessoal sem capacitação demonstrada.'
    if code=='4.1.3' and index==3:hazard='B/Q: falhas de execução não rastreáveis; ausência de evidência dos parâmetros aplicados na higienização.'
    if code=='4.5.3' and index==3:hazard='Q/B: saneante sem regularização ou uso inadequado; eficácia insuficiente e resíduos na água ou embalagem.'
    if code=='4.6.5':hazard=('B/F: sujidade e matéria orgânica na embalagem que impedem a desinfecção eficaz.' if index==1 else 'B: sobrevivência de microrganismos após desinfecção insuficiente da embalagem retornável.')
    if code=='4.6.6' and index==2:hazard='Q: resíduo de saneante não detectado por teste de sensibilidade ou execução inadequadas.'
    if code=='4.10.4' and index==1:hazard='B/Q: amostragem insuficiente ou não representativa impede sustentar a decisão de retenção/liberação.'
    support='Capacitação e registros dão suporte à execução; não são uma etapa de eliminação do perigo.' if 'capacita' in f['texto'].lower() or 'registra' in f['texto'].lower() else 'A frase estabelece condição ou controle de suporte; não define isoladamente uma etapa de redução do perigo.'
    measure='Deve existir: '+PROCEDURES[code]+'. '+f['texto']
    if code=='4.6.11' and index==2:measure='Manter registros datados da limpeza e desinfecção das embalagens, identificando linha, parâmetros executados e responsável.'
    if code=='4.6.11' and index==3:measure='Comprovar a capacitação dos executores e a compreensão dos procedimentos de limpeza, desinfecção e resposta aos desvios.'
    if code=='4.1.3' and index==2:measure='Capacitação comprovada dos executores da limpeza e desinfecção; conferir certificados, conteúdo e identificação dos funcionários.'
    if code=='4.1.3' and index==3:measure='Manter registros datados da limpeza e desinfecção, identificando captação, parâmetros executados e responsável; confrontar com o POP.'
    if code in ('4.1.3','4.2.7','4.3.5','4.7.8') and significant:measure+=' Definir liberação após higienização por microbiologia e/ou ATP, conforme aplicação; ATP não equivale a ensaio microbiológico.'
    special=code=='4.6.8';release=code=='4.10.4' and index==2
    triage={
      'A':('S' if significant else 'N','Perigo significativo tratado por medida específica nesta frase.' if significant else 'Nesta frase, o guia adota controle de base ou de apoio; a significância específica deve ser confirmada no processo.'),
      'B':('S','Medida prevista no requisito e na orientação do guia; existência documental não prova execução.'),
      'C':('S' if pcc else 'N',('Decisão de bloquear/liberar o lote; não elimina o perigo por si.' if release else 'Confirmar etapa efetiva de descontaminação, não apenas proteção.' if special else 'Etapa destinada a remover/reduzir o perigo identificado.') if pcc else support),
      'D':('S' if significant else 'ND','A falha pode comprometer a segurança da água ou da embalagem de contato.' if significant else 'Avaliar exposição e consequência na unidade; não inferir nível inaceitável apenas da ausência documental.'),
      'E':('N' if significant else 'NA','Não demonstrada barreira posterior que assegure o controle deste perigo no produto.' if significant else 'Rota encaminhada ao controle de suporte da Tabela 2.')}
    typeq={
      'F':('NA' if significant else 'N','Controle específico significativo: seguir à decisão Q1-Q4.' if significant else 'A frase isolada não foi adotada como PPRO no guia.'),
      'G':('NA' if significant else 'S' if cat=='POP' else 'N','Rota Q1-Q4.' if significant else 'Rotina operacional padronizada, inclusive higiene.' if cat=='POP' else 'O foco principal desta frase não é o procedimento de rotina.'),
      'H':('NA' if significant else 'S' if cat=='PPR' else 'N','Rota Q1-Q4.' if significant else 'Condição básica, estrutura, organização, capacitação ou registro de suporte.' if cat=='PPR' else 'O foco é procedimento ou verificação específica.'),
      'I':('NA' if significant else 'S' if cat=='PC' else 'N','Rota Q1-Q4.' if significant else 'Verificação ou apoio específico à decisão e ao acompanhamento do controle.' if cat=='PC' else 'Classificação encaminhada a '+cat+'.')}
    decision={
      'Q1':('S' if significant else 'NA','Medida necessária para o perigo identificado.' if significant else 'Controle de suporte classificado na Tabela 2.'),
      'Q2':('ND' if significant else 'NA','Exigir observação da operação e registros da unidade; o guia não comprova implantação.' if significant else 'Não aplicável a esta rota; verificar execução do controle de base.'),
      'Q3':('S' if significant else 'NA','Pré-análise: falha pode expor o produto ao perigo; confirmar sob implementação.' if significant else 'Rota não percorrida.'),
      'Q4':('ND' if significant else 'NA','PCC adotado: exigir limite crítico validado e detecção/correção oportunas.' if pcc else 'PPRO adotado: demonstrar critério de ação e monitoramento; não pressupor limite crítico.' if significant else 'Rota não percorrida.')}
    vals=[('ND','Demonstrar eficácia da medida por validação e verificação específicas.'),('ND','Fundamentar limite crítico mensurável e aplicável ao perigo.' if pcc else 'Definir critério de ação e tolerância de desvio fundamentados.'),('ND','Definir parâmetro, método, frequência, responsável e resposta oportuna.'),('ND','Definir interrupção/bloqueio, correção da causa e verificação para retomar.'),('ND','Identificar e bloquear lotes expostos; avaliar destino e liberação autorizada.'),('ND','Rastrear lote, resultados, execução, desvios, ações e verificação.')]
    if not significant:vals=[('NA','Controle '+cat+': verificar execução, adequação e registros da rotina.') for _ in range(6)]
    if significant and code in ('4.1.3','4.2.7','4.3.5','4.7.8'):vals[0]=('ND','Comprovar higienização e liberação por microbiologia e/ou ATP, conforme aplicação.')
    if code=='4.6.6' and index==1:vals[1]=('ND','Limite de resíduo por produto, com método e sensibilidade capazes de demonstrar o atendimento.')
    if release:vals[1]=('ND','Critérios de aceitação por perigo e bloqueio efetivo até autorização de liberação.');vals[0]=('ND','Demonstrar retenção/liberação efetivas; amostragem não garante todo o lote.')
    if special:vals[0]=('ND','Identificar e validar a descontaminação das tampas; proteção isolada não define PCC.')
    foundation=f.get('fundamento',f.get('consideracao',''))
    if significant:foundation+=' Classificação adotada no guia; confirmação definitiva depende da demonstração na unidade. Q2/Q4=ND não constituem aprovação.'
    notes='Pré-análise documental, sem nova inspeção. Respostas S descrevem o desenho necessário do controle; ND exige comprovação. P='+str(f['P'])+' é ordinal e mantido do guia, não frequência estatística. NA na árvore não dispensa requisito aplicável.'
    evidence='Exigir registros e documentos indicados na orientação vigente, identificados por data, responsável, processo e lote. Não foram presumidos resultados satisfatórios de uma empresa.'
    procedure=PROCEDURES[code]
    if code=='4.11.2':procedure={1:'Responsável técnico pela industrialização',2:'Responsável legal pela industrialização',3:'Proprietário responsável pela industrialização',4:'Habilitação e responsabilidade no CRQ',5:'Habilitação e responsabilidade no CRBio',6:'Habilitação e responsabilidade em outro conselho'}[index]
    if code=='4.10.2':procedure={1:'Capacidade e rastreabilidade do laboratório próprio',2:'Qualificação do laboratório externo',3:'Contrato de análises terceirizadas'}[index]
    if code=='4.10.3':procedure=(f['parameter']+' — '+f['monitoringPoint'])if f.get('parameter')else {15:'Análise anual das substâncias do Anexo I da RDC 717/2022',16:'Análise microbiológica externa mensal de um lote',17:'Controle microbiológico de todos os lotes em cinco unidades'}[index]
    if code in ['4.2.7','4.3.5']:procedure={1:'Higienização e liberação',2:'Registros de higienização',3:'Capacitação dos executores'}[index]+(' da canalização' if code=='4.2.7' else ' do reservatório')
    if code=='4.7.4':procedure={1:'Escoamento do piso',2:'Ralo sifonado e tampa escamoteável',3:'Proteção das luminárias',4:'Ventilação e controle de condensação'}[index]
    if code=='4.7.5':procedure={1:'Controle de acesso pela antesala',2:'Lavatório e torneira sem contato manual',3:'Sabonete inodoro e antisséptico',4:'Secagem sem contato manual',5:'Execução da higiene das mãos'}[index]
    if code=='4.6.11':procedure={1:'Execução da limpeza e desinfecção das embalagens',2:'Registros de limpeza e desinfecção das embalagens',3:'Capacitação dos executores da higienização das embalagens'}[index]
    return dict(procedure=procedure,hazard=hazard,measure=measure,triage=triage,typeq=typeq,decision=decision,validation=vals,foundation=foundation,notes=notes,evidence=evidence,cat=cat,p=f['P'])
