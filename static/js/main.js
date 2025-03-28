async function openDirectoryDialog() {
    try {
        const handle = await window.showDirectoryPicker();
        const directory = handle.name;
        document.getElementById('directory').value = directory;
    } catch (err) {
        showError('Erro ao selecionar diretório');
    }
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

// Adicione estas variáveis no escopo global
let totalFiles = 0;
let processedFiles = 0;
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
    totalMethods = stats.methods;
    processedFiles = 0;
    processedMethods = 0;
    
    // Exibir elementos de progresso
    const currentFileContainer = document.querySelector('.current-file-container');
    const progressContainer = document.querySelector('.progress-container');
    
    if (currentFileContainer) currentFileContainer.style.display = 'block';
    if (progressContainer) progressContainer.style.display = 'block';
    
    // Iniciar simulação de progresso
    simulateProgress();
}

let totalMethods = 0;
let processedMethods = 0;

function simulateProgress() {
    if (currentInterval) clearInterval(currentInterval);
    
    const simulatedFilesPerSecond = Math.max(1, Math.ceil(totalFiles / 60));
    const updateInterval = 1000;
    
    currentInterval = setInterval(() => {
        const filesThisUpdate = Math.min(
            Math.floor(Math.random() * simulatedFilesPerSecond) + 1,
            totalFiles - processedFiles
        );
        
        processedFiles += filesThisUpdate;
        
        // Simular progresso de métodos também
        if (totalMethods > 0) {
            const methodsThisUpdate = Math.min(
                Math.floor(Math.random() * (filesThisUpdate * 2)) + 1,
                totalMethods - processedMethods
            );
            processedMethods += methodsThisUpdate;
        }
        
        // Gerar nome de arquivo aleatório
        updateCurrentFile(`arquivo_${Math.floor(Math.random() * 1000)}.${getRandomExtension()}`);
        
        // Atualizar barras de progresso
        updateProgressBars(processedFiles, totalFiles, processedMethods, totalMethods);
        
        if (processedFiles >= totalFiles && processedMethods >= totalMethods) {
            clearInterval(currentInterval);
            currentInterval = null;
        }
    }, updateInterval);
}

function getRandomExtension() {
    const extensions = ['java', 'cs', 'py', 'js', 'sql', 'html', 'go', 'cpp'];
    return extensions[Math.floor(Math.random() * extensions.length)];
}

function updateCurrentFile(filename) {
    const currentFileElement = document.getElementById('currentFile');
    if (currentFileElement) {
        currentFileElement.textContent = filename;
    }
}

function updateProgressBars(files, totalFiles, methods, totalMethods) {
    if (totalFiles <= 0) return;
    
    const filePercentage = Math.min(100, Math.round((files / totalFiles) * 100));
    const methodPercentage = totalMethods > 0 
        ? Math.min(100, Math.round((methods / totalMethods) * 100))
        : 100;
    
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    const filesProcessed = document.getElementById('filesProcessed');
    
    if (progressBar) {
        progressBar.style.width = `${filePercentage}%`;
        progressBar.style.background = `linear-gradient(90deg, 
            var(--vscode-primary) ${methodPercentage}%, 
            var(--deloitte-green) ${methodPercentage}%)`;
    }
    
    if (progressText) {
        progressText.textContent = `${filePercentage}%`;
    }
    
    if (filesProcessed) {
        filesProcessed.textContent = 
            `${files}/${totalFiles} arquivos | ${methods}/${totalMethods} métodos`;
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
    const analyzing = document.querySelector('.analyzing');
    const results = document.querySelector('.results');
    const errorMessage = document.querySelector('.error-message');
    
    if (!directory) {
        showError('Por favor, selecione um diretório');
        return;
    }
    
    analyzing.style.display = 'block';
    results.style.display = 'none';
    errorMessage.style.display = 'none';
    
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
        
        updateResults(data);
        analyzing.style.display = 'none';
        results.style.display = 'block';
        
        const downloadBtn = document.getElementById('downloadExcel');
        downloadBtn.href = `/download/${data.excel_file}`;
        downloadBtn.style.display = 'inline-flex';
        
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
        analyzing.style.display = 'none';
    }
});

function hideProgressElements() {
    // Ocultar os elementos de progresso
    const tempStats = document.getElementById('tempStats');
    const currentFileContainer = document.querySelector('.current-file-container');
    const progressContainer = document.querySelector('.progress-container');
    
    if (tempStats) tempStats.style.display = 'none';
    if (currentFileContainer) currentFileContainer.style.display = 'none';
    if (progressContainer) progressContainer.style.display = 'none';
}

function updateStatus(message) {
    document.querySelector('.status-text').textContent = message;
}

function showError(message) {
    const errorDiv = document.querySelector('.error-message');
    errorDiv.querySelector('p').textContent = message;
    errorDiv.style.display = 'flex';
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
