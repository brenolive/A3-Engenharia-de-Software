// ============================================================
// produtos.js — Madeira Verde
// ✅ Listar | ✅ Criar | ✅ Editar (PUT) | ✅ Excluir | ✅ Visualizar
// ✅ Vincular Componente | ✅ Listar Componentes do Produto
// PADRÃO: API.get/post/put/delete | UI.mostrarAlerta(id, msg, tipo)
// NUNCA redeclarar const API — já existe em api.js
// NUNCA usar alert(), confirm(), console.error(), fetch() direto
// ============================================================

const formProduto = document.getElementById('form-produto');
const btnCancelar = document.getElementById('btn-cancelar-edicao');

let editandoId = null;

// ============================================================
// CARREGAR / LISTAR PRODUTOS
// ============================================================
async function carregarProdutos() {
  try {
    const data = await API.get('/produtos');
    renderizarTabela(data);
  } catch (err) {
    UI.tabelaVazia('tbody-produtos', 7);
  }
}

function renderizarTabela(produtos) {
  if (!produtos || !produtos.length) {
    UI.tabelaVazia('tbody-produtos', 7);
    return;
  }
  const tbody = document.getElementById('tbody-produtos');
  tbody.innerHTML = '';
  produtos.forEach((p, i) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${i + 1}</td>
      <td><strong>${p.codigo}</strong></td>
      <td>${p.nome}</td>
      <td>${p.categoria || '—'}</td>
      <td>${UI.formatarMoeda(p.preco_unitario)}</td>
      <td><span class="badge ${p.ativo !== false ? 'badge-ativo' : 'badge-inativo'}">
            ${p.ativo !== false ? 'Ativo' : 'Inativo'}
          </span></td>
      <td style="text-align:center;">
        <button class="btn-icon btn-ver"
                title="Visualizar"
                onclick="verProduto(${p.id_produto})">👁️</button>
        <button class="btn-icon btn-editar"
                title="Editar"
                onclick="iniciarEdicaoProduto(${p.id_produto})">✏️</button>
        <button class="btn-icon btn-excluir"
                title="Excluir"
                onclick="excluirProduto(${p.id_produto}, '${p.nome}')">🗑️</button>
      </td>`;
    tbody.appendChild(tr);
  });
}

// ============================================================
// POPULAR SELECTS — Produtos e Componentes
// ============================================================

/**
 * Popula #sel-produto-vinc com todos os produtos ativos.
 * Ao mudar a seleção, carrega os componentes já vinculados.
 */
async function carregarSelectProdutos() {
  const sel = document.getElementById('sel-produto-vinc');
  if (!sel) return;

  try {
    const produtos = await API.get('/produtos');

    // Limpa opções anteriores mantendo o placeholder
    sel.innerHTML = '<option value="">Selecione o produto...</option>';

    produtos.forEach(p => {
      const opt = document.createElement('option');
      opt.value       = p.id_produto;          // ← value = ID numérico
      opt.textContent = `${p.codigo} — ${p.nome}`;
      sel.appendChild(opt);
    });

  } catch (err) {
    UI.mostrarAlerta('alerta-vinc',
      '❌ Erro ao carregar produtos: ' + err.message, 'error');
  }
}

/**
 * Popula #sel-comp-vinc com todos os componentes cadastrados.
 */
async function carregarSelectComponentes() {
  const sel = document.getElementById('sel-comp-vinc');
  if (!sel) return;

  try {
    const componentes = await API.get('/componentes');

    // Limpa opções anteriores mantendo o placeholder
    sel.innerHTML = '<option value="">Selecione o componente...</option>';

    componentes.forEach(c => {
      const opt = document.createElement('option');
      opt.value       = c.id_componente;       // ← value = ID numérico
      opt.textContent = `${c.codigo || c.nome} — ${c.nome}`;
      sel.appendChild(opt);
    });

  } catch (err) {
    UI.mostrarAlerta('alerta-vinc',
      '❌ Erro ao carregar componentes: ' + err.message, 'error');
  }
}

// ============================================================
// CARREGAR COMPONENTES DO PRODUTO SELECIONADO
// ============================================================
async function carregarComponentesDoProduto(idProduto) {
  const area  = document.getElementById('area-componentes');
  const tbody = document.getElementById('tbody-comp-prod');

  if (!idProduto) {
    area.style.display = 'none';
    return;
  }

  try {
    const data = await API.get(`/produtos/${idProduto}/componentes`);
    area.style.display = 'block';

    if (!data || !data.length) {
      UI.tabelaVazia('tbody-comp-prod', 5);
      return;
    }

    tbody.innerHTML = '';
    data.forEach(item => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${item.nome_componente || item.componente?.nome || '—'}</td>
        <td>${item.tipo           || item.componente?.tipo || '—'}</td>
        <td>${item.quantidade_necessaria ?? '—'}</td>
        <td>${item.unidade_medida ?? '—'}</td>
        <td>${item.tempo_uso_horas != null ? item.tempo_uso_horas : '—'}</td>`;
      tbody.appendChild(tr);
    });

  } catch (err) {
    area.style.display = 'block';
    UI.tabelaVazia('tbody-comp-prod', 5);
    UI.mostrarAlerta('alerta-vinc',
      '❌ Erro ao carregar componentes do produto: ' + err.message, 'error');
  }
}

