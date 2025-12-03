/*
* ==========================================================
* SCRIPT.JS CONSOLIDADO (v2)
* ==========================================================
*/

/**
 * Função global para confirmar a exclusão de um aluno.
 */
function confirmDelete(event, nome) {
    const confirmacao = confirm(`ATENÇÃO: Você tem certeza que deseja DELETAR o aluno(a) "${nome}"? Todos os registros de presença e notas serão PERDIDOS.`);
    if (confirmacao) {
        return true;
    } else {
        event.preventDefault();
        return false;
    }
}

/**
 * NOVO (Func. 4): Função global para confirmar a exclusão de um material.
 */
function confirmMaterialDelete(event) {
    const confirmacao = confirm("Tem certeza que deseja DELETAR este material?");
    if (confirmacao) {
        return true;
    } else {
        event.preventDefault();
        return false;
    }
}


// ==========================================================
// RENDERIZAÇÃO DE GRÁFICOS (CHART.JS)
// ==========================================================

/**
 * GRÁFICO 1: Frequência (Dashboard da Turma)
 */
function renderFrequenciaChart(dadosFrequencia) {
    const canvas = document.getElementById('frequenciaChart');
    if (canvas) {
        const total = dadosFrequencia.presente + dadosFrequencia.ausente + dadosFrequencia.justificado;
        if (total === 0) {
            canvas.parentElement.innerHTML = '<p class="text-center text-gray-500 h-full flex items-center justify-center">Nenhum dado de frequência registrado.</p>';
            return;
        }

        const ctx = canvas.getContext('2d');
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Presente', 'Ausente', 'Justificado'],
                datasets: [{
                    data: [
                        dadosFrequencia.presente,
                        dadosFrequencia.ausente,
                        dadosFrequencia.justificado
                    ],
                    backgroundColor: ['rgba(22, 163, 74, 0.8)','rgba(220, 38, 38, 0.8)','rgba(234, 179, 8, 0.8)'],
                    borderColor: '#ffffff',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'top' } }
            }
        });
    }
}

/**
 * GRÁFICO 2: Desempenho (Dashboard da Turma)
 */
function renderDesempenhoChart(dadosDesempenho) {
    const canvas = document.getElementById('desempenhoChart');
    if (canvas) {
        if (!dadosDesempenho || dadosDesempenho.length === 0 || dadosDesempenho.every(d => d.desempenho === 0)) {
            canvas.parentElement.innerHTML = '<p class="text-center text-gray-500 h-full flex items-center justify-center">Nenhum dado de desempenho registrado.</p>';
            return;
        }
        
        const labels = dadosDesempenho.map(item => item.aluno);
        const desempenhos = dadosDesempenho.map(item => item.desempenho);

        const ctxIndividual = canvas.getContext('2d');
        new Chart(ctxIndividual, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Desempenho Médio (%)',
                    data: desempenhos,
                    backgroundColor: 'rgba(37, 99, 235, 0.8)',
                    borderColor: 'rgba(37, 99, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true, 
                maintainAspectRatio: false,
                scales: { y: { beginAtZero: true, max: 100 } },
                plugins: { legend: { display: false } }
            }
        });
    }
}

/**
 * GRÁFICO 3: Situação (Dashboard da Turma)
 */
function renderSituacaoChart(dadosSituacao) {
    const canvas = document.getElementById('situacaoChart');
    if (canvas) {
        const total = dadosSituacao.excelente + dadosSituacao.bom + dadosSituacao.reforco + dadosSituacao.insatisfatorio;
        if (total === 0) {
            canvas.parentElement.innerHTML = '<p class="text-center text-gray-500 h-full flex items-center justify-center">Nenhum aluno com situação definida.</p>';
            return;
        }

        const ctx = canvas.getContext('2d');
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Excelente (>=80)', 'Bom (>=60)', 'Reforço (>=40)', 'Insatisfatório (<40)'],
                datasets: [{
                    data: [
                        dadosSituacao.excelente,
                        dadosSituacao.bom,
                        dadosSituacao.reforco,
                        dadosSituacao.insatisfatorio
                    ],
                    backgroundColor: ['rgba(22, 163, 74, 0.8)','rgba(59, 130, 246, 0.8)','rgba(234, 179, 8, 0.8)','rgba(220, 38, 38, 0.8)'],
                    borderColor: '#ffffff',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'top' } }
            }
        });
    }
}

