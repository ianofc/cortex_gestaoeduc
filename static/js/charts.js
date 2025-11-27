document.addEventListener('DOMContentLoaded', function() {
    // Configuração Global Chart.js
    if (typeof Chart !== 'undefined') {
        Chart.defaults.font.family = "'Inter', sans-serif";
        Chart.defaults.color = '#6B7280';
    }

    // ==========================================
    // LÓGICA 1: DASHBOARD DA TURMA (dashboard.html)
    // ==========================================
    const divDataTurma = document.getElementById('dashboard-data');
    
    if (divDataTurma) {
        const rawDesempenho = JSON.parse(divDataTurma.dataset.desempenho || '[]');
        const rawSituacao = JSON.parse(divDataTurma.dataset.situacao || '{}');
        
        const labelsAlunos = rawDesempenho.map(item => item.aluno);
        const scoresAlunos = rawDesempenho.map(item => item.desempenho);

        // Gráfico de Desempenho (Barras)
        const ctxDesempenho = document.getElementById('desempenhoChart');
        if(ctxDesempenho) {
            new Chart(ctxDesempenho, {
                type: 'bar',
                data: {
                    labels: labelsAlunos,
                    datasets: [{
                        label: 'Desempenho (%)',
                        data: scoresAlunos,
                        backgroundColor: 'rgba(99, 102, 241, 0.6)', // Indigo-500
                        borderColor: 'rgba(99, 102, 241, 1)',
                        borderWidth: 1,
                        borderRadius: 4
                    }]
                },
                options: {
                    responsive: true, 
                    maintainAspectRatio: false,
                    scales: { y: { beginAtZero: true, max: 100 } }
                }
            });
        }

        // Gráfico de Situação (Doughnut)
        const ctxSituacao = document.getElementById('situacaoChart');
        if(ctxSituacao) {
            const labelsSit = Object.keys(rawSituacao);
            const dataSit = Object.values(rawSituacao);
            
            new Chart(ctxSituacao, {
                type: 'doughnut',
                data: {
                    labels: labelsSit,
                    datasets: [{
                        data: dataSit,
                        backgroundColor: [
                            'rgba(16, 185, 129, 0.6)', // Verde
                            'rgba(245, 158, 11, 0.6)', // Amarelo
                            'rgba(239, 68, 68, 0.6)'   // Vermelho
                        ],
                        borderColor: '#ffffff',
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true, 
                    maintainAspectRatio: false,
                    plugins: { legend: { position: 'bottom' } }
                }
            });
        }
    }

    // ==========================================
    // LÓGICA 2: DASHBOARD GLOBAL (dashboard_global.html)
    // ==========================================
    const divDataGlobal = document.getElementById('dashboard-global-data');

    if (divDataGlobal) {
        const labelsGlobal = JSON.parse(divDataGlobal.dataset.labels || '[]');
        const dataDesempenhoGlobal = JSON.parse(divDataGlobal.dataset.desempenho || '[]');
        const dataFrequenciaGlobal = JSON.parse(divDataGlobal.dataset.frequencia || '[]');

        // Gráfico Comparativo de Desempenho (Barras)
        const ctxGlobalDesempenho = document.getElementById('chartGlobalDesempenho');
        if (ctxGlobalDesempenho) {
            new Chart(ctxGlobalDesempenho, {
                type: 'bar',
                data: {
                    labels: labelsGlobal,
                    datasets: [{
                        label: 'Média de Notas',
                        data: dataDesempenhoGlobal,
                        backgroundColor: 'rgba(79, 70, 229, 0.6)',
                        borderColor: 'rgba(79, 70, 229, 1)',
                        borderWidth: 1,
                        borderRadius: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: { y: { beginAtZero: true, max: 10 } }
                }
            });
        }

        // Gráfico Comparativo de Frequência (Linha)
        const ctxGlobalFrequencia = document.getElementById('chartGlobalFrequencia');
        if (ctxGlobalFrequencia) {
            new Chart(ctxGlobalFrequencia, {
                type: 'line',
                data: {
                    labels: labelsGlobal,
                    datasets: [{
                        label: 'Frequência (%)',
                        data: dataFrequenciaGlobal,
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        borderColor: 'rgba(16, 185, 129, 1)',
                        borderWidth: 2,
                        tension: 0.3,
                        fill: true,
                        pointRadius: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: { y: { beginAtZero: true, max: 100 } }
                }
            });
        }
    }
});

// --- FUNÇÕES DE EXPORTAÇÃO INTELIGENTES ---

window.exportToPDF = function() {
    // Tenta encontrar o container principal de conteúdo (comum a ambas as páginas)
    const element = document.getElementById('dashboard-content');
    
    if (!element) {
        alert("Erro: Conteúdo para PDF não encontrado.");
        return;
    }

    const opt = {
        margin: 0.3,
        filename: 'Cortex_Relatorio.pdf',
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2, useCORS: true },
        jsPDF: { unit: 'in', format: 'a4', orientation: 'landscape' }
    };
    
    if (typeof html2pdf !== 'undefined') {
        html2pdf().set(opt).from(element).save();
    } else {
        alert("Erro: Biblioteca PDF não carregada.");
    }
};

window.exportToExcel = function() {
    // Tenta encontrar tabela de Turma OU tabela Global
    const table = document.getElementById('tableAlunos') || document.getElementById('tableTopAlunos');
    
    if (table && typeof XLSX !== 'undefined') {
        const wb = XLSX.utils.table_to_book(table, {sheet: "Relatorio"});
        XLSX.writeFile(wb, 'Cortex_Relatorio.xlsx');
    } else {
        alert("Erro: Tabela não encontrada ou biblioteca Excel ausente.");
    }
};

window.exportToDocx = function() {
    const table = document.getElementById('tableAlunos') || document.getElementById('tableTopAlunos');

    if (table && typeof htmlDocx !== 'undefined' && typeof saveAs !== 'undefined') {
        const content = `
            <h2 style="font-family: Arial;">Relatório Cortex Analytics</h2>
            <br>
            ${table.outerHTML}
        `;
        const converted = htmlDocx.asBlob(content);
        saveAs(converted, 'Cortex_Relatorio.docx');
    } else {
        alert("Erro: Tabela não encontrada ou bibliotecas Docx ausentes.");
    }
};