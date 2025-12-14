const API_RELATORIOS = "http://127.0.0.1:5000/api/relatorios";
const token = localStorage.getItem("token");

const headers = {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${token}`
};

// =============================
// VENDAS POR DIA
// =============================
async function carregarVendasPorDia() {
    const tabela = document.getElementById("tabelaVendasDia");

    try {
        const resposta = await fetch(`${API_RELATORIOS}/vendas_por_dia`, { headers });
        const dados = await resposta.json();

        tabela.innerHTML = "";

        dados.forEach(item => {
            const linha = document.createElement("tr");
            linha.innerHTML = `
                <td>${item.dia}</td>
                <td>R$ ${item.total.toFixed(2)}</td>
            `;
            tabela.appendChild(linha);
        });

    } catch (e) {
        tabela.innerHTML = "<tr><td colspan='2'>Erro ao carregar dados.</td></tr>";
    }
}

// =============================
// TOTALIZADOR
// =============================
async function carregarTotalizador() {
    try {
        const resposta = await fetch(`${API_RELATORIOS}/totalizador`, { headers });
        const dados = await resposta.json();

        document.getElementById("totalVendido").textContent = dados.total_vendido.toFixed(2);
        document.getElementById("quantidadeVendas").textContent = dados.quantidade_vendas;

    } catch (e) {
        document.getElementById("totalVendido").textContent = "Erro";
        document.getElementById("quantidadeVendas").textContent = "Erro";
    }
}

// =============================
// PRODUTOS MAIS VENDIDOS
// =============================
async function carregarMaisVendidos() {
    const tabela = document.getElementById("tabelaMaisVendidos");

    try {
        const resposta = await fetch(`${API_RELATORIOS}/produtos_mais_vendidos`, { headers });
        const dados = await resposta.json();

        tabela.innerHTML = "";

        dados.forEach(item => {
            const linha = document.createElement("tr");
            linha.innerHTML = `
                <td>${item.produto}</td>
                <td>${item.quantidade_vendida}</td>
            `;
            tabela.appendChild(linha);
        });

    } catch (e) {
        tabela.innerHTML = "<tr><td colspan='2'>Erro ao carregar dados.</td></tr>";
    }
}

// =============================
// MOVIMENTAÇÃO DE ESTOQUE
// =============================
async function carregarEstoque() {
    const tabela = document.getElementById("tabelaEstoque");

    try {
        const resposta = await fetch(`${API_RELATORIOS}/estoque`, { headers });
        const dados = await resposta.json();

        tabela.innerHTML = "";

        dados.forEach(item => {
            const linha = document.createElement("tr");
            linha.innerHTML = `
                <td>${item.produto}</td>
                <td>${item.tipo}</td>
                <td>${item.quantidade}</td>
                <td>${item.motivo}</td>
                <td>${item.data_hora}</td>
                <td>${item.usuario}</td>
            `;
            tabela.appendChild(linha);
        });

    } catch (e) {
        tabela.innerHTML = "<tr><td colspan='6'>Erro ao carregar dados.</td></tr>";
    }
}

// =============================
// CHAMAR TODAS AS FUNÇÕES
// =============================
carregarVendasPorDia();
carregarTotalizador();
carregarMaisVendidos();
carregarEstoque();
