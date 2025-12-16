const token = localStorage.getItem("token");
const urlClientes = "https://pdv-backend-dp61.onrender.com/api/clientes";

// CADASTRAR CLIENTE
document.getElementById("formCliente").addEventListener("submit", async (e) => {
  e.preventDefault();

  const nome = document.getElementById("nomeCliente").value;
  const telefone = document.getElementById("telefoneCliente").value;
  const email = document.getElementById("emailCliente").value;

  const resposta = await fetch(urlClientes, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify({ nome, telefone, email })
  });

  const dados = await resposta.json();

  if (!resposta.ok) {
    alert(dados.erro || "Erro ao cadastrar cliente.");
    return;
  }

  alert("Cliente cadastrado com sucesso!");
  document.getElementById("formCliente").reset();
  listarClientes();
});

// LISTAR CLIENTES
async function listarClientes() {
  const resposta = await fetch(urlClientes, {
    headers: { "Authorization": `Bearer ${token}` }
  });

  const clientes = await resposta.json();
  const tbody = document.querySelector("#tabelaClientes tbody");
  tbody.innerHTML = "";

  clientes.forEach(cli => {
    const tr = document.createElement("tr");

    tr.innerHTML = `
      <td style="padding:10px; border:1px solid #4b0082;">${cli.id}</td>
      <td style="padding:10px; border:1px solid #4b0082;">${cli.nome}</td>
      <td style="padding:10px; border:1px solid #4b0082;">${cli.telefone || "-"}</td>
      <td style="padding:10px; border:1px solid #4b0082;">${cli.email || "-"}</td>
      <td style="padding:10px; border:1px solid #4b0082;">
        <button onclick="excluirCliente(${cli.id})"
          style="background:#7f00ff; color:white; border:none; padding:5px 10px; border-radius:4px; cursor:pointer;">
          Excluir
        </button>
      </td>
    `;

    tbody.appendChild(tr);
  });
}

// EXCLUIR CLIENTE
async function excluirCliente(id) {
  if (!confirm("Deseja realmente excluir este cliente?")) return;

  const resposta = await fetch(`${urlClientes}/${id}`, {
    method: "DELETE",
    headers: { "Authorization": `Bearer ${token}` }
  });

  if (resposta.ok) {
    alert("Cliente excluído com sucesso!");
    listarClientes();
  } else {
    alert("Erro ao excluir cliente.");
  }
}

// INICIAR LISTAGEM
listarClientes();