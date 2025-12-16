const token = localStorage.getItem("token");
const urlCategorias = "https://pdv-backend-dp61.onrender.com/api/categorias";

// CADASTRAR CATEGORIA
document.getElementById("formCategoria").addEventListener("submit", async (e) => {
  e.preventDefault();

  const nome = document.getElementById("nomeCategoria").value;

  const resposta = await fetch(urlCategorias, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify({ nome })
  });

  const dados = await resposta.json();

  if (!resposta.ok) {
    alert(dados.erro || "Erro ao cadastrar categoria.");
    return;
  }

  alert("Categoria cadastrada com sucesso!");
  document.getElementById("formCategoria").reset();
  listarCategorias();
});

// LISTAR CATEGORIAS
async function listarCategorias() {
  const resposta = await fetch(urlCategorias, {
    headers: { "Authorization": `Bearer ${token}` }
  });

  const categorias = await resposta.json();
  const tbody = document.querySelector("#tabelaCategorias tbody");
  tbody.innerHTML = "";

  categorias.forEach(cat => {
    const tr = document.createElement("tr");

    tr.innerHTML = `
      <td style="padding:10px; border:1px solid #4b0082;">${cat.id}</td>
      <td style="padding:10px; border:1px solid #4b0082;">${cat.nome}</td>
      <td style="padding:10px; border:1px solid #4b0082;">
        <button onclick="excluirCategoria(${cat.id})"
          style="background:#7f00ff; color:white; border:none; padding:5px 10px; border-radius:4px; cursor:pointer;">
          Excluir
        </button>
      </td>
    `;

    tbody.appendChild(tr);
  });
}

// EXCLUIR CATEGORIA
async function excluirCategoria(id) {
  if (!confirm("Deseja realmente excluir esta categoria?")) return;

  const resposta = await fetch(`${urlCategorias}/${id}`, {
    method: "DELETE",
    headers: { "Authorization": `Bearer ${token}` }
  });

  if (resposta.ok) {
    alert("Categoria excluída com sucesso!");
    listarCategorias();
  } else {
    alert("Erro ao excluir categoria.");
  }
}

// INICIAR LISTAGEM
listarCategorias();