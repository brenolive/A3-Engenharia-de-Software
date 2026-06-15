// ============================================================
// encomendas.js — Madeira Verde
// ✅ Listar | ✅ Criar | ✅ Visualizar | ✅ Excluir
// PADRÃO: API.get/post/delete | UI.mostrarAlerta(id, msg, tipo)
// NUNCA redeclarar const API — já existe em api.js
// ============================================================

const formEncomenda = document.getElementById('form-encomenda');

// ============================================================
// INICIALIZAÇÃO — popula selects de clientes e produtos
// ============================================================
async function inicializarSelects() {
  try {
    const [clientes, produtos] = await Promise.all([
      API.get('/clientes'),
      API.get('/produtos'),
    ]);

    const selCliente = document.getElementById('id_cliente');
    const selFiltro  = document.getElementById('filtro-cliente');

    clientes.forEach(c => {
      const nome = c.nome_fantasia || c.razao_social;
      const opt  = `<option value="${c.id_cliente}">${nome}</option>`;
      if (selCliente) selCliente.insertAdjacentHTML('beforeend', opt);
      if (selFiltro)  selFiltro.insertAdjacentHTML('beforeend', opt);
    });

    window._produtos = produtos;

  } catch (err) {
    // ✅ UI.mostrarAlerta — nunca console.error
    UI.mostrarAlerta('alerta-enc', 'Erro ao carregar selects: ' + err.message, 'error');
  }
}

// ============================================================
// CARREGAR / LISTAR
// ============================================================
async function consultarEncomendas() {
  const clienteId = document.getElementById('filtro-cliente')?.value || '';
  try {
    const data = clienteId
      ? await API.get(`/encomendas/cliente/${clienteId}`)
      : await API.get('/encomendas');
    renderizarTabela(data);
  } catch (err) {
    UI.tabelaVazia('tbody-encomendas', 9);
  }
}

