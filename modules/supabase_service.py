"""
Módulo de persistência no Supabase.
Salva o histórico de estudos concluídos, sempre vinculado ao user_id logado.
"""
from datetime import datetime, timezone

from modules.auth import get_supabase_client

TABLE_NAME = "historico_estudos"


def salvar_estudo(
    user_id: str,
    situacao: str,
    texto_portugues: str,
    texto_ingles: str,
):
    """Insere um registro de estudo concluído. Retorna (sucesso: bool, erro: str|None)."""
    client = get_supabase_client()
    payload = {
        "user_id": user_id,
        "data_hora": datetime.now(timezone.utc).isoformat(),
        "situacao_estudada": situacao,
        "texto_portugues": texto_portugues,
        "texto_ingles": texto_ingles,
    }
    try:
        client.table(TABLE_NAME).insert(payload).execute()
        return True, None
    except Exception as e:
        return False, str(e)
