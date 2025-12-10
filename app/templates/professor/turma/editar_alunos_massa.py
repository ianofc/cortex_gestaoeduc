{% extends "layouts/base_app.html" %}

{% block title %}Editar Alunos em Massa - {{ turma.nome }}{% endblock %}

{% block content %}

<div class="max-w-4xl mx-auto">
    <div class="mb-8 flex items-center gap-4 animate-fade-in-down">
        <div class="p-3 bg-indigo-100 dark:bg-indigo-900/30 rounded-xl text-indigo-600 dark:text-indigo-400 shadow-sm">
            <i class="fas fa-users-cog text-2xl"></i>
        </div>
        <div>
            <h1 class="text-3xl font-black text-gray-900 dark:text-white tracking-tight">
                Editar Alunos em Massa
            </h1>
            <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
                Turma: <span class="font-bold text-indigo-600 dark:text-indigo-400">{{ turma.nome }}</span>
            </p>
        </div>
    </div>

    <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-100 dark:border-gray-700 p-6">
        <h2 class="text-xl font-bold text-gray-800 dark:text-white mb-4">Ajustar Nomes</h2>
        
        <form id="form-editar-alunos-massa">
            <div class="space-y-4 max-h-96 overflow-y-auto custom-scrollbar p-2">
                {% for aluno in alunos %}
                <div class="flex items-center gap-4 bg-gray-50 dark:bg-gray-900/50 p-3 rounded-lg border border-gray-200 dark:border-gray-700">
                    <div class="w-10 h-10 rounded-full bg-indigo-100 text-indigo-600 flex items-center justify-center text-xs font-bold shrink-0">
                        {{ aluno.nome[:2].upper() }}
                    </div>
                    <div class="flex-1">
                        <input type="text" name="aluno_nome_{{ aluno.id }}" 
                               data-aluno-id="{{ aluno.id }}"
                               value="{{ aluno.nome }}" 
                               class="w-full px-3 py-2 rounded-lg bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none text-sm aluno-input">
                    </div>
                </div>
                {% endfor %}
            </div>

            <div class="mt-6 flex justify-end gap-3">
                <a href="{{ url_for('alunos.turma', id_turma=turma.id) }}" class="px-6 py-3 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 font-bold rounded-xl hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors text-center text-sm">
                    Cancelar
                </a>
                <button type="submit" id="btn-salvar-massa-alunos" class="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl shadow-lg transition-colors">
                    <i class="fas fa-save mr-2"></i> Salvar Alterações
                </button>
            </div>
        </form>
    </div>
</div>

{% endblock %}

{% block scripts %}
<script>
    document.getElementById('form-editar-alunos-massa').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const btn = document.getElementById('btn-salvar-massa-alunos');
        const originalText = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Salvando...';
        btn.disabled = true;

        const inputs = document.querySelectorAll('.aluno-input');
        const alunosData = [];
        
        inputs.forEach(input => {
            alunosData.push({
                id: parseInt(input.dataset.alunoId),
                nome: input.value.trim()
            });
        });

        const payload = {
            alunos: alunosData
        };

        try {
            const response = await fetch("{{ url_for('alunos.salvar_alunos_massa', id_turma=turma.id) }}", {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            if (data.status === 'success') {
                Swal.fire({
                    icon: 'success', 
                    title: 'Alunos Atualizados!', 
                    text: data.message, 
                    showConfirmButton: false, 
                    timer: 2000
                });
                setTimeout(() => { window.location.href = "{{ url_for('alunos.turma', id_turma=turma.id) }}"; }, 2000);
            } else {
                Swal.fire('Erro', data.message, 'error');
            }

        } catch (error) {
            console.error("Erro de Rede ao salvar alunos em massa:", error);
            Swal.fire('Erro de Rede', 'Não foi possível se conectar ao servidor.', 'error');
        } finally {
            btn.innerHTML = originalText;
            btn.disabled = false;
        }
    });
</script> 
{% endblock %}