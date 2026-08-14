# 🗣️ Fluency Builder

Aplicativo Streamlit para aprender inglês por **repetição de blocos (chunking)**,
focado em situações específicas (entrevista de emprego, imigração, etc).

O app gera material de estudo com o **Google Gemini**, guia você por um fluxo
de repetição em Português e Inglês (com áudio via **gTTS**), autentica usuários
com **Supabase Auth** e salva o histórico de estudos no **Supabase**.

## 📁 Estrutura do projeto

```
fluency_builder/
├── app.py                     # App principal (login + fluxo de estudo)
├── modules/
│   ├── auth.py                 # Login, cadastro, logout (Supabase Auth)
│   ├── gemini_service.py       # Geração de material de estudo via Gemini
│   ├── tts_service.py          # Geração de áudio de pronúncia via gTTS
│   └── supabase_service.py     # Persistência do histórico de estudos
├── schema.sql                  # Script SQL para rodar no Supabase
├── requirements.txt            # Dependências Python
├── .env.example                # Modelo de variáveis de ambiente
└── README.md
```

## 1. Pré-requisitos

- Python 3.10+
- Uma conta no [Supabase](https://supabase.com) (gratuita)
- Uma chave de API do [Google Gemini](https://aistudio.google.com/app/apikey)

## 2. Configurar o Supabase

1. Crie um novo projeto no Supabase.
2. Vá em **SQL Editor** e execute o conteúdo do arquivo `schema.sql` deste
   projeto. Isso cria a tabela `historico_estudos`, a chave estrangeira para
   `auth.users` e habilita o **Row Level Security (RLS)**, garantindo que cada
   usuário só veja e altere os próprios dados.
3. Em **Project Settings → API**, copie:
   - `Project URL` → variável `SUPABASE_URL`
   - `anon public key` → variável `SUPABASE_KEY`
4. (Opcional) Em **Authentication → Providers**, você pode desabilitar a
   confirmação por e-mail durante os testes, para logar imediatamente após o
   cadastro.

## 3. Configurar as variáveis de ambiente

Copie o arquivo de exemplo e preencha com suas chaves:

```bash
cp .env.example .env
```

Edite o `.env`:

```env
SUPABASE_URL=https://SEU-PROJETO.supabase.co
SUPABASE_KEY=SUA_ANON_KEY_AQUI

GEMINI_API_KEY=SUA_GEMINI_API_KEY_AQUI
GEMINI_MODEL=gemini-2.0-flash
```

> ⚠️ Nunca commite o arquivo `.env` com chaves reais em um repositório público.

## 4. Instalar dependências

Recomendado usar um ambiente virtual:

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 5. Rodar o app

```bash
streamlit run app.py
```

O app abrirá em `http://localhost:8501`.

## 6. Como usar

1. **Cadastre-se ou faça login** na tela inicial.
2. Digite a **situação** que deseja treinar (ex.: "Entrevista de emprego para
   analista de suporte técnico") e clique em **Gerar Material de Estudo**.
3. Siga o fluxo guiado:
   - **Passo 1**: leia em voz alta cada parágrafo em Português, clicando em
     "+1" a cada repetição, até completar 10 — isso libera o próximo parágrafo.
   - **Passo 2**: repita o texto completo em Português 10 vezes.
   - **Passo 3**: repita cada parágrafo em Inglês 10 vezes (com botão de
     áudio 🔊 para ouvir a pronúncia).
   - **Passo 4**: repita o texto completo em Inglês 10 vezes (com áudio).
4. Ao concluir o Passo 4, clique em **Concluir e Salvar Estudo** para gravar
   a sessão no Supabase, vinculada ao seu usuário.
5. Use **🔄 Começar novo estudo** na barra lateral para treinar outra
   situação, ou **🔓 Logout** para sair.

## Tratamento de erros

- Credenciais do Supabase ou do Gemini ausentes/inválidas exibem um aviso
  claro na tela, sem quebrar o app.
- Falhas na API do Gemini (resposta fora do formato esperado, erro de rede,
  etc.) são capturadas e mostradas ao usuário, permitindo tentar novamente.
- Falhas ao gerar áudio (gTTS) ou ao salvar no Supabase também são exibidas
  como mensagens de erro, sem interromper o restante do fluxo.

## Notas técnicas

- O nome do modelo Gemini é configurável via `GEMINI_MODEL` no `.env`, caso
  você precise trocar de versão no futuro.
- O app usa `st.session_state` para manter login, material gerado e
  contadores de repetição entre re-renderizações, evitando perda de
  progresso ao interagir com a tela.
