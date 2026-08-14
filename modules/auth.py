"""
Módulo de autenticação (Supabase Auth).
Responsável por: criar o client Supabase, login, cadastro, logout
e renderizar a tela de autenticação.
"""
import os

import streamlit as st
from supabase import Client, create_client


@st.cache_resource(show_spinner=False)
def get_supabase_client() -> Client:
    """Cria (e cacheia) o client do Supabase a partir das variáveis de ambiente."""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        st.error(
            "⚠️ Variáveis `SUPABASE_URL` e/ou `SUPABASE_KEY` não configuradas. "
            "Verifique seu arquivo `.env`."
        )
        st.stop()
    try:
        return create_client(url, key)
    except Exception as e:
        st.error(f"⚠️ Não foi possível conectar ao Supabase: {e}")
        st.stop()


def sign_up(email: str, password: str):
    """Cadastra um novo usuário. Retorna (result, erro)."""
    client = get_supabase_client()
    try:
        result = client.auth.sign_up({"email": email, "password": password})
        return result, None
    except Exception as e:
        return None, str(e)


def sign_in(email: str, password: str):
    """Autentica um usuário existente. Retorna (result, erro)."""
    client = get_supabase_client()
    try:
        result = client.auth.sign_in_with_password(
            {"email": email, "password": password}
        )
        return result, None
    except Exception as e:
        return None, str(e)


def logout():
    """Encerra a sessão do usuário no Supabase."""
    client = get_supabase_client()
    try:
        client.auth.sign_out()
    except Exception:
        # Mesmo se der erro no sign_out remoto, seguimos limpando a sessão local
        pass


def render_auth_screen():
    """Renderiza a tela de Login / Cadastro. Atualiza st.session_state ao autenticar."""
    st.markdown(
        "<h1 style='text-align:center;'>🗣️ Fluency Builder</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align:center; color: gray;'>"
        "Aprenda inglês por repetição de blocos (chunking)</p>",
        unsafe_allow_html=True,
    )
    st.write("")

    tab_login, tab_signup = st.tabs(["🔑 Entrar", "🆕 Criar conta"])

    with tab_login:
        with st.form("login_form", clear_on_submit=False):
            email = st.text_input("E-mail", key="login_email")
            password = st.text_input("Senha", type="password", key="login_password")
            submitted = st.form_submit_button("Entrar", use_container_width=True)

            if submitted:
                if not email or not password:
                    st.warning("Preencha e-mail e senha.")
                else:
                    with st.spinner("Autenticando..."):
                        result, error = sign_in(email, password)
                    if error:
                        st.error(f"❌ Erro ao entrar: {error}")
                    elif result and result.user:
                        st.session_state.user = result.user
                        st.session_state.session = result.session
                        st.rerun()
                    else:
                        st.error("❌ Não foi possível autenticar. Tente novamente.")

    with tab_signup:
        with st.form("signup_form", clear_on_submit=False):
            email = st.text_input("E-mail", key="signup_email")
            password = st.text_input(
                "Senha (mín. 6 caracteres)", type="password", key="signup_password"
            )
            password2 = st.text_input(
                "Confirme a senha", type="password", key="signup_password2"
            )
            submitted = st.form_submit_button("Cadastrar", use_container_width=True)

            if submitted:
                if not email or not password:
                    st.warning("Preencha e-mail e senha.")
                elif password != password2:
                    st.warning("As senhas não coincidem.")
                elif len(password) < 6:
                    st.warning("A senha deve ter ao menos 6 caracteres.")
                else:
                    with st.spinner("Criando conta..."):
                        result, error = sign_up(email, password)
                    if error:
                        st.error(f"❌ Erro ao cadastrar: {error}")
                    else:
                        st.success(
                            "✅ Conta criada! Se a confirmação por e-mail estiver "
                            "habilitada no seu projeto Supabase, verifique sua caixa "
                            "de entrada antes de fazer login."
                        )
