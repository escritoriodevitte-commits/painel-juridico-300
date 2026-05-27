"""IA: geração de petição via Claude (Anthropic) quando há chave; senão, template local."""
import logging

from fastapi import APIRouter, Depends

from .. import models, schemas
from ..config import settings
from ..deps import require_roles

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/ia", tags=["ia"])

# Prompt de sistema frozen (sem dados voláteis) — bom para cache de prefixo.
_SYSTEM = (
    "Você é um advogado trabalhista brasileiro experiente. Redija peças jurídicas "
    "formais em português, conforme a CLT e a praxe forense, com endereçamento, "
    "exposição dos fatos, fundamentação jurídica, pedidos e fecho. Use linguagem "
    "técnica e impessoal. Não invente fatos além dos informados."
)


def _template(p: schemas.PeticaoIn) -> str:
    return (
        f"EXCELENTÍSSIMO(A) SENHOR(A) DOUTOR(A) JUIZ(A) DO TRABALHO\n\n"
        f"{p.cliente_nome}, vem, respeitosamente, à presença de Vossa Excelência "
        f"propor a presente {p.tipo.upper()}, pelos fatos e fundamentos a seguir.\n\n"
        f"DOS FATOS\n{p.fatos}\n\n"
        f"DOS PEDIDOS\n{p.pedidos}\n\n"
        f"Nestes termos, pede deferimento."
    )


def _gerar_claude(p: schemas.PeticaoIn) -> str | None:
    """Gera a peça via Claude. Retorna None se não houver chave ou em caso de falha."""
    if not settings.ANTHROPIC_API_KEY:
        return None
    try:
        import anthropic

        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        message = client.messages.create(
            model=settings.CLAUDE_MODEL,
            max_tokens=4096,
            system=[
                {
                    "type": "text",
                    "text": _SYSTEM,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Redija uma peça do tipo \"{p.tipo}\" para o(a) cliente "
                        f"{p.cliente_nome}.\n\nFATOS:\n{p.fatos}\n\nPEDIDOS:\n{p.pedidos}"
                    ),
                }
            ],
        )
        return "".join(b.text for b in message.content if b.type == "text").strip() or None
    except Exception:
        # Falha na IA não derruba o endpoint: cai no template local.
        logger.exception("Falha ao gerar petição via Claude; usando template")
        return None


@router.post("/peticao", response_model=schemas.PeticaoOut)
def gerar_peticao(
    payload: schemas.PeticaoIn,
    _user: models.User = Depends(require_roles("admin", "advogado")),
):
    texto = _gerar_claude(payload)
    if texto:
        return schemas.PeticaoOut(tipo=payload.tipo, fonte="claude", texto=texto)
    return schemas.PeticaoOut(
        tipo=payload.tipo, fonte="template", texto=_template(payload)
    )
