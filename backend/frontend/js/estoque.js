const token = localStorage.getItem("token");
const urlProdutos = "https://pdv-backend-dp61.onrender.com/api/produtos";

// LISTAR ESTOQUE
async function listarEstoque() {
  const resposta = await fetch(urlProdutos, {
    headers: { "Authorization": `Bearer ${token}` }
  });

  const produtos = await resposta.json();
  preencherTabela(produtos);
}

// PREENCHER TABELA
function preencherTabela(produtos) {
  const tbody = document.querySelector("#tabelaEstoque tbody");
  tbody.innerHTML = "";

  produtos.forEach(produto => {
    const tr = document.createElement("tr");

    tr.innerHTML = `
      <td style="padding:10px; border:1px solid #4b0082;">${produto.id}</td>
      <td style="padding:10px; border:1px solid #4b0082;">${produto.nome}</td>
      <td style="padding:10px; border:1px solid #4b0082;">${produto.estoque}</td>
      <td style="padding:10px; border:1px solid #4b0082;">
        <button onclick="ajustarEstoque(${produto.id}, 'entrada')" 
          style="background:#00bfff; color:black; border:none; padding:5px 10px; border-radius:4px; cursor:pointer;">
          + Entrada
        </button>

        <button onclick="ajustarEstoque(${produto.id}, 'saida')" 
          style="background:#7f00ff; color:white; border:none; padding:5px 10px; border-radius:4px; cursor:pointer;">
          - Saída
        </button>
      </td>
    `;

    tbody.appendChild(tr);
  });
}

// AJUSTAR ESTOQUE
async function ajustarEstoque(id, tipo) {
  const qtd = prompt(`Quantidade para ${tipo === 'entrada' ? 'entrada' : 'saída'}:`);

  if (!qtd || isNaN(qtd) || qtd <= 0) {
    alert("Quantidade inválida.");
    return;
  }

  const resposta = await fetch(`${urlProdutos}/${id}/estoque`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify({ tipo, quantidade: parseInt(qtd) })
  });

  const dados = await resposta.json();

  if (!resposta.ok) {
    alert(dados.erro || "Erro ao ajustar estoque.");
    return;
  }

  alert("Estoque atualizado com sucesso!");
  listarEstoque();
}

// BUSCA DE PRODUTOS
document.getElementById("buscaEstoque").addEventListener("input", async (e) => {
  const termo = e.target.value.toLowerCase();

  const resposta = await fetch(urlProdutos, {
    headers: { "Authorization": `Bearer ${token}` }
  });

  const produtos = await resposta.json();

  const filtrados = produtos.filter(p =>
    p.nome.toLowerCase().includes(termo)
  );

  preencherTabela(filtrados);
});

// INICIAR
listarEstoque();