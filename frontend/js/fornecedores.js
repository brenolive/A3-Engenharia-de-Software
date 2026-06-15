// ============================================================
// fornecedores.js — Madeira Verde
// ✅ Listar | ✅ Criar | ✅ Editar (PUT) | ✅ Excluir | ✅ Visualizar
// ✅ Vínculos Fornecedor × Componente
// PADRÃO: API.get/post/put/delete | UI.mostrarAlerta/tabelaVazia
// NUNCA redeclarar const API — já existe em api.js
// ============================================================

// ── Referências ao DOM ──────────────────────────────────────
const formFornecedor = document.getElementById('form-fornecedor');
const tabelaBody     = document.getElementById('tbody-fornecedores');
const btnCancelar    = document.getElementById('btn-cancelar-edicao');

let editandoId = null;

// ============================================================
// CARREGAR LISTA
// ============================================================
async function carregarFornecedores() {
  try {
    const data = await API.get('/fornecedores');
    renderizarTabela(data);
    preencherSelectFornecedorVinculo(data);
  } catch (err) {
    // ✅ assinatura correta: (elementId, mensagem, tipo)
    // ✅ tipo correto: 'error' (não 'erro')
    UI.mostrarAlerta('alerta-forn', 'Erro ao carregar fornecedores: ' + err.message, 'error');
  }
}

