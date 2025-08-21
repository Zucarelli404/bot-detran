# Bot Detran-SP - Roleplay

Bot para Discord que administra e controla o Detran-SP de uma cidade de roleplay, incluindo funcionalidades de registro, multas, CNH, veículos e cursos.

## 🚀 Funcionalidades

### 👥 Gestão de Membros
- Adicionar/remover membros da equipe do Detran
- Controle de permissões por cargo (Diretor, Instrutor, Agente)
- Listagem de membros por cargo

### 📋 Registro de Jogadores
- Registro de jogadores usando RG do jogo
- Consulta de informações dos jogadores
- Controle de status da CNH e pontuação

### 🚗 Gestão de CNH
- Emissão de CNH para diferentes categorias (A, B, C, D, E, Náutica, Aérea)
- Renovação de CNH
- Suspensão e cassação automática por pontos
- Consulta de status e detalhes da CNH

### 🚙 Gestão de Veículos
- Registro de veículos com CRLV
- Transferência de propriedade
- Apreensão e liberação de veículos
- Consulta de informações do veículo

### 🚨 Sistema de Multas
- Aplicação de multas baseada na tabela oficial
- Controle de reincidência (multa em dobro)
- Pagamento e recurso de multas
- Atualização automática de pontos na CNH

### 📚 Gestão de Cursos
- Listagem de cursos disponíveis
- Inscrição em cursos
- Aprovação/reprovação de alunos
- Controle de status dos cursos

### 📊 Relatórios
- Relatório de multas por agente
- Lista de CNHs suspensas/revogadas
- Consultas diversas

### 📖 Informações
- Tabela de taxas de serviços
- Tabela de infrações e multas
- Protocolo Operacional Padrão (POP)
- Regulamento Interno

## 🛠️ Instalação

### Pré-requisitos
- Python 3.11+
- Bot Discord criado no Discord Developer Portal

### Passos

1. **Clone ou baixe os arquivos do bot**
   ```bash
   # Arquivos necessários:
   # - bot.py
   # - database.py
   # - config.py
   # - requirements.txt
   ```

2. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure o token do Discord**
   - Edite o arquivo `config.py`
   - Substitua `"SEU_TOKEN_AQUI"` pelo token do seu bot

4. **Execute o bot**
   ```bash
   python bot.py
   ```

## ⚙️ Configuração do Bot Discord

### 1. Criar o Bot
1. Acesse [Discord Developer Portal](https://discord.com/developers/applications)
2. Clique em "New Application"
3. Dê um nome ao seu bot (ex: "Detran-SP Bot")
4. Vá para a aba "Bot"
5. Clique em "Add Bot"
6. Copie o token e cole no arquivo `config.py`

### 2. Configurar Permissões
O bot precisa das seguintes permissões:
- `Send Messages`
- `Use Slash Commands`
- `Embed Links`
- `Read Message History`

### 3. Convidar o Bot
1. Vá para a aba "OAuth2" > "URL Generator"
2. Selecione "bot" e "applications.commands"
3. Selecione as permissões necessárias
4. Use a URL gerada para convidar o bot ao seu servidor

### 4. Intents Necessários
O bot usa os seguintes intents:
- `Message Content Intent` (se necessário)
- `Server Members Intent` (se necessário)

## 📋 Comandos Disponíveis

### Registro e CNH
- `/registrar` - Registra um novo jogador
- `/cnh_emitir` - Emite uma nova CNH
- `/cnh_consultar` - Consulta status da CNH
- `/cnh_suspender` - Suspende CNH
- `/cnh_cassar` - Cassa CNH

### Membros do Detran
- `/membro_adicionar` - Adiciona membro à equipe
- `/membro_listar` - Lista membros
- `/membro_remover` - Remove membro

### Veículos
- `/veiculo_registrar` - Registra veículo
- `/veiculo_consultar` - Consulta veículo
- `/veiculo_transferir` - Transfere propriedade
- `/veiculo_apreender` - Apreende veículo
- `/veiculo_liberar` - Libera veículo

### Multas
- `/multar` - Aplica multa
- `/multa_consultar` - Consulta multas
- `/multa_pagar` - Registra pagamento
- `/multa_recorrer` - Registra recurso

### Cursos
- `/curso_listar` - Lista cursos
- `/curso_inscrever` - Inscreve em curso
- `/curso_aprovar` - Aprova aluno
- `/curso_reprovar` - Reprova aluno

### Consultas
- `/taxas` - Tabela de taxas
- `/infracoes` - Tabela de infrações
- `/pop` - Protocolo Operacional
- `/regulamento` - Regulamento Interno

### Relatórios
- `/relatorio_multas_agente` - Relatório por agente
- `/relatorio_cnhs_suspensas` - CNHs suspensas

## 🔐 Sistema de Permissões

### Cargos e Permissões

**Diretor:**
- Acesso total a todos os comandos
- Gestão de membros
- Emissão e gestão de CNH
- Relatórios

**Instrutor:**
- Registro de jogadores
- Emissão e renovação de CNH
- Gestão de cursos
- Registro de veículos

**Agente:**
- Aplicação de multas
- Apreensão/liberação de veículos
- Operações de blitz

## 📊 Banco de Dados

O bot usa SQLite para armazenar dados localmente. O arquivo `detran.db` é criado automaticamente na primeira execução.

### Tabelas Principais:
- `players` - Jogadores registrados
- `membros_detran` - Membros da equipe
- `cnhs` - Carteiras de habilitação
- `veiculos` - Veículos registrados
- `multas` - Multas aplicadas
- `cursos` - Cursos disponíveis
- `inscricoes_cursos` - Inscrições em cursos

## 🚨 Regras de Negócio

### Pontuação da CNH
- **20 pontos:** CNH suspensa automaticamente
- **30 pontos:** CNH revogada automaticamente

### Reincidência
- Mesma infração em 12 meses: multa em dobro

### Valores
- Baseados na tabela oficial do documento
- Multas de R$ 150 a R$ 1.000
- Taxas de R$ 200 a R$ 5.000

## 🔧 Manutenção

### Backup do Banco
```bash
# Fazer backup do banco de dados
cp detran.db detran_backup_$(date +%Y%m%d).db
```

### Logs
O bot exibe logs no console durante a execução. Para logs persistentes, redirecione a saída:
```bash
python bot.py > bot.log 2>&1
```

## 🆘 Solução de Problemas

### Bot não responde aos comandos
1. Verifique se o token está correto
2. Verifique se o bot tem permissões no servidor
3. Verifique se os comandos foram sincronizados

### Erro de permissão
1. Verifique se o usuário está registrado como membro do Detran
2. Verifique se o cargo tem permissão para o comando

### Erro de banco de dados
1. Verifique se o arquivo `detran.db` não está corrompido
2. Delete o arquivo para recriar (perderá dados)

## 📝 Licença

Este bot foi desenvolvido para uso em servidores de roleplay. Sinta-se livre para modificar conforme suas necessidades.

## 🤝 Suporte

Para suporte ou dúvidas sobre o bot, consulte a documentação ou entre em contato com a equipe de desenvolvimento.

---

**Detran-SP Bot** - Desenvolvido para Cidade Salve RP

