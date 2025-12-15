document.getElementById("formLogin").addEventListener("submit", async (e) => {
  e.preventDefault();

  const usuario = document.getElementById("usuario").value;
  const senha = document.getElementById("senha").value;

  const resposta = await fetch("https://pdv-backend-dp61.onrender.com/api/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ usuario, senha })
  });

  const dados = await resposta.json();

  if (!resposta.ok) {
    alert(dados.erro);
    return;
  }

  alert("Login realizado com sucesso!");
  localStorage.setItem("token", dados.token);
  window.location.href = "index.html"; // ou home.html se você quiser criar depois
});