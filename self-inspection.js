/* Autovistoria customizes only the informative APPCC simulation. */
(()=>{
 const button=document.getElementById('appcc-edit-mode'),restore=document.getElementById('appcc-restore'),status=document.getElementById('appcc-mode-status');
 function update(){button.textContent=appccEditable()?'Bloquear edição do APPCC':'Editar APPCC para autovistoria';button.setAttribute('aria-pressed',String(appccEditable()));const custom=Object.keys(S.appccOverrides||{}).length>0;status.textContent=(appccEditable()?'Autovistoria: use o botão F para editar APPCC, NC e probabilidade de cada frase.':'APPCC, NC e probabilidade somente para consulta.')+(custom?' Simulação com valores personalizados.':' Simulação com os valores originais do guia.')+' A média oficial permanece pelo cálculo original por item.';}
 button.onclick=()=>{S.selfInspectionEditing=!appccEditable();save();if(editing)renderPhrases();refreshPaper();update();};
 restore.onclick=()=>{if(!confirm('Restaurar APPCC, NC e probabilidades originais? As respostas, observações e demais dados da inspeção serão preservados.'))return;S.appccOverrides={};S.selfInspectionEditing=false;save();if(editing)renderPhrases();refreshPaper();update();};
 window.addEventListener('storage',update);update();
})();
