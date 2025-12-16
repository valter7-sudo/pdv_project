const token = localStorage.getItem("token");
const urlProdutos = "https://pdv-backend-dp61.onrender.com/api/produtos";
const urlVendas = "https://pdv-backend-dp61.onrender.com/api/vendas";

let carrinho = [];

// BUSCAR PRODUTOS ENQUANTO DIGITA
document.getElementById("buscaProduto").addEventListener("input", async (e) => {
  const termo = e.target.value.trim();

  if (termo.length < 2) {
    document.getElementById("listaBusca").style.display = "none";
    return;
  }

  const resposta = await fetch(urlProdutos, {
    headers: { "Authorization": `Bearer ${token}` }
  });

  const produtos = await resposta.json();

  const filtrados = produtos.filter(p =>
    p.nome.toLowerCase().includes(termo.toLowerCase())
  );

  mostrarResultados(filtrados);
});

// MOSTRAR RESULTADOS DA BUSCA
function mostrarResultados(lista) {
  const box = document.getElementById("listaBusca");
  box.innerHTML = "";

  if (lista.length === 0) {
    box.style.display = "none";
    return;
  }

  lista.forEach(produto => {
    const div = document.createElement("div");
    div.style.padding = "10px";
    div.style.cursor = "pointer";
    div.style.borderBottom = "1px solid #4b0082";
    div.style.color = "#00bfff";

    div.innerHTML = `${produto.nome} — R$ ${produto.preco.toFixed(2)}`;

    div.onclick = () => adicionarCarrinho(produto);

    box.appendChild(div);
  });

  box.style.display = "block";
}

// ADICIONAR AO CARRINHO
function adicionarCarrinho(produto) {
  const itemExistente = carrinho.find(i => i.id === produto.id);

  if (itemExistente) {
    itemExistente.qtd++;
  } else {
    carrinho.push({
      id: produto.id,
      nome: produto.nome,
      preco: produto.preco,
      qtd: 1
    });
  }

  atualizarCarrinho();
  document.getElementById("listaBusca").style.display = "none";
  document.getElementById("buscaProduto").value = "";
}

// ATUALIZAR TABELA DO CARRINHO
function atualizarCarrinho() {
  const tbody = document.querySelector("#tabelaCarrinho tbody");
  tbody.innerHTML = "";

  let total = 0;

  carrinho.forEach(item => {
    const subtotal = item.preco * item.qtd;
    total += subtotal;

    const tr = document.createElement("tr");

    tr.innerHTML = `
      <td style="padding:10px; border:1px solid #4b0082;">${item.nome}</td>
      <td style="padding:10px; border:1px solid #4b0082;">${item.qtd}</td>
      <td style="padding:10px; border:1px solid #4b0082;">R$ ${item.preco.toFixed(2)}</td>
      <td style="padding:10px; border:1px solid #4b0082;">R$ ${subtotal.toFixed(2)}</td>
      <td style="padding:10px; border:1px solid #4b0082;">
        <button onclick="removerItem(${item.id})" 
          style="background:#7f00ff; color:white; border:none; padding:5px 10px; border-radius:4px; cursor:pointer;">
          Remover
        </button>
      </td>
    `;

    tbody.appendChild(tr);
  });

  document.getElementById("totalVenda").innerText = `R$ ${total.toFixed(2)}`;
}

// REMOVER ITEM DO CARRINHO
function removerItem(id) {
  carrinho = carrinho.filter(i => i.id !== id);
  atualizarCarrinho();
}

// FINALIZAR VENDA
async function finalizarVenda() {
  if (carrinho.length === 0) {
    alert("O carrinho está vazio.");
    return;
  }

  const resposta = await fetch(urlVendas, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify({ itens: carrinho })
  });

  const dados = await resposta.json();

  if (!resposta.ok) {
    alert(dados.erro || "Erro ao finalizar venda.");
    return;
  }

  alert("Venda finalizada com sucesso!");

  carrinho = [];
  atualizarCarrinho();
}