// ── Renderiza tabela principal ───────────────────────────────
function renderizarTabela(fornecedores) {
  if (!fornecedores.length) {
    // ✅ assinatura correta: (tbodyId, colunas) — escreve no DOM direto
    UI.tabelaVazia('tbody-fornecedores', 6);
    return;
  }

  tabelaBody.innerHTML = '';
  fornecedores.forEach((f, i) => {
    const cidade = [f.cidade, f.estado].filter(Boolean).join(' / ') || '—';
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${i + 1}</td>
      <td>${f.cnpj}</td>
      <td><strong>${f.razao_social}</strong></td>
      <td>${f.email || '—'}</td>
      <td>${cidade}</td>
      <td class="acoes">
        <button class="btn-icon btn-ver"
                title="Visualizar"
                onclick="verFornecedor(${f.id_fornecedor})">👁️</button>
        <button class="btn-icon btn-editar"
                title="Editar"
                onclick="iniciarEdicaoFornecedor(${f.id_fornecedor})">✏️</button>
        <button class="btn-icon btn-excluir"
                title="Excluir"
                onclick="excluirFornecedor(${f.id_fornecedor}, '${f.razao_social}')">🗑️</button>
      </td>`;
    tabelaBody.appendChild(tr);
  });
}

// ============================================================
// VISUALIZAR — abrirModal() declarado no HTML
// ============================================================
async function verFornecedor(id) {
  try {
    const f = await API.get(`/fornecedores/${id}`);

    const campos = [
      ['CNPJ',         f.cnpj],
      ['Razão Social', f.razao_social],
      ['Nome Fantasia',f.nome_fantasia  || '—'],
      ['E-mail',       f.email          || '—'],
      ['Telefone',     f.telefone       || '—'],
      ['Cidade',       f.cidade         || '—'],
      ['Estado',       f.estado         || '—'],
    ];

    const linhas = campos.map(([k, v]) => `
      <tr>
        <td style="font-weight:600;width:45%;padding:6px 8px;color:#555;">${k}</td>
        <td style="padding:6px 8px;">${v}</td>
      </tr>`).join('');

    // ✅ abrirModal declarado no HTML — não redeclarar
    abrirModal(
      '🏭 Detalhes do Fornecedor',
      `<table style="width:100%;border-collapse:collapse;font-size:0.95rem;">
         ${linhas}
       </table>`
    );
  } catch (err) {
    UI.mostrarAlerta('alerta-forn', 'Fornecedor não encontrado.', 'error');
  }
}

// ============================================================
// EDITAR
// ============================================================
async function iniciarEdicaoFornecedor(id) {
  try {
    const f = await API.get(`/fornecedores/${id}`);

    editandoId = f.id_fornecedor;

    // ── Campo hidden ─────────────────────────────────────────
    setVal('fornecedor-id', f.id_fornecedor);

    // ── Campos conforme fornecedores.html ────────────────────
    setVal('cnpj-forn',     f.cnpj);
    setVal('razao-forn',    f.razao_social);
    setVal('fantasia-forn', f.nome_fantasia);
    setVal('email-forn',    f.email);
    setVal('tel-forn',      f.telefone);
    setVal('cidade-forn',   f.cidade);
    setVal('estado-forn',   f.estado);

    // ── Título do form ───────────────────────────────────────
    const titulo = document.getElementById('titulo-form-forn');
    if (titulo) titulo.textContent = `✏️ Editando: ${f.razao_social}`;

    // ── Visual do form em modo edição ────────────────────────
    const btnSubmit = document.getElementById('btn-forn');
    if (btnSubmit) btnSubmit.textContent = '💾 Salvar Alterações';

    formFornecedor.style.border       = '2px solid #e67e22';
    formFornecedor.style.borderRadius = '8px';
    formFornecedor.style.padding      = '12px';

    if (btnCancelar) btnCancelar.style.display = 'inline-block';
    formFornecedor.scrollIntoView({ behavior: 'smooth' });

  } catch (err) {
    UI.mostrarAlerta('alerta-forn', 'Erro ao carregar fornecedor: ' + err.message, 'error');
  }
}

// ── Cancelar edição ──────────────────────────────────────────
// ✅ Nome correto conforme onclick do HTML
function cancelarEdicaoFornecedor() {
  editandoId = null;
  formFornecedor.reset();
  setVal('fornecedor-id', '');

  const titulo = document.getElementById('titulo-form-forn');
  if (titulo) titulo.textContent = 'Cadastro de Fornecedor';

  const btnSubmit = document.getElementById('btn-forn');
  if (btnSubmit) btnSubmit.textContent = '💾 Salvar Fornecedor';

  formFornecedor.style.border       = '';
  formFornecedor.style.borderRadius = '';
  formFornecedor.style.padding      = '';

  if (btnCancelar) btnCancelar.style.display = 'none';
}

// ============================================================
// SALVAR — POST ou PUT
// ============================================================
formFornecedor.addEventListener('submit', async (ev) => {
  ev.preventDefault();

  const payload = {
    cnpj:          getVal('cnpj-forn')     || null,
    razao_social:  getVal('razao-forn')    || null,
    nome_fantasia: getVal('fantasia-forn') || null,
    email:         getVal('email-forn')    || null,
    telefone:      getVal('tel-forn')      || null,
    cidade:        getVal('cidade-forn')   || null,
    estado:        getVal('estado-forn')   || null,
  };

  try {
    if (editandoId) {
      await API.put(`/fornecedores/${editandoId}`, payload);
      // ✅ (elementId, mensagem, tipo) — tipo: 'success'
      UI.mostrarAlerta('alerta-forn', '✅ Fornecedor atualizado com sucesso!', 'success');
    } else {
      await API.post('/fornecedores', payload);
      UI.mostrarAlerta('alerta-forn', '✅ Fornecedor cadastrado com sucesso!', 'success');
    }

    cancelarEdicaoFornecedor();
    await carregarFornecedores();

  } catch (err) {
    const msg = err.message || 'Erro desconhecido';
    UI.mostrarAlerta('alerta-forn', '❌ ' + msg, 'error');
  }
});

// ============================================================
// EXCLUIR
// ============================================================
async function excluirFornecedor(id, nome) {
  if (!confirm(`Excluir o fornecedor "${nome}"?\nEsta ação não pode ser desfeita.`)) return;

  try {
    await API.delete(`/fornecedores/${id}`);
    UI.mostrarAlerta('alerta-forn', `✅ Fornecedor "${nome}" excluído.`, 'success');
    await carregarFornecedores();
  } catch (err) {
    UI.mostrarAlerta('alerta-forn', '❌ ' + (err.message || 'Erro desconhecido'), 'error');
  }
}

// ============================================================
// VÍNCULOS — Fornecedor × Componente
// ============================================================

// ── Preenche select de fornecedores na seção de vínculos ────
function preencherSelectFornecedorVinculo(fornecedores) {
  const sel = document.getElementById('sel-forn-vinc');
  if (!sel) return;

  // Preserva opção padrão e rebuilda
  sel.innerHTML = '<option value="">Selecione...</option>';
  fornecedores.forEach(f => {
    const opt = document.createElement('option');
    opt.value       = f.id_fornecedor;
    opt.textContent = `${f.cnpj} — ${f.razao_social}`;
    sel.appendChild(opt);
  });
}

// ── Carrega componentes disponíveis para vincular ────────────
async function carregarComponentesParaVincular() {
  try {
    const componentes = await API.get('/componentes');
    const sel = document.getElementById('sel-comp-forn');
    if (!sel) return;

    sel.innerHTML = '<option value="">Selecione...</option>';
    componentes.forEach(c => {
      const opt = document.createElement('option');
      opt.value       = c.id_componente;
      opt.textContent = `${c.codigo} — ${c.nome}`;
      sel.appendChild(opt);
    });
  } catch (err) {
    UI.mostrarAlerta('alerta-vf', 'Erro ao carregar componentes: ' + err.message, 'error');
  }
}

// ── onchange do select — chamado pelo HTML: onchange="listarCompForn()" ──
async function listarCompForn() {
  const id = getVal('sel-forn-vinc');
  const divLista = document.getElementById('lista-comp-forn');

  if (!id) {
    // ✅ Esconde a div de lista se nenhum fornecedor selecionado
    if (divLista) divLista.style.display = 'none';
    return;
  }

  try {
    const data = await API.get(`/fornecedores/${id}/componentes`);

    // Mostra a div
    if (divLista) divLista.style.display = 'block';

    renderizarTabelaVinculos(data);
  } catch (err) {
    UI.mostrarAlerta('alerta-vf', 'Erro ao carregar vínculos: ' + err.message, 'error');
  }
}

// ── Renderiza tabela de vínculos ─────────────────────────────
function renderizarTabelaVinculos(vinculos) {
  if (!vinculos.length) {
    // ✅ UI.tabelaVazia(tbodyId, colunas)
    UI.tabelaVazia('tbody-comp-forn', 4);
    return;
  }

  const tbody = document.getElementById('tbody-comp-forn');
  if (!tbody) return;
  tbody.innerHTML = '';

  vinculos.forEach(v => {
    const preco = v.preco_unitario != null ? UI.formatarMoeda(v.preco_unitario) : '—';
    const prazo = v.prazo_entrega  != null ? `${v.prazo_entrega} dias` : '—';
    // ✅ preferencial pode vir como boolean do backend
    const pref  = v.preferencial ? '⭐ Sim' : 'Não';

    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${v.nome  || v.codigo || '—'}</td>
      <td>${preco}</td>
      <td>${prazo}</td>
      <td>${pref}</td>`;
    tbody.innerHTML = '';
    tbody.appendChild(tr);
  });
}