// ============================================================
// VINCULAR COMPONENTE AO PRODUTO
// ============================================================
async function vincularComponente() {
  const idProduto    = document.getElementById('sel-produto-vinc').value;
  const idComponente = document.getElementById('sel-comp-vinc').value;
  const quantidade   = document.getElementById('qtd-vinc').value;
  const unidade      = document.getElementById('unidade-vinc').value;
  const tempo        = document.getElementById('tempo-vinc').value;

  // Validações client-side
  if (!idProduto) {
    UI.mostrarAlerta('alerta-vinc', '⚠️ Selecione um produto.', 'error');
    return;
  }
  if (!idComponente) {
    UI.mostrarAlerta('alerta-vinc', '⚠️ Selecione um componente.', 'error');
    return;
  }
  if (!quantidade || parseFloat(quantidade) <= 0) {
    UI.mostrarAlerta('alerta-vinc',
      '⚠️ Informe uma quantidade válida (maior que zero).', 'error');
    return;
  }

  const payload = {
    id_componente:        parseInt(idComponente, 10),
    quantidade_necessaria: parseFloat(quantidade),
    unidade_medida:       unidade || null,
    tempo_uso_horas:      tempo !== '' ? parseFloat(tempo) : null,
  };

  try {
    await API.post(`/produtos/${idProduto}/componentes`, payload);
    UI.mostrarAlerta('alerta-vinc',
      '✅ Componente vinculado com sucesso!', 'success');

    // Limpa campos do vínculo (mantém produto selecionado para facilitar
    // adição de múltiplos componentes ao mesmo produto)
    document.getElementById('sel-comp-vinc').value = '';
    document.getElementById('qtd-vinc').value      = '';
    document.getElementById('tempo-vinc').value    = '';
    document.getElementById('unidade-vinc').selectedIndex = 0;

    // Recarrega a lista de componentes do produto selecionado
    await carregarComponentesDoProduto(idProduto);

  } catch (err) {
    UI.mostrarAlerta('alerta-vinc', '❌ ' + err.message, 'error');
  }
}

// ============================================================
// VISUALIZAR PRODUTO
// ============================================================
async function verProduto(id) {
  try {
    const p = await API.get(`/produtos/${id}`);

    const campos = [
      ['Código',    p.codigo],
      ['Nome',      p.nome],
      ['Categoria', p.categoria || '—'],
      ['Descrição', p.descricao || '—'],
      ['Preço',     UI.formatarMoeda(p.preco_unitario)],
      ['Status',    p.ativo !== false ? '✅ Ativo' : '❌ Inativo'],
    ];

    const linhas = campos.map(([k, v]) => `
      <tr>
        <td style="font-weight:600;width:45%;padding:6px 8px;
                   color:#555;">${k}</td>
        <td style="padding:6px 8px;">${v}</td>
      </tr>`).join('');

    abrirModal(
      '🪑 Detalhes do Produto',
      `<table style="width:100%;border-collapse:collapse;font-size:0.95rem;">
         ${linhas}
       </table>`
    );
  } catch (err) {
    UI.mostrarAlerta('alerta-prod',
      '❌ Erro ao buscar produto: ' + err.message, 'error');
  }
}

