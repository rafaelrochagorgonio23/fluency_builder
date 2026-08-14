"""
Fluency Builder — app Streamlit para aprender inglês por repetição de blocos
(chunking), com autenticação via Supabase, geração de conteúdo via Gemini e
áudio de pronúncia via gTTS.
"""
import streamlit as st
from dotenv import load_dotenv

from modules import auth, gemini_service, supabase_service, tts_service

load_dotenv()

st.set_page_config(page_title="Fluency Builder", page_icon="🗣️", layout="centered")

REPETICOES_ALVO = 10


# --------------------------------------------------------------------------- #
# Estado
# --------------------------------------------------------------------------- #
def init_session_state():
    defaults = {
        "user": None,
        "session": None,
        "material": None,      # {"situacao": str, "pt": [p1,p2,p3], "en": [p1,p2,p3]}
        "counters": {},        # {"pt_p1": 0, ..., "en_full": 0}
        "salvo": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_estudo():
    st.session_state.material = None
    st.session_state.counters = {}
    st.session_state.salvo = False


# --------------------------------------------------------------------------- #
# Sidebar
# --------------------------------------------------------------------------- #
def render_sidebar():
    with st.sidebar:
        st.markdown("### 👤 Conta")
        email = getattr(st.session_state.user, "email", "usuário")
        st.write(email)
        if st.button("🔓 Logout", use_container_width=True):
            auth.logout()
            st.session_state.user = None
            st.session_state.session = None
            reset_estudo()
            st.rerun()

        if st.session_state.material:
            st.divider()
            if st.button("🔄 Começar novo estudo", use_container_width=True):
                reset_estudo()
                st.rerun()


# --------------------------------------------------------------------------- #
# Passo 0: entrada da situação
# --------------------------------------------------------------------------- #
def render_input_situacao():
    st.markdown("## 🎯 Qual situação você quer treinar?")
    st.caption(
        "Ex.: entrevista de emprego para analista de suporte, imigração no "
        "aeroporto, pedindo um café, reunião de trabalho, etc."
    )
    situacao = st.text_input(
        "Situação", key="input_situacao", label_visibility="collapsed",
        placeholder="Digite a situação que deseja treinar...",
    )
    if st.button("✨ Gerar Material de Estudo", type="primary", use_container_width=True):
        if not situacao.strip():
            st.warning("Digite uma situação antes de gerar o material.")
        else:
            with st.spinner("Gerando material de estudo com o Gemini..."):
                material, erro = gemini_service.gerar_material_estudo(situacao)
            if erro:
                st.error(f"❌ {erro}")
            else:
                material["situacao"] = situacao.strip()
                st.session_state.material = material
                st.session_state.counters = {}
                st.session_state.salvo = False
                st.rerun()


# --------------------------------------------------------------------------- #
# Bloco reutilizável: texto + (áudio) + contador de repetições
# --------------------------------------------------------------------------- #
def render_bloco(key: str, texto: str, titulo: str, with_audio: bool = False) -> bool:
    st.markdown(f"#### {titulo}")
    st.write(texto)

    if with_audio:
        tts_service.render_audio_button(texto, key=f"audio_{key}")

    count = st.session_state.counters.get(key, 0)
    col_bar, col_btn = st.columns([4, 1])
    with col_bar:
        st.progress(
            min(count / REPETICOES_ALVO, 1.0),
            text=f"Repetições: {count}/{REPETICOES_ALVO}",
        )
    with col_btn:
        if count < REPETICOES_ALVO:
            if st.button("🔁 +1", key=f"btn_{key}", use_container_width=True):
                st.session_state.counters[key] = count + 1
                st.rerun()
        else:
            st.success("✅ OK")

    st.divider()
    return count >= REPETICOES_ALVO


# --------------------------------------------------------------------------- #
# Fluxo de estudo (Passos 1 a 4)
# --------------------------------------------------------------------------- #
def render_fluxo_estudo():
    material = st.session_state.material
    pt = material["pt"]
    en = material["en"]
    pt_full = "\n\n".join(pt)
    en_full = "\n\n".join(en)

    st.markdown(f"## 📘 {material['situacao']}")
    st.caption(
        "Leia em voz alta e clique em '+1' a cada repetição. "
        "Cada etapa libera a próxima ao atingir 10 repetições."
    )
    st.write("")

    etapas = [
        ("pt_p1", pt[0], "Passo 1 · Português (bloco) — Parágrafo 1", False),
        ("pt_p2", pt[1], "Passo 1 · Português (bloco) — Parágrafo 2", False),
        ("pt_p3", pt[2], "Passo 1 · Português (bloco) — Parágrafo 3", False),
        ("pt_full", pt_full, "Passo 2 · Português — Texto completo", False),
        ("en_p1", en[0], "Passo 3 · Inglês (bloco) — Parágrafo 1", True),
        ("en_p2", en[1], "Passo 3 · Inglês (bloco) — Parágrafo 2", True),
        ("en_p3", en[2], "Passo 3 · Inglês (bloco) — Parágrafo 3", True),
        ("en_full", en_full, "Passo 4 · Inglês — Texto completo", True),
    ]

    for key, texto, titulo, with_audio in etapas:
        completo = render_bloco(key, texto, titulo, with_audio)
        if not completo:
            return  # etapas seguintes ficam bloqueadas até esta ser concluída

    # Todas as etapas concluídas
    st.success("🎉 Você concluiu todas as repetições deste estudo!")

    if st.session_state.salvo:
        st.info("Este estudo já foi salvo no seu histórico.")
        return

    if st.button("💾 Concluir e Salvar Estudo", type="primary", use_container_width=True):
        with st.spinner("Salvando no Supabase..."):
            ok, erro = supabase_service.salvar_estudo(
                user_id=st.session_state.user.id,
                situacao=material["situacao"],
                texto_portugues=pt_full,
                texto_ingles=en_full,
            )
        if ok:
            st.session_state.salvo = True
            st.balloons()
            st.success("✅ Estudo salvo com sucesso!")
        else:
            st.error(f"❌ Erro ao salvar no Supabase: {erro}")


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main():
    init_session_state()

    if not st.session_state.user:
        auth.render_auth_screen()
        return

    render_sidebar()

    if not st.session_state.material:
        render_input_situacao()
    else:
        render_fluxo_estudo()


if __name__ == "__main__":
    main()
