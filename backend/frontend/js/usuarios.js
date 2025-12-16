const token = localStorage.getItem("token");
const urlUsuarios = "https://pdv-backend-dp61.onrender.com/api/usuarios";

// CADASTRAR USUÁRIO
document.getElementById("formUsuario").addEventListener("submit", async (e) => {
  e.preventDefault();

  const nome = document.getElementById("nomeUsuario").value;
  const email = document.getElementById("emailUsuario").value;
  const senha = document.getElementById("senhaUsuario").value;

  const resposta = await fetch(urlUsuarios, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify({ nome, email, senha })
  });

  const dados = await resposta.json();

  if (!resposta.ok) {
    alert(dados.erro || "Erro ao cadastrar usuário.");
    return;
  }

  alert("Usuário cadastrado com sucesso!");
  document.getElementById("formUsuario").reset();
  listarUsuarios();
});

// LISTAR USUÁRIOS
async function listarUsuarios() {
  const resposta = await fetch(urlUsuarios, {
    headers: { "Authorization": `Bearer ${token}` }
  });

  const usuarios = await resposta.json();
  const tbody = document.querySelector("#tabelaUsuarios tbody");
  tbody.innerHTML = "";

  usuarios.forEach(user => {
    const tr = document.createElement("tr");

    tr.innerHTML = `
      <td style="padding:10px; border:1px solid #4b0082;">${user.id}</td>
      <td style="padding:10px; border:1px solid #4b0082;">${user.nome}</td>
      <td style="padding:10px; border:1px solid #4b0082;">${user.email}</td>
      <td style="padding:10px; border:1px solid #4b0082;">
        <button onclick="excluirUsuario(${user.id})"
          style="background:#7f00ff; color:white; border:none; padding:5px 10px; border-radius:4px; cursor:pointer;">
          Excluir
        </button>
      </td>
    `;

    tbody.appendChild(tr);
  });
}

// EXCLUIR USUÁRIO
async function excluirUsuario(id) {
  if (!confirm("Deseja realmente excluir este usuário?")) return;

  const resposta = await fetch(`${urlUsuarios}/${id}`, {
    method: "DELETE",
    headers: { "Authorization": `Bearer ${token}` }
  });

  if (resposta.ok) {
    alert("Usuário excluído com sucesso!");
    listarUsuarios();
  } else {
    alert("Erro ao excluir usuário.");
  }
}

// INICIAR LISTAGEM
listarUsuarios();