const token = localStorage.getItem("token");
const urlConfig = "https://pdv-backend-dp61.onrender.com/api/config";

// CARREGAR CONFIGURAÇÕES AO INICIAR
async function carregarConfiguracoes() {
  const resposta = await fetch(urlConfig, {
    headers: { "Authorization": `Bearer ${token}` }
  });

  const dados = await resposta.json();

  if (!resposta.ok) {
    console.warn("Nenhuma configuração encontrada.");
    return;
  }

  // Dados da empresa
  document.getElementById("nomeEmpresa").value = dados.nomeEmpresa || "";
  document.getElementById("cnpjEmpresa").value = dados.cnpjEmpresa || "";
  document.getElementById("enderecoEmpresa").value = dados.enderecoEmpresa || "";

  // Preferências
  document.getElementById("temaSistema").value = dados.tema || "dark";
  document.getElementById("notificacoesSistema").value = dados.notificacoes || "on";
}

// SALVAR DADOS DA EMPRESA
document.getElementById("formEmpresa").addEventListener("submit", async (e) => {
  e.preventDefault();

  const nomeEmpresa = document.getElementById("nomeEmpresa").value;
  const cnpjEmpresa = document.getElementById("cnpjEmpresa").value;
  const enderecoEmpresa = document.getElementById("enderecoEmpresa").value;

  const resposta = await fetch(`${urlConfig}/empresa`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify({ nomeEmpresa, cnpjEmpresa, enderecoEmpresa })
  });

  const dados = await resposta.json();

  if (!resposta.ok) {
    alert(dados.erro || "Erro ao salvar dados da empresa.");
    return;
  }

  alert("Dados da empresa salvos com sucesso!");
});

// SALVAR PREFERÊNCIAS DO SISTEMA
async function salvarPreferencias() {
  const tema = document.getElementById("temaSistema").value;
  const notificacoes = document.getElementById("notificacoesSistema").value;

  const resposta = await fetch(`${urlConfig}/preferencias`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify({ tema, notificacoes })
  });

  const dados = await resposta.json();

  if (!resposta.ok) {
    alert(dados.erro || "Erro ao salvar preferências.");
    return;
  }

  alert("Preferências salvas com sucesso!");
}

// INICIAR
carregarConfiguracoes();