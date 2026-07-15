# 💧 Coletor de Dinâmicas - Water Lab

Este é o repositório do site construído em **Streamlit** para coletar e salvar as respostas das dinâmicas do **Water Lab** em tempo real no **Google Sheets** (Planilhas Google).

---

## 🚀 Como Funciona o Fluxo de Dados
1. O participante ou grupo entra no site pelo celular ou computador.
2. Seleciona a dinâmica atual na barra lateral e preenche o formulário.
3. Ao clicar em enviar, a resposta é salva automaticamente como uma nova linha na aba correspondente da planilha no Google Drive.

---

## 🛠️ Passo 1: Configurar a Planilha e a API do Google (Gratuito)

Para conectar o site à sua planilha, precisamos de credenciais da API do Google. Siga estes passos simples:

### 1. Criar a Planilha no Google Drive
1. Crie uma planilha vazia no seu Google Drive e nomeie-a como quiser (ex: `Respostas Water Lab`).
2. Crie ou renomeie as abas (Worksheets) da planilha para que tenham os seguintes nomes exatos:
   - `01_Mural_Surpresa`
   - `03_Canvas_Barreiras`
   - `04_Brainwriting`
   - `05_Matriz_Ideias`
   - `07_Filtro_Etico`
   - `08_Impacto_Viabilidade`
   - `09_Desenho_Intervencao`
3. Copie o link (URL) da planilha do seu navegador (vamos usar no passo 3).

### 2. Ativar as APIs no Google Cloud
1. Acesse o [Google Cloud Console](https://console.cloud.google.com/).
2. Faça login com sua conta Google e crie um novo projeto (ex: `Water Lab App`).
3. No menu de pesquisa superior, procure e **Ative** as duas seguintes APIs:
   - **Google Sheets API**
   - **Google Drive API**

### 3. Criar uma Conta de Serviço (Service Account) e baixar a chave
1. No menu lateral do Google Cloud, vá em **IAM e administrador** > **Contas de serviço**.
2. Clique em **+ Criar conta de serviço** no topo.
3. Dê um nome (ex: `sheets-connector`) e clique em **Criar e Continuar**. Pule as permissões adicionais clicando em **Concluir**.
4. Você verá a conta criada listada na tela. Copie o endereço de e-mail dela (ex: `sheets-connector@seu-projeto.iam.gserviceaccount.com`).
5. **IMPORTANTE:** Vá na sua Planilha do Google, clique no botão **Compartilhar** no canto superior direito, cole esse e-mail da conta de serviço e dê permissão de **Editor** (para que ela possa escrever na planilha).
6. Volte ao Google Cloud Console, clique no e-mail da conta de serviço que você acabou de criar.
7. Vá na aba **Chaves** (Keys), clique em **Adicionar chave** > **Criar nova chave**.
8. Escolha o formato **JSON** e clique em **Criar**. Um arquivo `.json` será baixado no seu computador. Abra ele no bloco de notas para copiar as informações no próximo passo.

---

## 💻 Passo 2: Executar e Testar Localmente (Opcional)

Se você quiser testar o site no seu computador antes de subir para a internet:

1. Abra a pasta do projeto no seu computador.
2. Entre na pasta `.streamlit`.
3. Duplique ou renomeie o arquivo `secrets.toml.template` para `secrets.toml`.
4. Abra o `secrets.toml` com um editor de texto e preencha as informações copiando e colando os valores de dentro do arquivo JSON que você baixou do Google Cloud.
5. No final do arquivo, insira a URL da sua planilha na variável `spreadsheet_url`.
6. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
7. Rode o aplicativo:
   ```bash
   streamlit run app.py
   ```
8. O navegador abrirá a página local do site para teste.

---

## 📦 Passo 3: Colocar no seu GitHub

### Método Rápido (Via Navegador):
1. Crie um repositório público ou privado no seu [GitHub](https://github.com/). Nomeie como `water-lab-app`.
2. Não adicione README ou gitignore no GitHub (pois já criamos aqui localmente).
3. Na página do repositório vazio, clique no link **"uploading an existing file"** (carregar um arquivo existente).
4. Arraste e solte os seguintes arquivos do seu computador para o navegador:
   - `app.py`
   - `requirements.txt`
   - `.gitignore` (para evitar que seus segredos vazem por engano caso crie o secrets.toml local)
   - `README.md`
5. Clique em **Commit changes** para salvar.

### Método via Terminal (Se você tem Git instalado):
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/water-lab-app.git
git push -u origin main
```

---

## 🌐 Passo 4: Publicar no Streamlit Community Cloud (Hospedagem Gratuita)

1. Acesse o [Streamlit Share](https://share.streamlit.io/) e faça login com sua conta do GitHub.
2. Clique em **Create app** (Criar aplicativo).
3. Preencha os detalhes:
   - **Repository:** Selecione o seu repositório `water-lab-app` do GitHub.
   - **Branch:** `main`
   - **Main file path:** `app.py`
4. **IMPORTANTE (Adicionar Segredos):** No formulário de publicação, antes de clicar em Deploy, clique em **Advanced settings...** (Configurações avançadas) ou acesse as configurações de segredos após o deploy.
5. Na caixa de texto **Secrets**, cole a mesma estrutura do seu arquivo `secrets.toml` preenchido:
   ```toml
   [gspread]
   type = "service_account"
   project_id = "..."
   private_key_id = "..."
   private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
   client_email = "..."
   client_id = "..."
   auth_uri = "https://accounts.google.com/o/oauth2/auth"
   token_uri = "https://oauth2.googleapis.com/token"
   auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
   client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/..."
   universe_domain = "googleapis.com"
   spreadsheet_url = "https://docs.google.com/spreadsheets/d/.../edit"
   ```
6. Clique em **Save** e depois em **Deploy!**

Pronto! Em poucos minutos o Streamlit irá configurar o ambiente e fornecerá um link público (ex: `https://water-lab-app.streamlit.app/`) que você poderá compartilhar com todos os participantes!
