// ============================================================
// empregados.js — Madeira Verde
// ✅ Listar | ✅ Criar | ✅ Editar (PUT) | ✅ Excluir | ✅ Visualizar
// PADRÃO: API.get/post/put/delete | UI.mostrarAlerta/formatarMoeda/etc.
// NUNCA redeclarar const API — já existe em api.js
// NUNCA usar alert(), confirm(), console.error(), fetch() direto
// ============================================================

const formEmpregado = document.getElementById('form-empregado');
const tabelaBody    = document.getElementById('tbody-empregados');
const btnCancelar   = document.getElementById('btn-cancelar-edicao');

let editandoId = null;

// ============================================================
// CARREGAR LISTA
// ============================================================
async function carregarEmpregados() {
  try {
    const data = await API.get('/empregados');
    await preencherSelectSupervisor(data);
    renderizarTabela(data);
  } catch (err) {
    UI.mostrarAlerta('alerta-emp',
      'Erro ao carregar empregados: ' + err.message, 'error');
  }
}

// ── Preenche <select> de supervisor ─────────────────────────
async function preencherSelectSupervisor(empregados) {
  const sel = document.getElementById('supervisor');
  if (!sel) return;

  const valorAtual = sel.value;
  sel.innerHTML = '<option value="">— Sem supervisor —</option>';

  empregados.forEach(e => {
    // ✅ Não exibe o próprio empregado em edição como opção
    if (editandoId && e.id_empregado === editandoId) return;

    const opt = document.createElement('option');
    opt.value       = e.id_empregado;           // ← ID numérico
    opt.textContent = `${e.matricula} — ${e.nome}`;
    if (editandoId && String(e.id_empregado) === String(valorAtual)) {
      opt.selected = true;
    }
    sel.appendChild(opt);
  });
}

