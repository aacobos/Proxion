function login() {
    const username = document.getElementById("username").value; 
    const password = document.getElementById("password").value;
    const errorMsg = document.getElementById("error-msg");

    // Usuário e senha de teste
    if (username === "admin" && password === "1234") {
        sessionStorage.setItem("auth", "true");
        window.location.href = "Projeto/pages/dashboard.html";
    } else {
        errorMsg.style.display = "block";
    }
}

function forgotPassword() {
    alert("Entre em contato com o administrador do sistema para recuperar sua senha.");
}