function renderizarTabela(encomendas) {
  if (!encomendas.length) {
    UI.tabelaVazia('tbody-encomendas', 9);
    return;
  }
  const tbody = document.getElementById('tbody-encomendas');
  tbody.innerHTML = '';
  encomendas.forEach((enc, i) => {
    const data     = enc.data_encomenda ? UI.formatarData(enc.data_encomenda) : '—';
    const desconto = enc.desconto_percentual != null ? `${enc.desconto_percentual}%` : '0%';

    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${i + 1}</td>
      <td><strong>${enc.numero_encomenda}</strong></td>
      <td>${enc.cliente_nome || enc.id_cliente}</td>
      <td>${data}</td>
      <td>${UI.badgeStatus(enc.status)}</td>
      <td>${desconto}</td>
      <td>${UI.formatarMoeda(enc.valor_bruto)}</td>
      <td>${UI.formatarMoeda(enc.valor_liquido)}</td>
      <td style="text-align:center;">
        <button class="btn-icon btn-ver"
                title="Ver detalhes"
                onclick="verEncomenda(${enc.id_encomenda})">👁️</button>
        <button class="btn-icon btn-excluir"
                title="Excluir"
                onclick="excluirEncomenda(${enc.id_encomenda}, '${enc.numero_encomenda}')">🗑️</button>
      </td>`;
    tbody.appendChild(tr);
  });
}

// ============================================================
// VISUALIZAR DETALHES
// ============================================================
async function verEncomenda(id) {
  try {
    const enc = await API.get(`/encomendas/${id}`);

    const data        = enc.data_encomenda       ? UI.formatarData(enc.data_encomenda)        : '—';
    const dataEntrega = enc.data_entrega_prevista ? UI.formatarData(enc.data_entrega_prevista) : '—';

    let html = `
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;
                  margin-bottom:16px;font-size:0.9rem;">
        <div><strong>Número:</strong> ${enc.numero_encomenda}</div>
        <div><strong>Status:</strong> ${UI.badgeStatus(enc.status)}</div>
        <div><strong>Cliente:</strong> ${enc.cliente_nome || '—'}</div>
        <div><strong>Data:</strong> ${data}</div>
        <div><strong>Entrega Prevista:</strong> ${dataEntrega}</div>
        <div><strong>Desconto:</strong> ${enc.desconto_percentual ?? 0}%</div>
        <div><strong>Valor Bruto:</strong> ${UI.formatarMoeda(enc.valor_bruto)}</div>
        <div><strong>Valor Líquido:</strong>
          <span style="color:#27ae60;font-weight:700;">
            ${UI.formatarMoeda(enc.valor_liquido)}
          </span>
        </div>
      </div>`;

    if (enc.itens && enc.itens.length) {
      html += `
        <h4 style="margin:8px 0 6px;color:#2c3e50;">📦 Itens da Encomenda</h4>
        <table class="modal-table">
          <thead>
            <tr>
              <th>Produto</th>
              <th style="text-align:center;">Qtd</th>
              <th style="text-align:right;">Preço Unit.</th>
              <th style="text-align:right;">Subtotal</th>
            </tr>
          </thead>
          <tbody>
            ${enc.itens.map(item => `
              <tr>
                <td>${item.produto_nome || item.id_produto}</td>
                <td style="text-align:center;">${item.quantidade}</td>
                <td style="text-align:right;">${UI.formatarMoeda(item.preco_unitario)}</td>
                <td style="text-align:right;">${UI.formatarMoeda(item.subtotal)}</td>
              </tr>`).join('')}
          </tbody>
        </table>`;
    } else {
      html += '<p style="color:#888;font-style:italic;margin-top:8px;">Nenhum item registrado.</p>';
    }

    if (enc.observacoes) {
      html += `<p style="margin-top:12px;"><strong>Observações:</strong> ${enc.observacoes}</p>`;
    }

    abrirModal(`🛒 Encomenda ${enc.numero_encomenda}`, html);

  } catch (err) {
    // ✅ UI.mostrarAlerta — nunca alert()
    UI.mostrarAlerta('alerta-enc', 'Erro ao buscar encomenda: ' + err.message, 'error');
  }
}

// ============================================================
// ADICIONAR LINHA DE ITEM
// ============================================================
function adicionarItem() {
  const container = document.getElementById('itens-container');
  const produtos  = window._produtos || [];

  const div = document.createElement('div');
  div.className = 'item-linha';

  const opts = produtos.map(p =>
    `<option value="${p.id_produto}" data-preco="${p.preco_unitario}">${p.nome}</option>`
  ).join('');

  div.innerHTML = `
    <div class="form-group">
      <label>Produto</label>
      <select class="item-produto" onchange="atualizarPreco(this)">
        <option value="">Selecione...</option>
        ${opts}
      </select>
    </div>
    <div class="form-group">
      <label>Quantidade</label>
      <input type="number" class="item-quantidade" min="1" value="1"
             oninput="recalcular()" />
    </div>
    <div class="form-group">
      <label>Preço Unit. (R$)</label>
      <input type="number" class="item-preco" min="0" step="0.01"
             oninput="recalcular()" />
    </div>
    <div class="form-group" style="align-self:end;">
      <button type="button" class="btn btn-secondary btn-sm"
              onclick="this.closest('.item-linha').remove(); recalcular();">
        ✖
      </button>
    </div>`;

  container.appendChild(div);
}

function atualizarPreco(sel) {
  const opt   = sel.options[sel.selectedIndex];
  const preco = opt?.dataset?.preco || '';
  const linha = sel.closest('.item-linha');
  if (linha) {
    const inputPreco = linha.querySelector('.item-preco');
    if (inputPreco) inputPreco.value = preco;
  }
  recalcular();
}

function recalcular() {
  const desconto = parseFloat(document.getElementById('desconto')?.value || 0);
  let bruto = 0;

  document.querySelectorAll('.item-linha').forEach(linha => {
    const qtd   = parseFloat(linha.querySelector('.item-quantidade')?.value || 0);
    const preco = parseFloat(linha.querySelector('.item-preco')?.value      || 0);
    bruto += qtd * preco;
  });

  const valorDesc = bruto * (desconto / 100);
  const valorLiq  = bruto - valorDesc;

  document.getElementById('valor-bruto').textContent    = UI.formatarMoeda(bruto);
  document.getElementById('valor-desconto').textContent = `- ${UI.formatarMoeda(valorDesc)}`;
  document.getElementById('valor-liquido').textContent  = UI.formatarMoeda(valorLiq);
  document.getElementById('label-desconto').textContent = `Desconto (${desconto}%):`;
}

function limparEncomenda() {
  formEncomenda.reset();
  document.getElementById('itens-container').innerHTML = '';
  recalcular();
}

// ============================================================
// CRIAR ENCOMENDA
// ============================================================
formEncomenda?.addEventListener('submit', async (e) => {
  e.preventDefault();

  const clienteId = document.getElementById('id_cliente')?.value;
  const itens     = coletarItens();

  if (!clienteId) {
    UI.mostrarAlerta('alerta-enc', 'Selecione um cliente.', 'error');
    return;
  }
  if (!itens.length) {
    UI.mostrarAlerta('alerta-enc', 'Adicione pelo menos um produto.', 'error');
    return;
  }

  const payload = {
    id_cliente:            parseInt(clienteId),
    desconto_percentual:   parseFloat(document.getElementById('desconto')?.value || 0),
    data_entrega_prevista: document.getElementById('data_entrega')?.value || null,
    observacoes:           document.getElementById('obs')?.value           || null,
    itens,
  };

  try {
    await API.post('/encomendas', payload);
    UI.mostrarAlerta('alerta-enc', '✅ Encomenda registrada com sucesso!', 'success');
    limparEncomenda();
    await consultarEncomendas();
  } catch (err) {
    UI.mostrarAlerta('alerta-enc', '❌ ' + err.message, 'error');
  }
});

function coletarItens() {
  const itens = [];
  document.querySelectorAll('.item-linha').forEach(linha => {
    const prodId = linha.querySelector('.item-produto')?.value;
    const qtd    = linha.querySelector('.item-quantidade')?.value;
    const preco  = linha.querySelector('.item-preco')?.value;
    if (prodId && qtd && preco) {
      itens.push({
        id_produto:     parseInt(prodId),
        quantidade:     parseInt(qtd),
        preco_unitario: parseFloat(preco),
      });
    }
  });
  return itens;
}

// ============================================================
// EXCLUIR
// ============================================================
async function excluirEncomenda(id, numero) {
  if (!confirm(`Excluir a encomenda "${numero}"?\nTodos os itens serão removidos.`)) return;
  try {
    await API.delete(`/encomendas/${id}`);
    UI.mostrarAlerta('alerta-enc', `✅ Encomenda "${numero}" excluída.`, 'success');
    await consultarEncomendas();
  } catch (err) {
    UI.mostrarAlerta('alerta-enc', '❌ ' + err.message, 'error');
  }
}

// ============================================================
// INIT
// ============================================================
inicializarSelects();
