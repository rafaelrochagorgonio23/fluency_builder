"""
Módulo de integração com a API do Google Gemini.
Gera o material de estudo (PT + EN) dividido em 3 parágrafos correspondentes.
"""
import json
import os
import re

from google import genai
import streamlit as st

PROMPT_TEMPLATE = """
Você é um assistente especialista em ensino de inglês. Gere material de estudo
para a seguinte situação: "{situacao}"

Regras estritas:
1. Escreva um texto em Português, dividido em EXATAMENTE 3 parágrafos, útil e
   realista para praticar essa situação (vocabulário e frases relevantes).
2. Traduza esse texto para o Inglês de forma natural e idiomática, também
   dividido em EXATAMENTE 3 parágrafos, na mesma ordem/correspondência dos
   parágrafos em português (parágrafo 1 traduz parágrafo 1, e assim por diante).
3. Responda ESTRITAMENTE em formato JSON válido, sem nenhum texto adicional,
   comentário ou marcação markdown (sem ```), seguindo exatamente este schema:

{{
  "pt_paragrafo_1": "...",
  "pt_paragrafo_2": "...",
  "pt_paragrafo_3": "...",
  "en_paragrafo_1": "...",
  "en_paragrafo_2": "...",
  "en_paragrafo_3": "..."
}}
"""


def _get_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        st.error(
            "⚠️ Variável `GEMINI_API_KEY` não configurada. Verifique seu arquivo `.env` "
            "ou a área de Secrets do Streamlit."
        )
        st.stop()
    
    # O novo SDK inicializa o Cliente passando a chave
    return genai.Client(api_key=api_key)


def _extract_json(raw_text: str) -> str:
    """Remove eventuais cercas de código (```json ... ```) da resposta do modelo."""
    text = raw_text.strip()
    text = re.sub(r"^```(json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def gerar_material_estudo(situacao: str):
    """
    Chama o Gemini e retorna uma tupla (material, erro).
    material = {"pt": [p1, p2, p3], "en": [p1, p2, p3]}
    """
    if not situacao or not situacao.strip():
        return None, "Descreva a situação que deseja treinar antes de gerar o material."

    try:
        client = _get_client()
        # Atualizado para o modelo ativo mais recente
        model_name = os.environ.get("GEMINI_MODEL", "gemini-3.6-flash")
        
        # Nova estrutura de chamada através da API Interactions
        interaction = client.interactions.create(
            model=model_name,
            input=PROMPT_TEMPLATE.format(situacao=situacao.strip())
        )
        
        # A extração do texto agora usa 'output_text'
        raw_text = getattr(interaction, "output_text", None)
        if not raw_text:
            return None, "O Gemini não retornou nenhum conteúdo. Tente novamente."

        clean_text = _extract_json(raw_text)
        data = json.loads(clean_text)

        pt = [
            data["pt_paragrafo_1"].strip(),
            data["pt_paragrafo_2"].strip(),
            data["pt_paragrafo_3"].strip(),
        ]
        en = [
            data["en_paragrafo_1"].strip(),
            data["en_paragrafo_2"].strip(),
            data["en_paragrafo_3"].strip(),
        ]
        return {"pt": pt, "en": en}, None

    except json.JSONDecodeError:
        return None, (
            "A resposta da IA não veio em formato JSON válido. "
            "Tente gerar o material novamente."
        )
    except KeyError:
        return None, (
            "A resposta da IA não contém todos os campos esperados. "
            "Tente gerar o material novamente."
        )
    except Exception as e:
        return None, f"Erro ao chamar a API do Gemini: {e}"
