const token = localStorage.getItem("token");
const urlFinanceiro = "https://pdv-backend-dp61.onrender.com/api/financeiro";

// REGISTRAR LANÇAMENTO
async function registrarLancamento() {
  const tipo = document.getElementById("tipoLanc").value;
  const descricao = document.getElementById("descricaoLanc").value;
  const valor = parseFloat(document.getElementById("valorLanc").value);

  if (!descricao || !valor || valor <= 0) {
    alert("Preencha todos os campos corretamente.");
    return;
  }

  const resposta = await fetch(urlFinanceiro, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify({ tipo, descricao, valor })
  });

  const dados = await resposta.json();

  if (!resposta.ok) {
    alert(dados.erro || "Erro ao registrar lançamento.");
    return;
  }

  alert("Lançamento registrado com sucesso!");
  document.getElementById("descricaoLanc").value = "";
  document.getElementById("valorLanc").value = "";
  carregarLancamentos();
}

// LISTAR LANÇAMENTOS
async function carregarLancamentos() {
  const resposta = await fetch(urlFinanceiro, {
    headers: { "Authorization": `Bearer ${token}` }
  });

  const lancamentos = await resposta.json();
  preencherTabela(lancamentos);
  atualizarResumo(lancamentos);
}

// ATUALIZAR RESUMO
function atualizarResumo(lancamentos) {
  let totalReceber = 0;
  let totalPagar = 0;

  lancamentos.forEach(l => {
    if (l.tipo === "receber") totalReceber += l.valor;
    if (l.tipo === "pagar") totalPagar += l.valor;
  });

  document.getElementById("totalReceber").innerText = `R$ ${totalReceber.toFixed(2)}`;
  document.getElementById("totalPagar").innerText = `R$ ${totalPagar.toFixed(2)}`;
}

// PREENCHER TABELA
function preencherTabela(lancamentos) {
  const tbody = document.querySelector("#tabelaFinanceiro tbody");
  tbody.innerHTML = "";

  lancamentos.forEach(l => {
    const tr = document.createElement("tr");

    tr.innerHTML = `
      <td style="padding:10px; border:1px solid #4b0082;">${l.id}</td>
      <td style="padding:10px; border:1px solid #4b0082;">${l.tipo}</td>
      <td style="padding:10px; border:1px solid #4b0082;">${l.descricao}</td>
      <td style="padding:10px; border:1px solid #4b0082;">R$ ${l.valor.toFixed(2)}</td>
      <td style="padding:10px; border:1px solid #4b0082;">${l.data}</td>
      <td style="padding:10px; border:1px solid #4b0082;">
        <button onclick="excluirLancamento(${l.id})"
          style="background:#7f00ff; color:white; border:none; padding:5px 10px; border-radius:4px; cursor:pointer;">
          Excluir
        </button>
      </td>
    `;

    tbody.appendChild(tr);
  });
}

// EXCLUIR LANÇAMENTO
async function excluirLancamento(id) {
  if (!confirm("Deseja realmente excluir este lançamento?")) return;

  const resposta = await fetch(`${urlFinanceiro}/${id}`, {
    method: "DELETE",
    headers: { "Authorization": `Bearer ${token}` }
  });

  if (resposta.ok) {
    alert("Lançamento excluído com sucesso!");
    carregarLancamentos();
  } else {
    alert("Erro ao excluir lançamento.");
  }
}

// INICIAR
carregarLancamentos();