// ── Vincular — chamado pelo botão: onclick="vincularCompForn()" ──
async function vincularCompForn() {
  const idForn = getVal('sel-forn-vinc');
  const idComp = getVal('sel-comp-forn');
  const preco  = getValNum('preco-forn');
  const prazo  = getValNum('prazo-forn');

  // ✅ pref-forn é <select> com value "true"/"false" — não .checked
  const prefVal = document.getElementById('pref-forn')?.value;
  const pref    = prefVal === 'true';

  if (!idForn) {
    UI.mostrarAlerta('alerta-vf', '⚠️ Selecione o fornecedor.', 'info');
    return;
  }
  if (!idComp) {
    UI.mostrarAlerta('alerta-vf', '⚠️ Selecione o componente.', 'info');
    return;
  }

  const payload = {
    id_componente:  parseInt(idComp),
    preco_unitario: preco,
    prazo_entrega:  prazo ? parseInt(prazo) : null,
    preferencial:   pref,
  };

  try {
    await API.post(`/fornecedores/${idForn}/componentes`, payload);
    UI.mostrarAlerta('alerta-vf', '✅ Componente vinculado com sucesso!', 'success');

    // Recarrega a lista de vínculos
    await listarCompForn();

    // Limpa campos de vínculo (mantém fornecedor selecionado)
    setVal('sel-comp-forn', '');
    setVal('preco-forn', '');
    setVal('prazo-forn', '');
    setVal('pref-forn', 'false');

  } catch (err) {
    UI.mostrarAlerta('alerta-vf', '❌ ' + (err.message || 'Erro desconhecido'), 'error');
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
// INICIALIZAÇÃO
// ============================================================
(async () => {
  await carregarFornecedores();          // lista + preenche sel-forn-vinc
  await carregarComponentesParaVincular(); // preenche sel-comp-forn
})();
