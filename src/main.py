import streamlit as st
import boto3
import uuid
import os
import re
import random
import time
import json
import base64

def carregar_config():
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"bloquear_upload": False}  # default se não existir
    return json.loads(f.read())

def salvar_config(config):
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f)

# CONFIG
BUCKET_NAME = '123687089814-casamento-m-a-2026'
REGION = 'sa-east-1'
CONFIG_PATH = "src/eventos/config.json"

s3 = boto3.client('s3', region_name=REGION)

st.set_page_config(page_title="Cloud Photos", layout="wide")
if "upload_key" not in st.session_state:
    st.session_state.upload_key = 0

if "reset_form" not in st.session_state:
    st.session_state.reset_form = False

# 🎨 CSS CUSTOM
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .title {
        text-align: center;
        font-size: 40px;
        font-weight: bold;
        color: white;
        margin-bottom: 10px;
    }
    .subtitle {
        text-align: center;
        color: #9ca3af;
        margin-bottom: 30px;
    }
    .card {
        background-color: #1c1f26;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 45px;
        font-weight: bold;
        background-color: #4f46e5;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

def get_base64_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

img_base64 = get_base64_image("src/images/image.png")

st.markdown(f"""
<div style="
    width: 100%;
    height: 400px;
    display: flex;
    align-items: center;
    justify-content: center;
">
    <img src="data:image/png;base64,{img_base64}" style="
        max-height: 100%;
        width: auto;
        object-fit: contain;
    ">
</div>
""", unsafe_allow_html=True)

# HEADER
# st.markdown('<div class="title">📸</div>', unsafe_allow_html=True)
# st.markdown('<div class="subtitle">FotoCloud</div>', unsafe_allow_html=True)
# st.markdown('<div class="title" style="color:#000000;">Casamento</div>', unsafe_allow_html=True)
# st.markdown('<div class="title" style="color:#000000;">Amanda e Matheus</div>', unsafe_allow_html=True)
# st.markdown('<div class="subtitle">16/05/2026</div>', unsafe_allow_html=True)

# --------- FUNÇÕES ---------

def limpar_nome(nome):
    nome = nome.strip().replace(" ", "_")
    nome = re.sub(r'[^a-zA-Z0-9_]', '', nome)
    return nome.lower()

def gerar_url_temporaria(key):
    return s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': BUCKET_NAME, 'Key': key},
        ExpiresIn=3600
    )

# --------- MENU ---------

aba = st.tabs(["📤 Upload", "🖼️ Galeria", "⚙️ Configuração"])

# ========================
# 📤 UPLOAD
# ========================
with aba[0]:

    # -------- ESTADOS --------
    if "sucesso_upload" not in st.session_state:
        st.session_state.sucesso_upload = False

    if "upload_key" not in st.session_state:
        st.session_state.upload_key = 0

    if "reset_form" not in st.session_state:
        st.session_state.reset_form = False

    # -------- RESET SE NECESSÁRIO --------
    if st.session_state.reset_form:
        st.session_state["nome_input"] = ""
        st.session_state["momento_input"] = ""
        st.session_state.reset_form = False

    # -------- UI --------
    
    if st.session_state.sucesso_upload:
        st.success("Upload concluído com sucesso! 🚀")



    # -------- ENVIO --------
    bloquear_upload = carregar_config()
    bloquear_upload = bloquear_upload.get("bloquear_upload")
    if bloquear_upload:
        st.warning("🚫 Envio de fotos está bloqueado pelo administrador")
    else:
        nome_pessoa = st.text_input("Seu nome", key="nome_input")
        momento = st.text_input("Momento", key="momento_input")

        uploaded_files = st.file_uploader(
            "Selecione suas fotos",
            type=["png", "jpg", "jpeg", "mp4", "HEVC", "H.265", "mov"],
            accept_multiple_files=True,
            key=f"upload_input_{st.session_state.upload_key}"  # 🔥 chave dinâmica
        )
        if st.button("🚀 Enviar imagens"):

            if not nome_pessoa or not momento:
                st.warning("Digite seu nome e momento")
            elif not uploaded_files:
                st.warning("Selecione imagens")
            else:
                nome_limpo = limpar_nome(nome_pessoa)
                momento_limpo = limpar_nome(momento)

                progress_bar = st.progress(0)
                status_text = st.empty()

                total = len(uploaded_files)

                with st.spinner("Enviando para a nuvem..."):

                    for i, file in enumerate(uploaded_files):

                        ext = os.path.splitext(file.name)[1]
                        file_name = f"{nome_limpo}_{momento_limpo}_{uuid.uuid4()}{ext}"

                        sucesso = False
                        tentativas = 0

                        while not sucesso and tentativas < 3:
                            try:
                                s3.upload_fileobj(
                                    file,
                                    BUCKET_NAME,
                                    file_name,
                                    ExtraArgs={"ContentType": file.type}
                                )
                                sucesso = True
                            except:
                                tentativas += 1
                                time.sleep(1)

                        if sucesso:
                            status_text.text(f"✔ {file.name}")
                        else:
                            st.error(f"Erro ao enviar {file.name}")

                        progress_bar.progress((i + 1) / total)

                # -------- RESET CORRETO --------
                st.session_state.sucesso_upload = True
                st.session_state.reset_form = True
                st.session_state.upload_key += 1  # 🔥 recria uploader

                st.rerun()

