async function openDirectoryDialog() {
    // Tornar o campo editável
    const directoryInput = document.getElementById('directory');
    directoryInput.readOnly = false;
    directoryInput.focus();
    document.querySelector('.btn-analyze').classList.add('pulse');
}

async function retryFetch(url, options, maxRetries = 3) {
    for (let i = 0; i < maxRetries; i++) {
        try {
            const response = await fetch(url, options);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return response;
        } catch (error) {
            if (i === maxRetries - 1) throw error;
            await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
            updateStatus(`Tentativa ${i + 2} de ${maxRetries}...`);
        }
    }
}

async function analyzeProgress(directory) {
    const stats = {
        files: 0,
        lines: 0,
        methods: 0
    };
    
    try {
        const files = await getAllFiles(directory);
        stats.files = files.length;
        
        for (const file of files) {
            const content = await file.text();
            stats.lines += content.split('\n').length;
            stats.methods += (content.match(/\b(public|private|protected)\s+\w+\s+\w+\s*\(/g) || []).length;
        }
        
        return stats;
    } catch (error) {
        console.error('Erro ao calcular estatísticas:', error);
        return stats;
    }
}

// Variáveis globais para controle de progresso
let totalFiles = 0;
let processedFiles = 0;
let totalMethods = 0;
let processedMethods = 0;
let currentInterval = null;

function showTemporaryStats(stats) {
    const tempStats = document.getElementById('tempStats');
    let byLanguageHtml = '';
    
    // Criar lista detalhada por linguagem
    for (const [lang, count] of Object.entries(stats.by_language)) {
        if (count > 0) {
            byLanguageHtml += `${lang}: ${count} arquivos\n`;
        }
    }
    
    tempStats.innerHTML = `
        <pre>Analisando:
${stats.subdirs} subdiretórios
${stats.files} arquivos de Desenvolvimento
${stats.lines.toLocaleString()} linhas de código
${stats.methods} métodos com CNPJ

Distribuição por linguagem:
${byLanguageHtml}</pre>
    `;
    tempStats.style.display = 'block';
    
    // Inicializar variáveis globais de progresso
    totalFiles = stats.files;
    totalMethods = stats.methods || 50; // Valor mínimo para demonstração
    processedFiles = 0;
    processedMethods = 0;
    
    // Primeiro criar e exibir o gráfico
    const languageChartContainer = document.querySelector('.language-chart-container');
    if (languageChartContainer) languageChartContainer.style.display = 'block';
    createLanguageChart(stats);
    
    // Depois exibir a barra de progresso e container de arquivo atual
    setTimeout(() => {
        const currentFileContainer = document.querySelector('.current-file-container');
        const progressContainer = document.querySelector('.progress-container');
        
        if (currentFileContainer) currentFileContainer.style.display = 'flex';
        if (progressContainer) progressContainer.style.display = 'block';
        
        // Iniciar simulação do progresso dos métodos
        startMethodProgressSimulation();
    }, 800); // Pequeno atraso para melhor UX
}

// Função completamente reescrita para simular o progresso dos métodos
function startMethodProgressSimulation() {
    // Limpar qualquer intervalo existente
    if (currentInterval) {
        clearInterval(currentInterval);
        currentInterval = null;
    }
    
    // Reiniciar contadores
    processedMethods = 0;
    
    // Nomes de métodos relacionados a CNPJ para simulação
    const methodNames = [
        'validarCNPJ', 'formatarCNPJ', 'extrairCNPJ', 'verificarCNPJ', 
        'salvarCNPJ', 'buscarPorCNPJ', 'converterCNPJ', 'carregarCNPJ',
        'analisarCNPJ', 'consultarCNPJ', 'enviarCNPJ', 'processarCNPJ',
        'validarFormatoCNPJ', 'desformatarCNPJ', 'exibirCNPJ', 'filtrarCNPJ'
    ];
    
    const classNames = [
        'Cliente', 'Empresa', 'Cadastro', 'Fiscal', 'Documento', 'Registro',
        'Pessoa', 'Fornecedor', 'Emissor', 'Receptor', 'Contribuinte', 'Servico'
    ];
    
    // Duração total desejada da simulação (ms)
    const totalDuration = 25000; // 25 segundos
    
    // Intervalo entre atualizações
    const updateInterval = 300; // 300ms
    
    // Calcular incremento por atualização
    const totalUpdates = totalDuration / updateInterval;
    const methodsPerUpdate = Math.max(1, Math.ceil(totalMethods / totalUpdates));
    
    // Atualizar a UI com 0%
    updateProgressUI(0, totalMethods);
    updateCurrentFile('Iniciando análise...');
    
    currentInterval = setInterval(() => {
        // Calcular quantos métodos processar nesta iteração
        const increment = Math.min(
            methodsPerUpdate,
            totalMethods - processedMethods
        );
        
        processedMethods += increment;
        
        // Gerar nome de método aleatório
        const randomMethod = methodNames[Math.floor(Math.random() * methodNames.length)];
        const randomClass = classNames[Math.floor(Math.random() * classNames.length)];
        updateCurrentFile(`${randomClass}.${randomMethod}()`);
        
        // Atualizar a UI com o progresso atual
        updateProgressUI(processedMethods, totalMethods);
        
        // Verificar se a simulação terminou
        if (processedMethods >= totalMethods) {
            clearInterval(currentInterval);
            currentInterval = null;
            
            // Mostrar 100% e mensagem de conclusão
            updateProgressUI(totalMethods, totalMethods);
            updateCurrentFile("Análise concluída! Gerando relatório...");
        }
    }, updateInterval);
}

// Função para atualizar a interface com o progresso atual
function updateProgressUI(current, total) {
    if (total <= 0) return;
    
    const percentage = Math.min(100, Math.round((current / total) * 100));
    
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    const filesProcessed = document.getElementById('filesProcessed');
    
    if (progressBar) {
        progressBar.style.width = `${percentage}%`;
    }
    
    if (progressText) {
        progressText.textContent = `${percentage}%`;
    }
    
    if (filesProcessed) {
        filesProcessed.textContent = `${current}/${total} métodos analisados`;
    }
}

function updateCurrentFile(filename) {
    const currentFileElement = document.getElementById('currentFile');
    if (currentFileElement) {
        currentFileElement.textContent = filename;
    }
}

async function preAnalyzeDirectory(directory) {
    try {
        const formData = new FormData();
        formData.append('directory', directory);
        
        const response = await fetch('/pre-analyze', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error('Erro na pré-análise:', error);
        throw error;
    }
}

document.getElementById('analyzeForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const directory = document.getElementById('directory').value;
    
    if (!directory) {
        showError('Por favor, selecione um diretório');
        return;
    }
    
    // Ir para o passo 2
    goToStep(2);
    
    try {
        updateStatus('Analisando estrutura do projeto...');
        const stats = await preAnalyzeDirectory(directory);
        showTemporaryStats(stats);
        
        updateStatus('Iniciando análise com AI...');
        
        const formData = new FormData();
        formData.append('directory', directory);
        
        updateStatus('Analisando impactos com AI...');
        
        const response = await retryFetch('/analyze', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        // Limpar o intervalo de simulação quando terminar
        if (currentInterval) {
            clearInterval(currentInterval);
            currentInterval = null;
        }
        
        // Remover estatísticas temporárias e elementos de progresso
        hideProgressElements();
        
        // Atualizar resultados e ir para o passo 3
        updateResults(data);
        goToStep(3);
        
        // Mostrar botão de download
        const downloadBtn = document.getElementById('downloadExcel');
        downloadBtn.href = `/download/${data.excel_file}`;
        downloadBtn.style.display = 'inline-flex';
        
        // Criar gráfico
        createImpactChart();
        
    } catch (error) {
        // Limpar o intervalo de simulação em caso de erro
        if (currentInterval) {
            clearInterval(currentInterval);
            currentInterval = null;
        }
        
        // Esconder elementos de progresso
        hideProgressElements();
        
        let errorMsg = 'Falha na conexão com o servidor. ';
        if (error.message === 'Failed to fetch') {
            errorMsg += 'Verifique sua conexão e se o servidor está rodando.';
        } else {
            errorMsg += error.message;
        }
        showError(errorMsg);
        
        // Voltar para o passo 1
        goToStep(1);
    }
});

function hideProgressElements() {
    // Ocultar os elementos de progresso
    const tempStats = document.getElementById('tempStats');
    const currentFileContainer = document.querySelector('.current-file-container');
    const progressContainer = document.querySelector('.progress-container');
    const languageChartContainer = document.querySelector('.language-chart-container');
    const aiInsightsContainer = document.querySelector('.ai-insights-container');
    
    if (tempStats) tempStats.style.display = 'none';
    if (currentFileContainer) currentFileContainer.style.display = 'none';
    if (progressContainer) progressContainer.style.display = 'none';
    if (languageChartContainer) languageChartContainer.style.display = 'none';
    if (aiInsightsContainer) aiInsightsContainer.style.display = 'none';
}

function updateStatus(message) {
    document.querySelector('.status-text').textContent = message;
}

function showError(message) {
    const errorDiv = document.querySelector('.error-message');
    errorDiv.querySelector('p').textContent = message;
    errorDiv.style.display = 'flex';
    
    // Auto-hide after 10 seconds
    setTimeout(() => {
        errorDiv.style.display = 'none';
    }, 10000);
}

function updateResults(data) {
    const counts = {high: 0, medium: 0, low: 0};
    const totals = {dev: 0, test: 0, total: 0};
    const tbody = document.querySelector('#resultsTable tbody');
    tbody.innerHTML = '';
    
    data.data.forEach(item => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${item.arquivo}</td>
            <td>${item.metodo}</td>
            <td>${item.linha}</td>
            <td>${item.tipo_uso}</td>
            <td>${item.severidade}</td>
            <td>${item.horas_dev}</td>
            <td>${item.horas_teste}</td>
            <td>${item.horas_total}</td>
        `;
        tbody.appendChild(row);
        
        if (item.severidade === 'ALTA') counts.high++;
        else if (item.severidade === 'MEDIA') counts.medium++;
        else if (item.severidade === 'BAIXA') counts.low++;
        
        totals.dev += item.horas_dev;
        totals.test += item.horas_teste;
        totals.total += item.horas_total;
    });
    
    // Atualizar contadores e mostrar totais de forma separada
    document.getElementById('highImpact').textContent = `${counts.high} métodos`;
    document.getElementById('mediumImpact').textContent = `${counts.medium} métodos`;
    document.getElementById('lowImpact').textContent = `${counts.low} métodos`;
    
    // Adicionar totais de horas na tabela
    const tfoot = document.createElement('tfoot');
    tfoot.innerHTML = `
        <tr>
            <td colspan="5" style="text-align: right"><strong>Total de Horas:</strong></td>
            <td>${totals.dev.toFixed(1)}</td>
            <td>${totals.test.toFixed(1)}</td>
            <td><strong>${totals.total.toFixed(1)}</strong></td>
        </tr>
    `;
    document.querySelector('#resultsTable').appendChild(tfoot);
}

// Adicionar funcionalidade de troca de etapas
function goToStep(stepNumber) {
    // Atualizar sidebar
    document.querySelectorAll('.nav-steps li').forEach(item => {
        item.classList.remove('active');
    });
    document.querySelector(`.nav-steps li[data-step="${stepNumber}"]`).classList.add('active');
    
    // Atualizar conteúdo
    document.querySelectorAll('.step-section').forEach(section => {
        section.classList.remove('active');
    });
    document.getElementById(`step${stepNumber}`).classList.add('active');
}

// Adicionar eventos de clique à navegação lateral
document.querySelectorAll('.nav-steps li').forEach(item => {
    item.addEventListener('click', () => {
        const step = item.getAttribute('data-step');
        goToStep(step);
    });
});

// Função para resetar análise
function resetAnalysis() {
    // Limpar resultados
    document.getElementById('highImpact').textContent = '0';
    document.getElementById('mediumImpact').textContent = '0';
    document.getElementById('lowImpact').textContent = '0';
    document.querySelector('#resultsTable tbody').innerHTML = '';
    
    // Voltar para o passo 1
    goToStep(1);
    
    // Ocultar download
    document.getElementById('downloadExcel').style.display = 'none';
}

// Função para criar gráfico de impacto
function createImpactChart() {
    const ctx = document.getElementById('impactChart').getContext('2d');
    
    const highImpact = parseInt(document.getElementById('highImpact').textContent);
    const mediumImpact = parseInt(document.getElementById('mediumImpact').textContent);
    const lowImpact = parseInt(document.getElementById('lowImpact').textContent);
    
    // Destruir gráfico existente se houver
    if (window.impactChart instanceof Chart) {
        window.impactChart.destroy();
    }
    
    window.impactChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Alto Impacto', 'Médio Impacto', 'Baixo Impacto'],
            datasets: [{
                data: [highImpact, mediumImpact, lowImpact],
                backgroundColor: [
                    'rgba(255, 71, 87, 0.8)',
                    'rgba(255, 165, 2, 0.8)',
                    'rgba(46, 213, 115, 0.8)'
                ],
                borderColor: [
                    'rgba(255, 71, 87, 1)',
                    'rgba(255, 165, 2, 1)',
                    'rgba(46, 213, 115, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        color: 'rgba(255, 255, 255, 0.7)',
                        font: {
                            family: "'Inter', sans-serif",
                            size: 12
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleFont: {
                        family: "'Inter', sans-serif",
                        size: 14
                    },
                    bodyFont: {
                        family: "'Inter', sans-serif",
                        size: 13
                    },
                    padding: 12
                }
            },
            cutout: '65%',
            animation: {
                animateScale: true,
                animateRotate: true,
                duration: 1000
            }
        }
    });
}

// Função para tentar novamente a última análise
function retryLastAnalysis() {
    const form = document.getElementById('analyzeForm');
    if (form) form.dispatchEvent(new Event('submit'));
}

// Adicionar estas funções após a função showTemporaryStats

function createLanguageChart(stats) {
    const languageChartContainer = document.querySelector('.language-chart-container');
    if (!languageChartContainer) return;
    
    languageChartContainer.style.display = 'block';
    
    const ctx = document.getElementById('languageDistChart').getContext('2d');
    const languages = [];
    const counts = [];
    const colors = [
        'rgba(54, 162, 235, 0.8)',
        'rgba(255, 99, 132, 0.8)',
        'rgba(255, 206, 86, 0.8)',
        'rgba(75, 192, 192, 0.8)',
        'rgba(153, 102, 255, 0.8)',
        'rgba(255, 159, 64, 0.8)',
        'rgba(199, 199, 199, 0.8)',
        'rgba(83, 102, 255, 0.8)',
    ];
    
    let totalFiles = 0;
    
    // Extrair dados por linguagem
    for (const [lang, count] of Object.entries(stats.by_language)) {
        if (count > 0) {
            languages.push(lang.charAt(0).toUpperCase() + lang.slice(1));
            counts.push(count);
            totalFiles += count;
        }
    }
    
    // Se não houver linguagens, adicionar dados dummy para evitar erro
    if (languages.length === 0) {
        languages.push('Sem dados');
        counts.push(1);
    }
    
    // Destruir gráfico existente se houver
    if (window.languageChart instanceof Chart) {
        window.languageChart.destroy();
    }
    
    // Criar novo gráfico com ajustes para tamanho
    window.languageChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: languages,
            datasets: [{
                data: counts,
                backgroundColor: colors.slice(0, languages.length),
                borderColor: 'rgba(255, 255, 255, 0.1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            layout: {
                padding: {
                    top: 5,
                    bottom: 5
                }
            },
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        boxWidth: 12,
                        padding: 10,
                        color: 'rgba(255, 255, 255, 0.7)',
                        font: {
                            family: "'Inter', sans-serif",
                            size: 10
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const percentage = Math.round((value / totalFiles) * 100);
                            return `${label}: ${value} arquivos (${percentage}%)`;
                        }
                    }
                }
            },
            cutout: '60%',
            animation: {
                animateRotate: true,
                animateScale: true,
                duration: 800
            }
        }
    });
    
    // Adicionar insights de AI com base nos dados
    addAIInsight(stats);
}

function addAIInsight(stats) {
    const analyzing = document.querySelector('.analyzing');
    if (!analyzing) return;
    
    // Criar container de insights se não existir
    let insightsContainer = document.querySelector('.ai-insights-container');
    if (!insightsContainer) {
        insightsContainer = document.createElement('div');
        insightsContainer.className = 'ai-insights-container';
        analyzing.appendChild(insightsContainer);
    }
    
    // Criar insights baseados nos dados
    const insights = [
        {
            title: "Distribuição de Código",
            content: generateDistributionInsight(stats)
        },
        {
            title: "Complexidade Estimada",
            content: generateComplexityInsight(stats)
        },
        {
            title: "Uso de CNPJ",
            content: `Encontrados ${stats.methods} métodos que manipulam CNPJ em ${stats.subdirs} subdiretórios.`
        }
    ];
    
    // Adicionar insights com intervalo para animação
    insights.forEach((insight, index) => {
        setTimeout(() => {
            const insightEl = document.createElement('div');
            insightEl.className = 'ai-insight';
            insightEl.innerHTML = `
                <div class="title">
                    <span class="material-icons">psychology</span>
                    ${insight.title}
                </div>
                <div class="content">${insight.content}</div>
            `;
            insightsContainer.appendChild(insightEl);
            
            // Acionar animação após inserção no DOM
            setTimeout(() => {
                insightEl.classList.add('visible');
            }, 50);
        }, index * 1000);
    });
}

function generateDistributionInsight(stats) {
    // Encontrar a linguagem mais comum
    let topLanguage = "";
    let topCount = 0;
    
    for (const [lang, count] of Object.entries(stats.by_language)) {
        if (count > topCount) {
            topCount = count;
            topLanguage = lang;
        }
    }
    
    if (topLanguage && topCount > 0) {
        const percentage = Math.round((topCount / stats.files) * 100);
        return `Predominância de ${topLanguage} (${percentage}% dos arquivos). Esta distribuição indica ${percentage > 70 ? 'um sistema monolítico' : 'uma arquitetura multi-linguagem'}.`;
    }
    
    return "Não foi possível determinar a distribuição predominante.";
}

function generateComplexityInsight(stats) {
    const filesPerMethod = stats.files / Math.max(1, stats.methods);
    
    if (filesPerMethod < 2) {
        return "Alta concentração de uso de CNPJ. Cada arquivo tem múltiplos métodos afetados, indicando alto acoplamento.";
    } else if (filesPerMethod < 5) {
        return "Distribuição moderada de uso de CNPJ. Os pontos de impacto estão distribuídos pelo sistema.";
    } else {
        return "Baixa densidade de uso de CNPJ. Os pontos de impacto são isolados, indicando melhor encapsulamento.";
    }
}

async function* getFilesRecursively(dirHandle) {
    for await (const entry of dirHandle.values()) {
        if (entry.kind === "file") {
            yield entry;
        } else if (entry.kind === "directory") {
            yield* getFilesRecursively(entry);
        }
    }
}

async function getAllFiles(directory) {
    try {
        const dirHandle = await window.showDirectoryPicker({
            startIn: directory
        });
        const files = [];
        for await (const file of getFilesRecursively(dirHandle)) {
            files.push(file);
        }
        return files;
    } catch (error) {
        console.error('Erro ao listar arquivos:', error);
        return [];
    }
}
