const token = localStorage.getItem("token");
const urlCaixa = "https://pdv-backend-dp61.onrender.com/api/caixa";

// ATUALIZAR STATUS DO CAIXA
async function carregarStatus() {
  const resposta = await fetch(`${urlCaixa}/status`, {
    headers: { "Authorization": `Bearer ${token}` }
  });

  const dados = await resposta.json();

  const texto = document.getElementById("textoStatus");

  if (dados.aberto) {
    texto.innerHTML = `✅ Caixa aberto — Saldo atual: <strong>R$ ${dados.saldo.toFixed(2)}</strong>`;
    texto.style.color = "#00ff99";
  } else {
    texto.innerHTML = "❌ Caixa fechado";
    texto.style.color = "#ff5555";
  }

  listarMovimentacoes();
}

// ABRIR CAIXA
async function abrirCaixa() {
  const valor = prompt("Valor inicial do caixa:");

  if (!valor || isNaN(valor) || valor < 0) {
    alert("Valor inválido.");
    return;
  }

  const resposta = await fetch(`${urlCaixa}/abrir`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify({ valorInicial: parseFloat(valor) })
  });

  const dados = await resposta.json();

  if (!resposta.ok) {
    alert(dados.erro || "Erro ao abrir caixa.");
    return;
  }

  alert("Caixa aberto com sucesso!");
  carregarStatus();
}

// FECHAR CAIXA
async function fecharCaixa() {
  if (!confirm("Deseja realmente fechar o caixa?")) return;

  const resposta = await fetch(`${urlCaixa}/fechar`, {
    method: "POST",
    headers: { "Authorization": `Bearer ${token}` }
  });

  const dados = await resposta.json();

  if (!resposta.ok) {
    alert(dados.erro || "Erro ao fechar caixa.");
    return;
  }

  alert(`Caixa fechado! Total final: R$ ${dados.total.toFixed(2)}`);
  carregarStatus();
}

// REGISTRAR MOVIMENTAÇÃO
async function registrarMovimentacao() {
  const tipo = document.getElementById("tipoMov").value;
  const valor = parseFloat(document.getElementById("valorMov").value);

  if (!valor || valor <= 0) {
    alert("Valor inválido.");
    return;
  }

  const resposta = await fetch(`${urlCaixa}/movimentar`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify({ tipo, valor })
  });

  const dados = await resposta.json();

  if (!resposta.ok) {
    alert(dados.erro || "Erro ao registrar movimentação.");
    return;
  }

  alert("Movimentação registrada!");
  document.getElementById("valorMov").value = "";
  carregarStatus();
}

// LISTAR MOVIMENTAÇÕES
async function listarMovimentacoes() {
  const resposta = await fetch(`${urlCaixa}/movimentacoes`, {
    headers: { "Authorization": `Bearer ${token}` }
  });

  const movs = await resposta.json();
  const tbody = document.querySelector("#tabelaCaixa tbody");
  tbody.innerHTML = "";

  movs.forEach(m => {
    const tr = document.createElement("tr");

    tr.innerHTML = `
      <td style="padding:10px; border:1px solid #4b0082;">${m.id}</td>
      <td style="padding:10px; border:1px solid #4b0082;">${m.tipo}</td>
      <td style="padding:10px; border:1px solid #4b0082;">R$ ${m.valor.toFixed(2)}</td>
      <td style="padding:10px; border:1px solid #4b0082;">${m.data}</td>
    `;

    tbody.appendChild(tr);
  });
}

// INICIAR
carregarStatus();