/**
 * GRÁFICO 4: Desempenho Global (Dashboard Global)
 */
function renderGlobalDesempenho(data) {
    const canvas = document.getElementById('globalDesempenhoChart');
    if (!canvas) return;
    
    if (!data || data.length === 0) {
        canvas.parentElement.innerHTML = '<p class="text-center text-gray-500 h-full flex items-center justify-center">Nenhum dado de desempenho encontrado nas turmas.</p>';
        return;
    }
    
    const labels = data.map(item => item.turma);
    const desempenhos = data.map(item => item.desempenho);

    new Chart(canvas.getContext('2d'), {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Desempenho Médio (%)',
                data: desempenhos,
                backgroundColor: 'rgba(22, 163, 74, 0.8)',
            }]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            scales: { y: { beginAtZero: true, max: 100 } },
            plugins: { legend: { display: false } }
        }
    });
}

/**
 * GRÁFICO 5: Frequência Global (Dashboard Global)
 */
function renderGlobalFrequencia(data) {
    const canvas = document.getElementById('globalFrequenciaChart');
     if (!canvas) return;

    if (!data || data.length === 0) {
        canvas.parentElement.innerHTML = '<p class="text-center text-gray-500 h-full flex items-center justify-center">Nenhum dado de frequência encontrado nas turmas.</p>';
        return;
    }
    
    const labels = data.map(item => item.turma);
    const frequencias = data.map(item => item.frequencia);

    new Chart(canvas.getContext('2d'), {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Frequência Média (%)',
                data: frequencias,
                backgroundColor: 'rgba(37, 99, 235, 0.8)',
            }]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            scales: { y: { beginAtZero: true, max: 100 } },
            plugins: { legend: { display: false } }
        }
    });
}


