"""
Ponto de Entrada — Sistema Madeira Verde.
FastAPI com CORS e inicialização automática do banco.
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from backend.database import init_db
from backend.routers import (
    clientes,
    componentes,
    dashboard,
    empregados,
    encomendas,
    fornecedores,
    manutencoes,
    produtos,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializa o banco na subida e libera recursos na descida."""
    init_db()
    print("✅ Banco de dados inicializado — Madeira Verde online")
    yield
    print("🔒 Sistema Madeira Verde encerrado")


app = FastAPI(
    title="Sistema Madeira Verde",
    description="API de Gestão da Fábrica de Móveis Madeira Verde",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(clientes.router)
app.include_router(produtos.router)
app.include_router(componentes.router)
app.include_router(empregados.router)
app.include_router(fornecedores.router)
app.include_router(encomendas.router)
app.include_router(manutencoes.router)
app.include_router(dashboard.router)


# ── Rotas simples ────────────────────────────────────────────
@app.get("/", tags=["Root"])
def raiz():
    return RedirectResponse(url="/static/index.html")


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}


# ── StaticFiles — servir o frontend ─────────────────────────
# ⚠️ DEVE ficar DEPOIS dos routers e rotas @app.get
FRONTEND = Path(__file__).parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=FRONTEND), name="static")
