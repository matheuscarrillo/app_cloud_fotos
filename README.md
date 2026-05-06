# 🚀 Deploy do Streamlit na AWS EC2 com Python 3.11

Este guia mostra como configurar uma instância EC2 e rodar sua aplicação Streamlit usando **Python 3.11**, garantindo compatibilidade e estabilidade.

---

## 🧠 Visão Geral

Você irá:

1. Criar uma instância EC2  
2. Instalar Python 3.11 (via pyenv)  
3. Clonar o repositório  
4. Criar ambiente virtual  
5. Instalar dependências  
6. Rodar o Streamlit  

⏱️ Tempo estimado: ~20 minutos

---

## ✅ 1. Criar Instância EC2

- Acesse o console da AWS → EC2 → Launch Instance

### 🔧 Configurações recomendadas:

| Campo           | Valor                  |
|----------------|-----------------------|
| Nome           | streamlit-app         |
| AMI            | Ubuntu 22.04 LTS      |
| Tipo           | t3.small              |
| Região         | sa-east-1 (São Paulo) |

---

### 🔑 Key Pair
- Crie uma nova chave (.pem)
- Faça o download e guarde com segurança

---

### 🌐 Security Group

Adicione as seguintes regras:

| Tipo        | Porta |
|-------------|-------|
| SSH         | 22    |
| Custom TCP  | 8501  |

---

## ✅ 2. Conectar na EC2

```bash
chmod 400 sua-chave.pem

ssh -i sua-chave.pem ubuntu@SEU_IP_PUBLICO
```

---

## ✅ 3. Instalar dependências do sistema

```bash
sudo apt update

sudo apt install -y make build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev curl libncursesw5-dev \
xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
```

---

## ✅ 4. Instalar pyenv

```bash
curl https://pyenv.run | bash
```

---

## ✅ 5. Configurar pyenv

```bash
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init --path)"' >> ~/.bashrc

source ~/.bashrc
```

---

## ✅ 6. Instalar Python 3.11

```bash
pyenv install 3.11.9
pyenv global 3.11.9
```

---

## ✅ 7. Clonar o repositório

```bash
sudo apt install git -y

git clone https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
cd SEU_REPOSITORIO
```

---

## ✅ 8. Criar ambiente virtual

```bash
python -m venv venv
source venv/bin/activate
```

---

## ✅ 9. Instalar dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## ✅ 10. Rodar a aplicação

```bash
streamlit run main.py --server.port 8501 --server.address 0.0.0.0
```

---

## 🌐 11. Acessar no navegador

```
http://SEU_IP_PUBLICO:8501
```

---

## 🔥 12. Manter o app rodando (IMPORTANTE)

### Opção 1 — Simples (recomendado)

```bash
nohup streamlit run main.py --server.port 8501 --server.address 0.0.0.0 > log.out 2>&1 &
```

👉 O app continua rodando mesmo após fechar o terminal

---

### Opção 2 — Melhor (usando screen)

```bash
sudo apt install screen -y
screen
```

Dentro do screen, rode:

```bash
streamlit run main.py --server.port 8501 --server.address 0.0.0.0
```

Para sair sem parar o app:

```
Ctrl + A + D
```

Para voltar:

```bash
screen -r
```

---

## ⚙️ 13. (Opcional) Executar automaticamente no boot

```bash
sudo nano /etc/systemd/system/streamlit.service
```

Conteúdo:

```ini
[Unit]
Description=Streamlit App
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/SEU_REPOSITORIO
ExecStart=/home/ubuntu/SEU_REPOSITORIO/venv/bin/streamlit run main.py --server.port 8501 --server.address 0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
```

Ativar:

```bash
sudo systemctl daemon-reexec
sudo systemctl enable streamlit
sudo systemctl start streamlit
```

---

## 💰 Custo estimado

- t3.small → ~R$ 20–30 por semana  

---

## ⚠️ Boas práticas

- Não salvar credenciais AWS no código  
- Usar IAM Role na EC2  
- Não depender de arquivos locais para config  
- Usar S3 para persistência  

---

## 🎯 Resultado final

- Python 3.11 instalado  
- Ambiente isolado  
- Streamlit rodando publicamente  
- App persistente (não para ao fechar terminal)  

---

## 🚀 Próximos passos (opcional)

- Configurar domínio (ex: fotos.com)  
- Adicionar HTTPS (Let's Encrypt)  
- Implementar upload direto para S3  
- Escalar para múltiplos usuários  