// ==========================================================
// EVENT LISTENER PRINCIPAL (DOM LOADED)
// ==========================================================
document.addEventListener('DOMContentLoaded', () => {
    
    // --- LÓGICA DO DASHBOARD DA TURMA (Existente) ---
    const dataElement = document.getElementById('dashboard-data');
    if (dataElement) {
        try {
            const dadosDesempenho = JSON.parse(dataElement.dataset.desempenho);
            const dadosFrequencia = JSON.parse(dataElement.dataset.frequencia);
            const dadosSituacao = JSON.parse(dataElement.dataset.situacao);

            renderFrequenciaChart(dadosFrequencia);
            renderDesempenhoChart(dadosDesempenho);
            renderSituacaoChart(dadosSituacao);
        } catch (e) {
            console.error("Erro ao carregar dados do dashboard da turma:", e);
        }
    }

    // --- LÓGICA DO DASHBOARD GLOBAL (Func. 10) ---
    const globalDataElement = document.getElementById('global-dashboard-data');
    if (globalDataElement) {
        try {
            const dadosDesempenho = JSON.parse(globalDataElement.dataset.desempenho);
            const dadosFrequencia = JSON.parse(globalDataElement.dataset.frequencia);
            
            renderGlobalDesempenho(dadosDesempenho);
            renderGlobalFrequencia(dadosFrequencia);
        } catch (e) {
            console.error("Erro ao carregar dados do dashboard global:", e);
        }
    }

    // --- LÓGICA DO GRADEBOOK (Func. 1) ---
    const gradebookTable = document.getElementById('gradebook-table');
    if (gradebookTable) {
        gradebookTable.addEventListener('change', (event) => {
            const input = event.target;
            if (!input.classList.contains('gradebook-input')) return;

            const data = {
                id_aluno: input.dataset.alunoId,
                id_atividade: input.dataset.atividadeId,
                campo: input.dataset.campo,
                valor: input.value
            };

            input.classList.remove('bg-green-100', 'bg-red-100');
            input.classList.add('bg-yellow-100');

            fetch('/gradebook/salvar', { // Rota da API
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                input.classList.remove('bg-yellow-100');
                if(result.status === 'success') {
                    input.classList.add('bg-green-100');
                    setTimeout(() => input.classList.remove('bg-green-100'), 1500);
                } else {
                    input.classList.add('bg-red-100');
                    alert('Erro ao salvar: ' + result.message);
                }
            })
            .catch(error => {
                input.classList.remove('bg-yellow-100');
                input.classList.add('bg-red-100');
                console.error('Erro de rede ao salvar gradebook:', error);
                alert('Erro de rede ao salvar.');
            });
        });
    }

    // --- ⭐️⭐️ NOVO (Ideia 2): LÓGICA DE ADIÇÃO EM MASSA (Gradebook) ⭐️⭐️ ---
    const btnSalvarListaAlunos = document.getElementById('btn-salvar-lista-alunos');
    if (btnSalvarListaAlunos) {
        btnSalvarListaAlunos.addEventListener('click', () => {
            const idTurma = btnSalvarListaAlunos.dataset.idTurma;
            const textarea = document.getElementById('bulk-add-alunos-list');
            const nomes = textarea.value.split('\n').filter(n => n.trim() !== ''); // Filtra linhas vazias

            if (nomes.length === 0) {
                alert('Por favor, insira pelo menos um nome.');
                return;
            }

            btnSalvarListaAlunos.disabled = true;
            btnSalvarListaAlunos.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Salvando...';

            fetch(`/turma/${idTurma}/bulk_add_alunos`, { // Rota da API
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ nomes: nomes })
            })
            .then(response => response.json())
            .then(result => {
                if (result.status === 'success') {
                    // Recarrega a página para mostrar o gradebook preenchido
                    location.reload();
                } else {
                    alert('Erro ao salvar alunos: ' + result.message);
                    btnSalvarListaAlunos.disabled = false;
                    btnSalvarListaAlunos.innerHTML = '<i class="fas fa-save"></i> Salvar Alunos e Recarregar Página';
                }
            })
            .catch(error => {
                console.error('Erro de rede ao adicionar alunos:', error);
                alert('Erro de rede.');
                btnSalvarListaAlunos.disabled = false;
                btnSalvarListaAlunos.innerHTML = '<i class="fas fa-save"></i> Salvar Alunos e Recarregar Página';
            });
        });
    }
    // --- ⭐️⭐️ FIM NOVO ⭐️⭐️ ---


    // --- LÓGICA DO HORÁRIO (Func. 3) ---
    const modal = document.getElementById('horario-modal');
    if (modal) {
        const modalTitle = document.getElementById('modal-title');
        const modalIdBloco = document.getElementById('modal-id-bloco');
        const modalTurma = document.getElementById('modal-turma');
        const modalTexto = document.getElementById('modal-texto');
        
        document.querySelectorAll('.horario-bloco').forEach(blocoCell => {
            blocoCell.addEventListener('click', () => {
                const idBloco = blocoCell.dataset.idBloco;
                
                modalTitle.textContent = `Editar Bloco (${blocoCell.dataset.dia} - ${blocoCell.dataset.hora})`;
                modalIdBloco.value = idBloco;
                
                modalTurma.value = 'None';
                modalTexto.value = '';

                const displaySpan = document.getElementById('display-bloco-' + idBloco);
                const textoAtual = displaySpan.textContent.trim();
                
                let turmaEncontrada = false;
                Array.from(modalTurma.options).forEach(option => {
                    if (option.text === textoAtual) {
                        modalTurma.value = option.value;
                        turmaEncontrada = true;
                    }
                });
                
                if (!turmaEncontrada && textoAtual !== 'VAGO') {
                    modalTexto.value = textoAtual;
                }
                
                modal.style.display = 'flex';
            });
        });

        document.getElementById('modal-cancel').addEventListener('click', () => {
            modal.style.display = 'none';
        });

        document.getElementById('modal-save').addEventListener('click', () => {
            const data = {
                id_bloco: modalIdBloco.value,
                id_turma: modalTurma.value,
                texto_alternativo: modalTexto.value
            };

            fetch('/horario/salvar_bloco', { // Rota da API
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                if (result.status === 'success') {
                    const displaySpan = document.getElementById('display-bloco-' + data.id_bloco);
                    displaySpan.textContent = result.nome_display;
                    
                    if(result.nome_display === "VAGO" || result.nome_display === "") {
                        displaySpan.className = 'font-bold text-gray-400';
                        displaySpan.textContent = "VAGO";
                    } else if (result.nome_display === data.texto_alternativo) {
                         displaySpan.className = 'font-bold text-gray-700';
                    } else {
                        displaySpan.className = 'font-bold text-blue-700';
                    }
                    modal.style.display = 'none';
                } else {
                    alert('Erro: ' + result.message);
                }
            })
            .catch(error => {
                console.error('Erro de rede ao salvar bloco:', error);
                alert('Erro de rede ao salvar.');
            });
        });
    }

    // --- LÓGICA DO GERADOR DE QUESTÕES IA (Func. 6) ---
    const btnGerarQuestoes = document.getElementById('btn-gerar-questoes');
    if (btnGerarQuestoes) {
        const inputTitulo = document.getElementById('titulo');
        const inputTipo = document.getElementById('ia-tipo-questoes');
        const outputDescricao = document.getElementById('descricao');

        if (!inputTitulo || !inputTipo || !outputDescricao) {
            console.warn("Elementos para Gerador de Questões IA não encontrados (titulo, ia-tipo-questoes, descricao).");
        } else {
            btnGerarQuestoes.addEventListener('click', () => {
                const tema = inputTitulo.value;
                const tipo = inputTipo.value;

                if (!tema) {
                    alert('Por favor, preencha o Título da atividade primeiro.');
                    inputTitulo.focus();
                    return;
                }

                btnGerarQuestoes.disabled = true;
                btnGerarQuestoes.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Gerando...';

                fetch('/gerar_questoes_ia', { // Rota da API
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ tema: tema, tipo: tipo })
                })
                .then(response => response.json())
                .then(result => {
                    if (result.status === 'success') {
                        outputDescricao.value = result.questoes;
                        outputDescricao.style.height = 'auto';
                        outputDescricao.style.height = (outputDescricao.scrollHeight) + 'px';
                    } else {
                        alert('Erro da IA: ' + result.message);
                    }
                })
                .catch(error => {
                    console.error('Erro de rede ao gerar questões:', error);
                    alert('Erro de rede ao gerar questões.');
                })
                .finally(() => {
                    btnGerarQuestoes.disabled = false;
                    btnGerarQuestoes.innerHTML = '<i class="fas fa-magic"></i> Gerar Questões';
                });
            });
        }
    }

    // --- LÓGICA DA ANÁLISE DE ACESSIBILIDADE IA (Func. 9) ---
    const analisarButtons = document.querySelectorAll('.btn-analisar-ia');
    if (analisarButtons.length > 0) {
        analisarButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const idPlano = e.currentTarget.dataset.idPlano;
                const select = document.getElementById(`select-necessidade-${idPlano}`);
                const resultadoDiv = document.getElementById(`resultado-ia-${idPlano}`);
                
                if (!select || !resultadoDiv) {
                    console.error(`Elementos de IA para o plano ${idPlano} não encontrados.`);
                    return;
                }

                const data = {
                    necessidade: select.value
                };

                button.disabled = true;
                button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
                resultadoDiv.style.display = 'block';
                resultadoDiv.textContent = 'Analisando...';

                fetch(`/plano/${idPlano}/analisar_acessibilidade`, { // Rota da API
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                })
                .then(response => response.json())
                .then(result => {
                    if (result.status === 'success') {
                        resultadoDiv.textContent = result.analise;
                    } else {
                        resultadoDiv.textContent = 'Erro: ' + result.message;
                    }
                })
                .catch(error => {
                    console.error('Erro de rede ao analisar acessibilidade:', error);
                    resultadoDiv.textContent = 'Erro de rede ao tentar analisar.';
                })
                .finally(() => {
                    button.disabled = false;
                    button.innerHTML = '<i class="fas fa-magic"></i> Analisar';
                });
            });
        });
    }

    // ==========================================================
    //  FUNCIONALIDADES DE IA (NOVAS)
    // ==========================================================

    // --- 1. ANÁLISE DE DESEMPENHO DO ALUNO ---
    const btnAnalisarAluno = document.getElementById('btn-analisar-aluno');
    if (btnAnalisarAluno) {
        btnAnalisarAluno.addEventListener('click', () => {
            const idAluno = btnAnalisarAluno.dataset.idAluno;
            const container = document.getElementById('resultado-analise-container');
            const content = document.getElementById('resultado-analise-content');

            // UI de Carregamento
            const originalText = btnAnalisarAluno.innerHTML;
            btnAnalisarAluno.disabled = true;
            btnAnalisarAluno.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Consultando a IA...';
            
            container.classList.remove('hidden');
            content.innerHTML = '<div class="flex items-center space-x-2 text-gray-500"><i class="fas fa-circle-notch fa-spin"></i> <span>Analisando histórico de notas e presenças...</span></div>';

            fetch(`/aluno/${idAluno}/analisar_desempenho_ia`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    content.innerHTML = data.analise;
                } else {
                    content.innerHTML = `<div class="text-red-600 bg-red-50 p-3 rounded border border-red-200"><i class="fas fa-exclamation-circle"></i> ${data.message}</div>`;
                }
            })
            .catch(error => {
                console.error('Erro:', error);
                content.innerHTML = '<div class="text-red-600">Erro de comunicação com o servidor. Verifique sua conexão.</div>';
            })
            .finally(() => {
                btnAnalisarAluno.disabled = false;
                btnAnalisarAluno.innerHTML = originalText;
            });
        });
    }

    // --- 2. ASSISTENTE DE DIÁRIO DE BORDO ---
    const btnSugerirDiario = document.getElementById('btn-sugerir-diario');
    if (btnSugerirDiario) {
        btnSugerirDiario.addEventListener('click', () => {
            // Seletores para os campos do formulário (adaptado para WTForms)
            // Procura o select de turma pelo nome 'id_turma'
            const selectTurma = document.querySelector('select[name="id_turma"]');
            // Procura o input de data (que o WTForms gera com id 'data' ou name 'data')
            const inputData = document.querySelector('input[name="data"]'); 
            const textareaAnotacao = document.getElementById('campo-anotacao');

            if (!selectTurma || !inputData || !textareaAnotacao) {
                console.error("Campos do formulário de diário não encontrados.");
                return;
            }

            const idTurma = selectTurma.value;
            const dataDiario = inputData.value;

            if (!idTurma || idTurma === 'None') {
                alert('Por favor, selecione uma Turma específica (não "Geral") para que a IA possa buscar o plano de aula.');
                selectTurma.focus();
                return;
            }
            if (!dataDiario) {
                alert('Por favor, preencha a Data do diário.');
                inputData.focus();
                return;
            }

            // UI de Carregamento
            const originalText = btnSugerirDiario.innerHTML;
            btnSugerirDiario.disabled = true;
            btnSugerirDiario.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Escrevendo...';

            fetch('/diario/sugerir_ia', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id_turma: idTurma, data: dataDiario })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Efeito de "digitação" simples ou apenas preencher
                    textareaAnotacao.value = data.sugestao;
                    textareaAnotacao.classList.add('bg-yellow-50'); // Feedback visual
                    setTimeout(() => textareaAnotacao.classList.remove('bg-yellow-50'), 1000);
                } else {
                    alert('A IA não conseguiu sugerir: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Erro:', error);
                alert('Erro ao conectar com o servidor.');
            })
            .finally(() => {
                btnSugerirDiario.disabled = false;
                btnSugerirDiario.innerHTML = originalText;
            });
        });
    }

}); // Fim do DOMContentLoaded