// ============================================================
// INICIAR EDIÇÃO
// ============================================================
async function iniciarEdicaoProduto(id) {
  try {
    const p = await API.get(`/produtos/${id}`);
    editandoId = id;

    setVal('codigo',    p.codigo);
    setVal('nome',      p.nome);
    setVal('preco',     p.preco_unitario);
    setVal('categoria', p.categoria);
    setVal('ativo',     p.ativo !== false ? 'true' : 'false');
    setVal('descricao', p.descricao);

    document.getElementById('titulo-form-produto')
            .textContent = '✏️ Editar Produto';
    if (btnCancelar) btnCancelar.style.display = 'inline-block';
    formProduto.scrollIntoView({ behavior: 'smooth' });

  } catch (err) {
    UI.mostrarAlerta('alerta-prod',
      '❌ Erro ao buscar produto: ' + err.message, 'error');
  }
}

function cancelarEdicaoProduto() {
  editandoId = null;
  formProduto.reset();
  document.getElementById('titulo-form-produto')
          .textContent = 'Cadastro de Produto';
  if (btnCancelar) btnCancelar.style.display = 'none';
}

// ============================================================
// SALVAR PRODUTO (POST ou PUT)
// ============================================================
formProduto.addEventListener('submit', async (e) => {
  e.preventDefault();

  const payload = {
    codigo:         getVal('codigo'),
    nome:           getVal('nome'),
    preco_unitario: getValNum('preco'),
    categoria:      getVal('categoria') || null,
    descricao:      getVal('descricao') || null,
    ativo:          document.getElementById('ativo').value === 'true',
  };

  try {
    if (editandoId) {
      await API.put(`/produtos/${editandoId}`, payload);
      UI.mostrarAlerta('alerta-prod',
        '✅ Produto atualizado com sucesso!', 'success');
    } else {
      await API.post('/produtos', payload);
      UI.mostrarAlerta('alerta-prod',
        '✅ Produto cadastrado com sucesso!', 'success');
    }
    cancelarEdicaoProduto();
    await carregarProdutos();
    // Recarrega o select de produtos do vínculo para incluir o novo/editado
    await carregarSelectProdutos();

  } catch (err) {
    UI.mostrarAlerta('alerta-prod', '❌ ' + err.message, 'error');
  }
});

// ============================================================
// EXCLUIR PRODUTO
// ✅ Sem confirm() — usa UI.mostrarAlerta com botão de confirmação
// ============================================================
function excluirProduto(id, nome) {
  // Exibe alerta de confirmação inline em vez de confirm()
  const alertDiv = document.getElementById('alerta-prod');
  alertDiv.className   = 'alert alert-error';
  alertDiv.style.display = 'block';
  alertDiv.innerHTML = `
    ⚠️ Excluir o produto <strong>"${nome}"</strong>? Esta ação não pode ser desfeita.<br>
    <div style="margin-top:.75rem; display:flex; gap:.5rem; flex-wrap:wrap;">
      <button class="btn btn-primary btn-sm"
              style="background:#ef4444; border-color:#ef4444;"
              onclick="confirmarExclusaoProduto(${id}, '${nome}')">
        🗑️ Sim, excluir
      </button>
      <button class="btn btn-secondary btn-sm"
              onclick="document.getElementById('alerta-prod').className=
                       'alert alert-hidden'">
        ✖ Cancelar
      </button>
    </div>`;
  alertDiv.scrollIntoView({ behavior: 'smooth' });
}

async function confirmarExclusaoProduto(id, nome) {
  try {
    await API.delete(`/produtos/${id}`);
    UI.mostrarAlerta('alerta-prod',
      `✅ Produto "${nome}" excluído com sucesso.`, 'success');
    await carregarProdutos();
    await carregarSelectProdutos(); // Atualiza select do vínculo
  } catch (err) {
    UI.mostrarAlerta('alerta-prod', '❌ ' + err.message, 'error');
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
  return document.getElementById(id)?.value.trim() || '';
}
function getValNum(id) {
  const v = document.getElementById(id)?.value;
  return v !== '' && v != null ? parseFloat(v) : null;
}

// ============================================================
// EVENTOS & INICIALIZAÇÃO
// ============================================================
if (btnCancelar) {
  btnCancelar.addEventListener('click', cancelarEdicaoProduto);
}

// Ao mudar o produto selecionado no vínculo → carrega componentes vinculados
document.getElementById('sel-produto-vinc')
  .addEventListener('change', (e) => {
    carregarComponentesDoProduto(e.target.value);
  });

// ──────────────────────────────────────────────────────────────
// DOMContentLoaded — ponto único de inicialização
// ──────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', async () => {
  await carregarProdutos();           // tabela principal
  await carregarSelectProdutos();     // #sel-produto-vinc
  await carregarSelectComponentes();  // #sel-comp-vinc
});