# ========================
# 🖼️ GALERIA
# ========================
with aba[1]:
    bloquear_galeria = carregar_config()
    bloquear_galeria = bloquear_galeria.get("bloquear_galeria")
    if bloquear_galeria:
        st.warning("🚫 Acesso à galeria está bloqueado pelo administrador")
    else:
        st.subheader("Galeria")

        filtro_nome = st.text_input("Filtrar por nome ou momento")

        qtd_fotos = st.selectbox(
            "Quantidade de Fotos",
            [5, 10, 15],
            index=0  # default = 5
        )

        try:
            response = s3.list_objects_v2(Bucket=BUCKET_NAME)
        except Exception as e:
            st.error(f"Erro ao acessar bucket: {e}")
            st.stop()

        if "Contents" not in response:
            st.info("Nenhuma imagem encontrada")
        else:
            arquivos = response["Contents"]

            if filtro_nome:
                filtro_nome = limpar_nome(filtro_nome)
                arquivos = [obj for obj in arquivos if obj["Key"]]

            if len(arquivos) == 0:
                st.warning("Nenhuma imagem encontrada")
            else:
                arquivos_aleatorios = random.sample(
                    arquivos,
                    min(int(qtd_fotos), len(arquivos))
                )

            # 🎨 GRID STYLE (lado a lado + vertical)
            cols = st.columns(3)  # ajuste: 2 (mais destaque) | 3 (equilíbrio) | 4 (mais compacto)

            for i, obj in enumerate(arquivos_aleatorios):
                key = obj["Key"]
                url = gerar_url_temporaria(key)

                with cols[i % 3]:
                    # extrai nome e momento do nome do arquivo
                    partes = key.split("_")

                    nome = partes[0] if len(partes) > 0 else "desconhecido"
                    momento = partes[1] if len(partes) > 1 else "sem_momento"
                    if len(momento.split('.'))>1:
                        momento='Desconhecido'

                    # deixa mais bonito
                    nome = nome.replace("-", " ").title()
                    momento = momento.replace("-", " ").title()

                    st.markdown(f"""
                        <div style="
                            width: 100%;
                            margin-bottom: 25px;
                        ">
                            <div style="
                                width: 100%;
                                height: 500px;
                                border-radius: 15px;
                                overflow: hidden;
                                background-color: #ffffff;
                                box-shadow: 0 4px 15px rgba(0,0,0,0.4);
                            ">
                                <img src="{url}" style="
                                    width: 100%;
                                    height: 100%;
                                    object-fit: cover;
                                ">
                            </div>
                            <div style="
                                padding: 10px 5px;
                                color: #9ca3af;
                                font-size: 14px;
                            ">
                                <strong>👤 {nome}</strong><br>
                                <span style="color:#9ca3af;">📍 {momento}</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

#========================
#Configurações
#========================

with aba[2]:

    # inicializa estado
    if "logado" not in st.session_state:
        st.session_state.logado = False

    st.subheader("⚙️ Configurações")

    # 🔐 SE NÃO ESTIVER LOGADO → MOSTRA LOGIN
    if not st.session_state.logado:

        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")

        if st.button("Entrar"):

            if usuario == "admin" and senha == "casamento@amanda1234":
                st.session_state.logado = True
                st.success("Login realizado com sucesso!")
                st.rerun()  # 🔥 atualiza a tela
            else:
                st.error("Usuário ou senha inválidos")

    # ✅ SE ESTIVER LOGADO → MOSTRA CONFIGURAÇÕES
    else:

        st.success("Você está logado como admin")

        # carregar config UMA vez
        config = carregar_config()

        # inicializa session_state
        if "bloquear_upload" not in st.session_state:
            st.session_state.bloquear_upload = config.get("bloquear_upload", False)

        if "bloquear_galeria" not in st.session_state:
            st.session_state.bloquear_galeria = config.get("bloquear_galeria", False)

        # 🔒 toggles (SEM atribuição!)
        st.toggle(
            "Bloquear envio de fotos",
            key="bloquear_upload"
        )

        st.toggle(
            "Bloquear galeria de fotos",
            key="bloquear_galeria"
        )

        # 💾 salvar SOMENTE quando clicar
        if st.button("Salvar configurações"):

            novo_config = {
                **config,
                "bloquear_upload": st.session_state.bloquear_upload,
                "bloquear_galeria": st.session_state.bloquear_galeria
            }

            salvar_config(novo_config)

            st.success("Configurações salvas!")

        # 🚪 logout
        if st.button("Sair"):
            st.session_state.logado = False
            st.rerun()
