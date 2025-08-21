# Guia de Instalação - Bot Detran-SP

## 📋 Pré-requisitos

### Sistema Operacional
- Windows 10/11, macOS, ou Linux
- Python 3.11 ou superior

### Conta Discord
- Conta Discord ativa
- Permissões para criar aplicações no Discord Developer Portal

---

## 🔧 Instalação Passo a Passo

### 1. Preparar o Ambiente

#### Windows
1. Baixe e instale Python 3.11+ do [site oficial](https://python.org)
2. Durante a instalação, marque "Add Python to PATH"
3. Abra o Prompt de Comando (cmd)

#### macOS
```bash
# Instalar Homebrew (se não tiver)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Instalar Python
brew install python@3.11
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3.11 python3.11-pip
```

### 2. Baixar os Arquivos do Bot

Crie uma pasta para o bot e baixe os seguintes arquivos:
- `bot.py`
- `database.py`
- `config.py`
- `requirements.txt`
- `README.md`
- `MANUAL_OPERACAO.md`

### 3. Instalar Dependências

Abra o terminal/prompt na pasta do bot e execute:
```bash
pip install -r requirements.txt
```

---

## 🤖 Configuração do Bot Discord

### 1. Criar Aplicação Discord

1. Acesse [Discord Developer Portal](https://discord.com/developers/applications)
2. Clique em "New Application"
3. Digite o nome: "Detran-SP Bot"
4. Clique em "Create"

### 2. Configurar o Bot

1. Na aba "Bot":
   - Clique em "Add Bot"
   - Copie o **Token** (mantenha secreto!)
   - Ative "Message Content Intent" se necessário

2. Na aba "OAuth2" > "URL Generator":
   - Selecione "bot" e "applications.commands"
   - Selecione as permissões:
     - Send Messages
     - Use Slash Commands
     - Embed Links
     - Read Message History

3. Copie a URL gerada e use para convidar o bot ao seu servidor

### 3. Configurar Token

Edite o arquivo `config.py`:
```python
# Substitua "SEU_TOKEN_AQUI" pelo token copiado
DISCORD_TOKEN = "seu_token_aqui"
```

---

## ⚙️ Configuração Inicial

### 1. Executar o Bot

```bash
python bot.py
```

Se tudo estiver correto, você verá:
```
Bot está online!
Sincronizados X comandos slash
```

### 2. Configurar Primeiro Diretor

No Discord, use os comandos:
```
/membro_adicionar @seu_usuario Diretor
```

### 3. Testar Funcionalidades

```
/taxas
/infracoes
/curso_listar
```

---

## 🔐 Configuração de Permissões

### Cargos do Discord (Opcional)

Você pode criar cargos no Discord para organizar:
- `@Diretor Detran`
- `@Instrutor Detran`
- `@Agente Detran`

### Permissões por Cargo

O bot controla permissões internamente:

**Diretor:**
- Todos os comandos
- Gestão de membros
- Relatórios

**Instrutor:**
- Registro de jogadores
- Gestão de CNH e cursos
- Registro de veículos

**Agente:**
- Aplicação de multas
- Apreensão de veículos
- Operações de blitz

---

## 📊 Backup e Manutenção

### Backup do Banco de Dados

O bot cria um arquivo `detran.db` automaticamente. Para backup:

```bash
# Windows
copy detran.db detran_backup_%date%.db

# macOS/Linux
cp detran.db detran_backup_$(date +%Y%m%d).db
```

### Logs do Bot

Para manter logs persistentes:

```bash
# Windows
python bot.py > bot.log 2>&1

# macOS/Linux
python bot.py > bot.log 2>&1 &
```

### Atualização

Para atualizar o bot:
1. Faça backup do `detran.db`
2. Substitua os arquivos Python
3. Execute `pip install -r requirements.txt`
4. Reinicie o bot

---

## 🚀 Execução em Produção

### Usando PM2 (Linux/macOS)

```bash
# Instalar PM2
npm install -g pm2

# Iniciar bot
pm2 start bot.py --name detran-bot --interpreter python3

# Ver status
pm2 status

# Ver logs
pm2 logs detran-bot

# Reiniciar
pm2 restart detran-bot
```

### Usando systemd (Linux)

Crie `/etc/systemd/system/detran-bot.service`:
```ini
[Unit]
Description=Detran-SP Discord Bot
After=network.target

[Service]
Type=simple
User=seu_usuario
WorkingDirectory=/caminho/para/bot
ExecStart=/usr/bin/python3 bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Ativar:
```bash
sudo systemctl enable detran-bot
sudo systemctl start detran-bot
```

---

## 🆘 Solução de Problemas

### Bot não inicia

**Erro: Token inválido**
- Verifique se o token está correto no `config.py`
- Regenere o token no Discord Developer Portal

**Erro: Módulo não encontrado**
- Execute `pip install -r requirements.txt`
- Verifique se está usando Python 3.11+

### Comandos não aparecem

**Comandos slash não sincronizam**
- Aguarde até 1 hora para sincronização global
- Reinicie o bot
- Verifique permissões do bot no servidor

### Erro de permissão

**"Sem Permissão" para todos**
- Use `/membro_adicionar` para registrar o primeiro diretor
- Verifique se o Discord ID está correto

### Banco de dados corrompido

```bash
# Backup atual
mv detran.db detran_corrupted.db

# O bot criará um novo banco na próxima execução
python bot.py
```

---

## 📱 Configuração Mobile

### Discord Mobile
- Todos os comandos funcionam no Discord mobile
- Use `/` para acessar comandos slash
- Embeds são exibidos corretamente

---

## 🔧 Configurações Avançadas

### Personalizar Valores

Edite `config.py` para ajustar:
- Valores de multas
- Limites de pontuação
- Cores dos embeds
- Textos do POP e Regulamento

### Adicionar Novas Infrações

Em `config.py`, adicione à `TABELA_INFRACOES`:
```python
"nova_infracao": {
    "descricao": "Descrição da infração",
    "valor": 500.0,
    "pontos": 5
}
```

### Modificar Permissões

Edite `CARGOS_PERMISSOES` em `config.py` para ajustar quem pode usar cada comando.

---

## 📞 Suporte Técnico

### Logs Importantes

Sempre inclua estas informações ao reportar problemas:
- Versão do Python (`python --version`)
- Sistema operacional
- Logs do bot
- Comando que causou o erro

### Contato

Para suporte técnico, forneça:
1. Descrição detalhada do problema
2. Logs de erro
3. Passos para reproduzir
4. Configuração do ambiente

---

## ✅ Checklist de Instalação

- [ ] Python 3.11+ instalado
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Bot criado no Discord Developer Portal
- [ ] Token configurado em `config.py`
- [ ] Bot convidado ao servidor Discord
- [ ] Permissões configuradas no Discord
- [ ] Bot executando sem erros
- [ ] Comandos slash sincronizados
- [ ] Primeiro diretor adicionado
- [ ] Comandos básicos testados
- [ ] Backup configurado

**Parabéns! Seu Bot Detran-SP está pronto para uso!** 🎉

