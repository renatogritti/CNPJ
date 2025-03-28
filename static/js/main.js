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

function showTemporaryStats(stats) {
    const analyzing = document.querySelector('.analyzing');
    const codeStats = document.createElement('div');
    codeStats.className = 'code-stats';
    codeStats.id = 'tempStats';
    codeStats.innerHTML = `
        <pre>Analisando:
${stats.subdirs} subdiretórios
${stats.files} arquivos de Desenvolvimento
${stats.lines.toLocaleString()} linhas de código
${stats.methods} métodos com CNPJ</pre>
    `;
    analyzing.appendChild(codeStats);
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
        
        updateStatus('Iniciando análise com LLM...');
        
        const formData = new FormData();
        formData.append('directory', directory);
        
        updateStatus('Analisando impactos com LLM...');
        
        const response = await retryFetch('/analyze', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        // Remover estatísticas temporárias apenas após sucesso
        const tempStats = document.getElementById('tempStats');
        if (tempStats) tempStats.remove();
        
        updateResults(data);
        analyzing.style.display = 'none';
        results.style.display = 'block';
        
        const downloadBtn = document.getElementById('downloadExcel');
        downloadBtn.href = `/download/${data.excel_file}`;
        downloadBtn.style.display = 'inline-flex';
        
    } catch (error) {
        // Remover estatísticas temporárias em caso de erro
        const tempStats = document.getElementById('tempStats');
        if (tempStats) tempStats.remove();
        
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
