/* Download prebuilt blank forms without generating PDF fields in the browser. */
(()=>{
 const link=document.querySelector('a[download]');
 if(!link)return;
 const toggle=document.getElementById('include-document-checklist');
 function update(){const name=toggle?.checked?'Guia_APPCC_BPF_Em_Branco_Todos_F_Documentos.pdf':'Guia_APPCC_BPF_Em_Branco_Todos_F.pdf';link.href=name+'?v=medias-frases-20261102';link.download=name;}
 toggle?.addEventListener('change',update);update();
})();
