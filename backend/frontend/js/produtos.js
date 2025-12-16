const token = localStorage.getItem("token");
const url = "https://pdv-backend-dp61.onrender.com/api/produtos";

// CADASTRAR PRODUTO
document.getElementById("formProduto").addEventListener("submit", async (e) => {
  e.preventDefault();

  const nome = document.getElementById("nome").value;
  const preco = parseFloat(document.getElementById("preco").value);
  const estoque = parseInt(document.getElementById("estoque").value);

  const resposta = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify({ nome, preco, estoque })
  });

  const dados = await resposta.json();

  if (!resposta.ok) {
    alert(dados.erro || "Erro ao cadastrar produto.");
    return;
  }

  alert("Produto cadastrado com sucesso!");
  document.getElementById("formProduto").reset();
  listarProdutos();
});

// LISTAR PRODUTOS
async function listarProdutos() {
  const resposta = await fetch(url, {
    headers: { "Authorization": `Bearer ${token}` }
  });

  const dados = await resposta.json();
  const tbody = document.querySelector("#tabelaProdutos tbody");
  tbody.innerHTML = "";

  dados.forEach(produto => {
    const tr = document.createElement("tr");

    tr.innerHTML = `
      <td style="padding:10px; border:1px solid #4b0082;">${produto.id}</td>
      <td style="padding:10px; border:1px solid #4b0082;">${produto.nome}</td>
      <td style="padding:10px; border:1px solid #4b0082;">R$ ${produto.preco.toFixed(2)}</td>
      <td style="padding:10px; border:1px solid #4b0082;">${produto.estoque}</td>
      <td style="padding:10px; border:1px solid #4b0082;">
        <button onclick="excluirProduto(${produto.id})" style="background:#7f00ff; color:white; border:none; padding:5px 10px; border-radius:4px; cursor:pointer;">Excluir</button>
      </td>
    `;

    tbody.appendChild(tr);
  });
}

// EXCLUIR PRODUTO
async function excluirProduto(id) {
  if (!confirm("Deseja realmente excluir este produto?")) return;

  const resposta = await fetch(`${url}/${id}`, {
    method: "DELETE",
    headers: { "Authorization": `Bearer ${token}` }
  });

  if (resposta.ok) {
    alert("Produto excluído com sucesso!");
    listarProdutos();
  } else {
    alert("Erro ao excluir produto.");
  }
}

// INICIAR LISTAGEM
listarProdutos();