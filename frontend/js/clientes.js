/**
 * Módulo: Clientes
 * Gerencia cadastro, edição e listagem de clientes PJ.
 */

// ── Estado do formulário ─────────────────────────────────────
// Guarda o ID do cliente em edição. null = modo cadastro.
let clienteEditandoId = null;

// ── Máscara CNPJ ─────────────────────────────────────────────
document.getElementById("cnpj").addEventListener("input", function () {
  let v = this.value.replace(/\D/g, "").substring(0, 14);
  v = v.replace(/^(\d{2})(\d)/,           "$1.$2");
  v = v.replace(/^(\d{2})\.(\d{3})(\d)/,  "$1.$2.$3");
  v = v.replace(/\.(\d{3})(\d)/,           ".$1/$2");
  v = v.replace(/(\d{4})(\d)/,             "$1-$2");
  this.value = v;
});

// ── Máscara CEP ──────────────────────────────────────────────
document.getElementById("cep").addEventListener("input", function () {
  let v = this.value.replace(/\D/g, "").substring(0, 8);
  v = v.replace(/(\d{5})(\d)/, "$1-$2");
  this.value = v;
});

// ── Submit do formulário ──────────────────────────────────────
document.getElementById("form-cliente").addEventListener("submit", async function (e) {
  e.preventDefault();

  if (!validarFormulario()) return;

  const btn = document.getElementById("btn-salvar");
  btn.disabled = true;
  btn.innerHTML = '<span class="loading"></span> Salvando...';

  try {
    if (clienteEditandoId !== null) {
      await salvarEdicao();
    } else {
      await salvarCadastro();
    }
  } finally {
    btn.disabled = false;
    btn.innerHTML = clienteEditandoId !== null
      ? "💾 Salvar Alterações"
      : "💾 Salvar Cliente";
  }
});

// ── Cadastrar novo cliente ────────────────────────────────────
async function salvarCadastro() {
  const dados = coletarCampos({ incluirCnpj: true });

  try {
    await API.post("/clientes/", dados);
    UI.mostrarAlerta("alerta-form", "✅ Cliente cadastrado com sucesso!", "success");
    limparForm();
    carregarClientes();
  } catch (erro) {
    UI.mostrarAlerta("alerta-form", `Erro: ${erro.message}`, "error");
  }
}

// ── Salvar edição de cliente existente ────────────────────────
async function salvarEdicao() {
  // CNPJ excluído do payload — RN-02: identificador único, não editável
  const dados = coletarCampos({ incluirCnpj: false });

  try {
    await API.put(`/clientes/${clienteEditandoId}`, dados);
    UI.mostrarAlerta("alerta-form", "✅ Cliente atualizado com sucesso!", "success");
    encerrarModoEdicao();
    carregarClientes();
  } catch (erro) {
    UI.mostrarAlerta("alerta-form", `Erro: ${erro.message}`, "error");
  }
}

// ── Coleta os valores do formulário ──────────────────────────
function coletarCampos({ incluirCnpj }) {
  const dados = {
    razao_social:  document.getElementById("razao_social").value,
    nome_fantasia: document.getElementById("nome_fantasia").value || null,
    email:         document.getElementById("email").value,
    telefone:      document.getElementById("telefone").value      || null,
    cep:           document.getElementById("cep").value           || null,
    logradouro:    document.getElementById("logradouro").value    || null,
    numero:        document.getElementById("numero").value        || null,
    complemento:   document.getElementById("complemento").value   || null,
    bairro:        document.getElementById("bairro").value        || null,
    cidade:        document.getElementById("cidade").value        || null,
    estado:        document.getElementById("estado").value        || null,
  };

  if (incluirCnpj) {
    dados.cnpj = document.getElementById("cnpj").value;
  }

  return dados;
}

// ── Carregar dados do cliente no formulário para edição ───────
async function editarCliente(id) {
  try {
    const c = await API.get(`/clientes/${id}`);

    document.getElementById("cnpj").value          = c.cnpj;
    document.getElementById("razao_social").value  = c.razao_social;
    document.getElementById("nome_fantasia").value = c.nome_fantasia || "";
    document.getElementById("email").value         = c.email;
    document.getElementById("telefone").value      = c.telefone      || "";
    document.getElementById("cep").value           = c.cep           || "";
    document.getElementById("logradouro").value    = c.logradouro    || "";
    document.getElementById("numero").value        = c.numero        || "";
    document.getElementById("complemento").value   = c.complemento   || "";
    document.getElementById("bairro").value        = c.bairro        || "";
    document.getElementById("cidade").value        = c.cidade        || "";
    document.getElementById("estado").value        = c.estado        || "";

    // Bloqueia o CNPJ — RN-02: não pode ser alterado
    document.getElementById("cnpj").disabled = true;

    // Ativa o modo edição
    clienteEditandoId = id;

    document.querySelector(".card-header h2").textContent =
      `✏️ Editando: ${c.razao_social}`;
    document.getElementById("btn-salvar").innerHTML = "💾 Salvar Alterações";
    document.getElementById("btn-cancelar-edicao").style.display = "inline-flex";

    document.getElementById("form-cliente").scrollIntoView({ behavior: "smooth" });

    UI.mostrarAlerta(
      "alerta-form",
      `ℹ️ Editando cliente: ${c.razao_social}. O CNPJ não pode ser alterado.`,
      "info"
    );
  } catch (erro) {
    UI.mostrarAlerta("alerta-form", `Erro ao carregar cliente: ${erro.message}`, "error");
  }
}