// ── Renderiza tabela ─────────────────────────────────────────
function renderizarTabela(empregados) {
  if (!empregados || !empregados.length) {
    UI.tabelaVazia('tbody-empregados', 8);
    return;
  }

  tabelaBody.innerHTML = '';
  empregados.forEach((emp, i) => {
    const supervisor = emp.supervisor_nome ? `👤 ${emp.supervisor_nome}` : '—';
    const salario    = emp.salario   != null ? UI.formatarMoeda(emp.salario)    : '—';
    const admissao   = emp.data_admissao    ? UI.formatarData(emp.data_admissao) : '—';

    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${i + 1}</td>
      <td><strong>${emp.matricula}</strong></td>
      <td>${emp.nome}</td>
      <td>${emp.cargo || '—'}</td>
      <td>${salario}</td>
      <td>${admissao}</td>
      <td>${supervisor}</td>
      <td class="acoes">
        <button class="btn-icon btn-ver"
                title="Visualizar"
                onclick="verEmpregado(${emp.id_empregado})">👁️</button>
        <button class="btn-icon btn-editar"
                title="Editar"
                onclick="iniciarEdicaoEmpregado(${emp.id_empregado})">✏️</button>
        <button class="btn-icon btn-excluir"
                title="Excluir"
                onclick="excluirEmpregado(${emp.id_empregado},
                  '${emp.nome.replace(/'/g, "\\'")}')">🗑️</button>
      </td>`;
    tabelaBody.appendChild(tr);
  });
}

// ============================================================
// VISUALIZAR
// ============================================================
async function verEmpregado(id) {
  try {
    const e = await API.get(`/empregados/${id}`);

    const campos = [
      ['Matrícula',    e.matricula],
      ['Nome',         e.nome],
      ['CPF',          e.cpf              || '—'],
      ['Cargo',        e.cargo            || '—'],
      ['Salário',      e.salario != null  ? UI.formatarMoeda(e.salario) : '—'],
      ['Admissão',     e.data_admissao    ? UI.formatarData(e.data_admissao) : '—'],
      ['E-mail',       e.email            || '—'],
      ['Telefone',     e.telefone         || '—'],
      ['Supervisor',   e.supervisor_nome  || '— (nenhum) —'],
      ['Qualificações',e.qualificacoes    || '—'],  // ✅ qualificacoes
    ];

    const linhas = campos.map(([k, v]) => `
      <tr>
        <td style="font-weight:600;width:45%;padding:6px 8px;
                   color:#555;">${k}</td>
        <td style="padding:6px 8px;">${v}</td>
      </tr>`).join('');

    abrirModal(
      '👤 Detalhes do Empregado',
      `<table style="width:100%;border-collapse:collapse;font-size:0.95rem;">
         ${linhas}
       </table>`
    );
  } catch (err) {
    UI.mostrarAlerta('alerta-emp', 'Empregado não encontrado.', 'error');
  }
}

// ============================================================
// EDITAR
// ============================================================
async function iniciarEdicaoEmpregado(id) {
  try {
    const e = await API.get(`/empregados/${id}`);

    editandoId = e.id_empregado;
    setVal('empregado-id', e.id_empregado);

    setVal('matricula', e.matricula);
    setVal('nome-emp',  e.nome);
    setVal('cpf-emp',   e.cpf);
    setVal('cargo',     e.cargo);
    setVal('salario',   e.salario);
    setVal('admissao',  e.data_admissao);
    setVal('email-emp', e.email);
    setVal('tel-emp',   e.telefone);
    setVal('qualif',    e.qualificacoes);   // ✅ qualificacoes

    // Recarrega select SEM o próprio empregado e seleciona supervisor atual
    const todos = await API.get('/empregados');
    await preencherSelectSupervisor(todos);
    const sel = document.getElementById('supervisor');
    if (sel && e.id_supervisor) sel.value = String(e.id_supervisor);

    const titulo = document.getElementById('titulo-form-emp');
    if (titulo) titulo.textContent = `✏️ Editando: ${e.nome}`;

    const btnSubmit = formEmpregado.querySelector('[type="submit"]');
    if (btnSubmit) btnSubmit.textContent = '💾 Salvar Alterações';

    formEmpregado.style.border       = '2px solid #e67e22';
    formEmpregado.style.borderRadius = '8px';
    formEmpregado.style.padding      = '12px';

    if (btnCancelar) btnCancelar.style.display = 'inline-block';
    formEmpregado.scrollIntoView({ behavior: 'smooth' });

  } catch (err) {
    UI.mostrarAlerta('alerta-emp',
      'Erro ao carregar empregado: ' + err.message, 'error');
  }
}

// ── Cancelar edição ──────────────────────────────────────────
function cancelarEdicaoEmpregado() {
  editandoId = null;
  formEmpregado.reset();
  setVal('empregado-id', '');

  const titulo = document.getElementById('titulo-form-emp');
  if (titulo) titulo.textContent = '➕ Novo Empregado';

  const btnSubmit = formEmpregado.querySelector('[type="submit"]');
  if (btnSubmit) btnSubmit.textContent = '💾 Salvar Empregado';

  formEmpregado.style.border       = '';
  formEmpregado.style.borderRadius = '';
  formEmpregado.style.padding      = '';

  if (btnCancelar) btnCancelar.style.display = 'none';

  // Recarrega select sem filtro (editandoId já é null)
  carregarEmpregados();
}

// ============================================================
// SALVAR — POST ou PUT
// ============================================================
formEmpregado.addEventListener('submit', async (ev) => {
  ev.preventDefault();

  const supervisorRaw = getVal('supervisor');
  // ✅ "" ou "0" → null | qualquer outro inteiro positivo → int
  const idSupervisor = supervisorRaw && supervisorRaw !== '0'
    ? parseInt(supervisorRaw, 10)
    : null;

  const payload = {
    matricula:     getVal('matricula')  || null,
    nome:          getVal('nome-emp')   || null,
    cpf:           getVal('cpf-emp')    || null,
    cargo:         getVal('cargo')      || null,
    salario:       getValNum('salario'),
    data_admissao: getVal('admissao')   || null,
    email:         getVal('email-emp')  || null,
    telefone:      getVal('tel-emp')    || null,
    qualificacoes: getVal('qualif')     || null,  // ✅ qualificacoes
    id_supervisor: idSupervisor,                  // ✅ null ou int
  };

  // ── RN-10 (client-side) ──────────────────────────────────
  if (editandoId && payload.id_supervisor === editandoId) {
    UI.mostrarAlerta(
      'alerta-emp',
      '⚠️ RN-10: Um empregado não pode ser seu próprio supervisor!',
      'error'
    );
    return;
  }

  try {
    if (editandoId) {
      await API.put(`/empregados/${editandoId}`, payload);
      UI.mostrarAlerta('alerta-emp',
        '✅ Empregado atualizado com sucesso!', 'success');
    } else {
      await API.post('/empregados', payload);
      UI.mostrarAlerta('alerta-emp',
        '✅ Empregado cadastrado com sucesso!', 'success');
    }
    cancelarEdicaoEmpregado();

  } catch (err) {
    UI.mostrarAlerta('alerta-emp', '❌ ' + (err.message || 'Erro desconhecido'), 'error');
  }
});

// ============================================================
// EXCLUIR
// ✅ Sem confirm() — alerta inline com botões Sim/Cancelar
// ============================================================
function excluirEmpregado(id, nome) {
  const alertDiv = document.getElementById('alerta-emp');
  alertDiv.className    = 'alert alert-error';
  alertDiv.style.display = 'block';
  alertDiv.innerHTML = `
    ⚠️ Excluir o empregado <strong>"${nome}"</strong>?
    Esta ação não pode ser desfeita.<br>
    <div style="margin-top:.75rem;display:flex;gap:.5rem;flex-wrap:wrap;">
      <button class="btn btn-primary btn-sm"
              style="background:#ef4444;border-color:#ef4444;"
              onclick="confirmarExclusaoEmpregado(${id}, '${nome.replace(/'/g, "\\'")}')">
        🗑️ Sim, excluir
      </button>
      <button class="btn btn-secondary btn-sm"
              onclick="document.getElementById('alerta-emp').className=
                       'alert alert-hidden'">
        ✖ Cancelar
      </button>
    </div>`;
  alertDiv.scrollIntoView({ behavior: 'smooth' });
}

async function confirmarExclusaoEmpregado(id, nome) {
  try {
    await API.delete(`/empregados/${id}`);
    UI.mostrarAlerta('alerta-emp',
      `✅ Empregado "${nome}" excluído com sucesso.`, 'success');
    await carregarEmpregados();
  } catch (err) {
    UI.mostrarAlerta('alerta-emp',
      '❌ Erro ao excluir: ' + (err.message || 'Erro desconhecido'), 'error');
  }
}

// ============================================================
// HELPERS
// ============================================================
function setVal(id, val) {
  const el = document.getElementById(id);
  if (el) el.value = val ?? '';
}

function getVal(id) {
  return document.getElementById(id)?.value.trim() ?? '';
}

function getValNum(id) {
  const v = document.getElementById(id)?.value;
  return (v !== '' && v != null) ? parseFloat(v) : null;
}

// ============================================================
// EVENTOS & INICIALIZAÇÃO
// ============================================================
if (btnCancelar) {
  btnCancelar.addEventListener('click', cancelarEdicaoEmpregado);
}

document.addEventListener('DOMContentLoaded', () => {
  carregarEmpregados();
});
