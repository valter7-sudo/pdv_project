const token = localStorage.getItem("token");
const urlVendas = "https://pdv-backend-dp61.onrender.com/api/vendas";

// GERAR RELATÓRIO
async function gerarRelatorio() {
  const inicio = document.getElementById("dataInicio").value;
  const fim = document.getElementById("dataFim").value;

  if (!inicio || !fim) {
    alert("Selecione a data inicial e final.");
    return;
  }

  const resposta = await fetch(`${urlVendas}?inicio=${inicio}&fim=${fim}`, {
    headers: { "Authorization": `Bearer ${token}` }
  });

  const vendas = await resposta.json();

  preencherTabela(vendas);
  atualizarResumo(vendas);
}

// ATUALIZAR RESUMO
function atualizarResumo(vendas) {
  let totalVendido = 0;
  let totalItens = 0;

  vendas.forEach(v => {
    totalVendido += v.total;
    totalItens += v.itens.reduce((soma, item) => soma + item.qtd, 0);
  });

  document.getElementById("totalVendido").innerText = 
    `R$ ${totalVendido.toFixed(2)}`;

  document.getElementById("totalItens").innerText = totalItens;
}

// PREENCHER TABELA
function preencherTabela(vendas) {
  const tbody = document.querySelector("#tabelaRelatorios tbody");
  tbody.innerHTML = "";

  vendas.forEach(v => {
    const tr = document.createElement("tr");

    tr.innerHTML = `
      <td style="padding:10px; border:1px solid #4b0082;">${v.id}</td>
      <td style="padding:10px; border:1px solid #4b0082;">${v.data}</td>
      <td style="padding:10px; border:1px solid #4b0082;">R$ ${v.total.toFixed(2)}</td>
      <td style="padding:10px; border:1px solid #4b0082;">${v.itens.length}</td>
    `;

    tbody.appendChild(tr);
  });
}