// ── Sai do modo edição e restaura o formulário ────────────────
function encerrarModoEdicao() {
  clienteEditandoId = null;
  limparForm();
  document.getElementById("cnpj").disabled = false;
  document.querySelector(".card-header h2").textContent =
    "Cadastro de Cliente (Pessoa Jurídica)";
  document.getElementById("btn-salvar").innerHTML = "💾 Salvar Cliente";
  document.getElementById("btn-cancelar-edicao").style.display = "none";
}

// ── Validação do formulário ───────────────────────────────────
function validarFormulario() {
  let valido = true;

  // CNPJ — só valida no modo cadastro (em edição está bloqueado)
  if (clienteEditandoId === null) {
    const cnpjDigitos = document.getElementById("cnpj").value.replace(/\D/g, "");
    const errCnpj     = document.getElementById("err-cnpj");
    const inputCnpj   = document.getElementById("cnpj");

    if (cnpjDigitos.length === 11) {
      errCnpj.textContent = "❌ CPF não é aceito. O sistema atende apenas Pessoas Jurídicas (CNPJ).";
      errCnpj.classList.add("visible");
      inputCnpj.classList.add("error");
      valido = false;
    } else if (cnpjDigitos.length !== 14) {
      errCnpj.textContent = "CNPJ inválido. Informe todos os 14 dígitos.";
      errCnpj.classList.add("visible");
      inputCnpj.classList.add("error");
      valido = false;
    } else {
      errCnpj.classList.remove("visible");
      inputCnpj.classList.remove("error");
    }
  }

  // Razão Social
  const razao    = document.getElementById("razao_social").value;
  const errRazao = document.getElementById("err-razao");
  if (!razao || razao.trim().length < 3) {
    errRazao.classList.add("visible");
    document.getElementById("razao_social").classList.add("error");
    valido = false;
  } else {
    errRazao.classList.remove("visible");
    document.getElementById("razao_social").classList.remove("error");
  }

  // E-mail
  const email    = document.getElementById("email").value;
  const errEmail = document.getElementById("err-email");
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    errEmail.classList.add("visible");
    document.getElementById("email").classList.add("error");
    valido = false;
  } else {
    errEmail.classList.remove("visible");
    document.getElementById("email").classList.remove("error");
  }

  return valido;
}

// ── Limpar formulário ─────────────────────────────────────────
function limparForm() {
  document.getElementById("form-cliente").reset();
  document.getElementById("cnpj").disabled = false;
  document.querySelectorAll(".field-error").forEach((el) =>
    el.classList.remove("visible")
  );
  document.querySelectorAll(".error").forEach((el) =>
    el.classList.remove("error")
  );
}

// ── Carregar lista de clientes ────────────────────────────────
async function carregarClientes() {
  const tbody = document.getElementById("tbody-clientes");
  tbody.innerHTML = `
    <tr>
      <td colspan="8" style="text-align:center; padding:2rem; color:var(--cinza-escuro)">
        ⏳ Carregando clientes...
      </td>
    </tr>
  `;

  try {
    const clientes = await API.get("/clientes/");

    if (!clientes.length) {
      UI.tabelaVazia("tbody-clientes", 8);
      return;
    }

    tbody.innerHTML = clientes.map((c) => `
      <tr>
        <td>${c.id_cliente}</td>
        <td><code>${c.cnpj}</code></td>
        <td><strong>${c.razao_social}</strong></td>
        <td>${c.nome_fantasia || "—"}</td>
        <td>${c.email}</td>
        <td>${c.cidade ? `${c.cidade}/${c.estado}` : "—"}</td>
        <td>${UI.formatarData(c.data_cadastro)}</td>
        <td class="acoes">
          <button class="btn btn-warning btn-sm"
                  title="Editar cliente"
                  onclick="editarCliente(${c.id_cliente})">
            ✏️
          </button>
          <button class="btn btn-danger btn-sm"
                  title="Excluir cliente"
                  onclick="deletarCliente(${c.id_cliente}, '${c.razao_social.replace(/'/g, "\\'")}')">
            🗑️
          </button>
        </td>
      </tr>
    `).join("");

  } catch (erro) {
    // ✅ CORRIGIDO — consistente com os outros módulos
    UI.tabelaVazia("tbody-clientes", 8);
    UI.mostrarAlerta("alerta-form", `Erro ao carregar clientes: ${erro.message}`, "error");
  }
}

// ── Deletar cliente ───────────────────────────────────────────
async function deletarCliente(id, nome) {
  // ✅ CORRIGIDO — substituído confirm() por UI.mostrarAlerta + flag de confirmação
  UI.mostrarAlerta(
    "alerta-form",
    `⚠️ Tem a certeza que deseja remover "<strong>${nome}</strong>"?
     <button class="btn btn-danger btn-sm" style="margin-left:1rem"
             onclick="confirmarDelecao(${id})">
       Sim, remover
     </button>`,
    "info"
  );
}

async function confirmarDelecao(id) {
  // Se estava editando esse cliente, cancela a edição antes
  if (clienteEditandoId === id) encerrarModoEdicao();

  try {
    await API.delete(`/clientes/${id}`);
    UI.mostrarAlerta("alerta-form", "✅ Cliente removido com sucesso.", "success");
    carregarClientes();
  } catch (erro) {
    UI.mostrarAlerta("alerta-form", `Erro: ${erro.message}`, "error");
  }
}

// ── Inicialização ─────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", carregarClientes);
