"""IA: geração de petição via OpenAI quando há chave; senão, template local."""
from fastapi import APIRouter, Depends

from .. import models, schemas
from ..config import settings
from ..deps import require_roles

router = APIRouter(prefix="/api/v1/ia", tags=["ia"])


def _template(p: schemas.PeticaoIn) -> str:
    return (
        f"EXCELENTÍSSIMO(A) SENHOR(A) DOUTOR(A) JUIZ(A) DO TRABALHO\n\n"
        f"{p.cliente_nome}, vem, respeitosamente, à presença de Vossa Excelência "
        f"propor a presente {p.tipo.upper()}, pelos fatos e fundamentos a seguir.\n\n"
        f"DOS FATOS\n{p.fatos}\n\n"
        f"DOS PEDIDOS\n{p.pedidos}\n\n"
        f"Nestes termos, pede deferimento."
    )


def _gerar_openai(p: schemas.PeticaoIn) -> str | None:
    if not settings.OPENAI_API_KEY:
        return None
    try:
        from openai import OpenAI

        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        resp = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "Você é advogado trabalhista. Redija peças jurídicas em português.",
                },
                {
                    "role": "user",
                    "content": (
                        f"Tipo de peça: {p.tipo}\nCliente: {p.cliente_nome}\n"
                        f"Fatos: {p.fatos}\nPedidos: {p.pedidos}"
                    ),
                },
            ],
        )
        return resp.choices[0].message.content
    except Exception:
        # Falha na IA externa não derruba o endpoint: cai no template.
        return None


@router.post("/peticao", response_model=schemas.PeticaoOut)
def gerar_peticao(
    payload: schemas.PeticaoIn,
    _user: models.User = Depends(require_roles("admin", "advogado")),
):
    texto = _gerar_openai(payload)
    if texto is not None:
        return schemas.PeticaoOut(tipo=payload.tipo, fonte="openai", texto=texto)
    return schemas.PeticaoOut(
        tipo=payload.tipo, fonte="template", texto=_template(payload)
    )
