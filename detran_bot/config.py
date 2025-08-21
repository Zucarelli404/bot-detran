# Configurações do Bot Detran-SP

# Token do bot Discord (deve ser definido como variável de ambiente)
import os
DISCORD_TOKEN = os.environ.get("TOKEN", "SEU_TOKEN_AQUI")

# IDs de cargos do Discord
ROLE_FUNCIONARIOS = 1404275629427261490
ROLE_GERENCIA = 1405260058224234637

# Configurações de permissões por cargo
CARGOS_PERMISSOES = {
    "Diretor": [
        "registrar", "cnh_emitir", "cnh_renovar", "cnh_suspender", "cnh_cassar",
        "membro_adicionar", "membro_remover", "veiculo_registrar", "veiculo_transferir",
        "veiculo_apreender", "veiculo_liberar", "multar", "multa_pagar", "multa_recorrer",
        "curso_inscrever", "curso_aprovar", "curso_reprovar", "blitz_iniciar", "blitz_finalizar",
        "relatorios"
    ],
    "Instrutor": [
        "registrar", "cnh_emitir", "cnh_renovar", "veiculo_registrar", "veiculo_transferir",
        "curso_inscrever", "curso_aprovar", "curso_reprovar"
    ],
    "Agente": [
        "veiculo_apreender", "veiculo_liberar", "multar", "blitz_iniciar", "blitz_finalizar"
    ]
}

# Comandos permitidos para o cargo padrão de funcionários
PERMISSOES_FUNCIONARIOS = list({
    comando
    for cargo, comandos in CARGOS_PERMISSOES.items()
    if cargo != "Diretor"
    for comando in comandos
})

# Tabela de infrações e multas (baseada no documento oficial)
TABELA_INFRACOES = {
    "excesso_velocidade_leve": {
        "descricao": "Excesso de velocidade até 20 km/h acima do limite",
        "valor": 150.0,
        "pontos": 3
    },
    "excesso_velocidade_medio": {
        "descricao": "Excesso de velocidade entre 21 e 40 km/h acima do limite",
        "valor": 300.0,
        "pontos": 5
    },
    "excesso_velocidade_grave": {
        "descricao": "Excesso de velocidade acima de 40 km/h do limite",
        "valor": 600.0,
        "pontos": 7
    },
    "conducao_sem_cnh": {
        "descricao": "Dirigir sem habilitação ou com CNH vencida",
        "valor": 800.0,
        "pontos": 7
    },
    "documentacao_irregular": {
        "descricao": "Veículo com documentação irregular ou vencida",
        "valor": 400.0,
        "pontos": 5
    },
    "recusa_bafometro": {
        "descricao": "Recusar ou fugir de teste de alcoolemia (Lei Seca)",
        "valor": 1000.0,
        "pontos": 10
    },
    "direcao_perigosa": {
        "descricao": "Dirigir de forma perigosa, colocando terceiros em risco",
        "valor": 900.0,
        "pontos": 7
    },
    "estacionamento_proibido": {
        "descricao": "Estacionar em local não autorizado",
        "valor": 200.0,
        "pontos": 3
    },
    "sem_capacete": {
        "descricao": "Conduzir moto sem capacete de segurança",
        "valor": 350.0,
        "pontos": 5
    },
    "transporte_irregular": {
        "descricao": "Violar regras de transporte de carga ou passageiros",
        "valor": 700.0,
        "pontos": 7
    }
}

# Tabela de taxas de serviços (baseada no documento oficial)
TABELA_TAXAS = {
    "primeira_habilitacao": {
        "descricao": "Emissão da 1ª Habilitação (CNH)",
        "valor": 500.0
    },
    "renovacao_cnh": {
        "descricao": "Renovação da CNH",
        "valor": 300.0
    },
    "curso_reciclagem": {
        "descricao": "Curso Obrigatório para Condutores Infratores",
        "valor": 250.0
    },
    "emissao_crlv": {
        "descricao": "Emissão de CRLV",
        "valor": 200.0
    },
    "transferencia_propriedade": {
        "descricao": "Transferência de Propriedade de Veículo",
        "valor": 400.0
    },
    "liberacao_veiculo": {
        "descricao": "Liberação de Veículo Apreendido",
        "valor": 600.0
    },
    "participacao_leilao": {
        "descricao": "Taxa de Participação em Leilão de Veículo",
        "valor": 1500.0
    },
    "curso_nautica": {
        "descricao": "Curso para Habilitação Náutica",
        "valor": 3500.0
    },
    "curso_aerea": {
        "descricao": "Curso para Habilitação Aérea",
        "valor": 5000.0
    }
}

# Limites de pontuação da CNH
LIMITE_SUSPENSAO_CNH = 20
LIMITE_REVOGACAO_CNH = 30

# Cores para embeds do Discord
CORES = {
    "sucesso": 0x00ff00,
    "erro": 0xff0000,
    "aviso": 0xffff00,
    "info": 0x0099ff,
    "detran": 0x003366
}

# Protocolo Operacional Padrão (resumo)
POP_RESUMO = """
**Protocolo Operacional Padrão (POP) para Fiscalização**

**Equipamentos Necessários:**
• Rádio comunicador
• Equipamentos para teste de alcoolemia (Lei Seca)
• Radar móvel portátil
• Colete refletivo e uniformes oficiais
• Sistema digital para registro de autuações
• Veículo de fiscalização com sirenes e iluminação

**Procedimentos:**
1. **Planejamento:** Operação autorizada pela Direção Geral
2. **Abordagem:** Posicionamento seguro, sinais luminosos, cortesia
3. **Verificação:** Solicitar CNH, CRLV, verificar validade
4. **Multas:** Aplicar conforme tabela oficial, explicar direitos
5. **Lei Seca:** Teste simulado, penalidades conforme regulamento
6. **Recolhimento:** Guincho para pátio, documentação completa
7. **Finalização:** Relatório para Direção Geral

**Segurança:** Usar EPIs, manter comunicação, acionar PM se necessário
"""

# Regulamento Interno (resumo)
REGULAMENTO_RESUMO = """
**Regulamento Interno do Departamento de Trânsito e Transportes**

**Responsabilidades:**
• **Agentes de Fiscalização:** Cumprir POP, agir com ética e profissionalismo
• **Coordenadores:** Planejar, supervisionar e avaliar operações
• **Direção Geral:** Aprovar operações, analisar relatórios, promover treinamentos

**Procedimentos de Fiscalização:**
• Operações devem ser autorizadas e comunicadas
• Abordagem cortês e identificação obrigatória
• Verificação documental rigorosa
• Aplicação de penalidades conforme tabela oficial
• Registro completo de todas as ocorrências

**Contatos de Emergência:**
• CPTRAN: Para apoio em operações
• Polícia Militar: Em casos de resistência ou conflito
"""

