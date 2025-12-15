const API_RELATORIOS = "https://pdv-project.onrender.com/api/relatorios";
const token = localStorage.getItem("token");

const headers = {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${token}`
};

// =============================
// RELATÓRIO DE ESTOQUE
// =============================
async function carregarEstoque() {
    const tabela = document.getElementById("tabelaEstoque");

    try {
        const resposta = await fetch(`${API_RELATORIOS}/estoque`, { headers });
        const dados = await resposta.json();

        tabela.innerHTML = "";

        dados.baixo_estoque.forEach(item => {
            const linha = document.createElement("tr");
            linha.innerHTML = `
                <td>${item.codigo}</td>
                <td>${item.nome}</td>
                <td>${item.quantidade}</td>
            `;
            tabela.appendChild(linha);
        });

    } catch (e) {
        tabela.innerHTML = "<tr><td colspan='3'>Erro ao carregar dados.</td></tr>";
    }
}

// =============================
// CHAMAR FUNÇÃO EXISTENTE
// =============================
carregarEstoque();
