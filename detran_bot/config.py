# Configurações do Bot Detran-SP

# Token do bot Discord (deve ser definido como variável de ambiente)
import os
DISCORD_TOKEN = os.environ.get("TOKEN", "SEU_TOKEN_AQUI")

# IDs de cargos do Discord
ROLE_FUNCIONARIOS = 1404275629427261490
ROLE_GERENCIA = 1405260058224234637
# Cargo atribuído automaticamente a novos membros
ROLE_INICIAL = 1403835890803146865
# Cargo concedido após registro no servidor
ROLE_REGISTRADO = 1408159947015065630

# IDs de canais do Discord
# Canal onde o painel de controle será publicado
CANAL_PAINEL_FUNCIONARIOS = 1408158616783163616
# Canal onde novos membros devem se registrar
CANAL_REGISTRO = 1403794454413967526

# Configurações de permissões por cargo
CARGOS_PERMISSOES = {
    "Diretor": [
        "painel", "registrar", "cnh_emitir", "cnh_renovar", "cnh_suspender", "cnh_cassar",
        "membro_adicionar", "membro_remover", "veiculo_registrar", "veiculo_transferir",
        "veiculo_apreender", "veiculo_liberar", "multar", "multa_pagar", "multa_recorrer",
        "curso_inscrever", "curso_aprovar", "curso_reprovar", "blitz_iniciar", "blitz_finalizar",
        "relatorios"
    ],
    "Instrutor": [
        "painel", "registrar", "cnh_emitir", "cnh_renovar", "veiculo_registrar", "veiculo_transferir",
        "curso_inscrever", "curso_aprovar", "curso_reprovar"
    ],
    "Agente": [
        "painel", "veiculo_apreender", "veiculo_liberar", "multar", "blitz_iniciar", "blitz_finalizar"
    ]
}

# Comandos permitidos para o cargo padrão de funcionários
PERMISSOES_FUNCIONARIOS = list({
    comando
    for cargo, comandos in CARGOS_PERMISSOES.items()
    if cargo != "Diretor"
    for comando in comandos
})

# Tabela de infrações e multas
# Valores em dinheiro virtual do servidor
TABELA_INFRACOES = {
    # Capítulo I – Infrações Leves
    "estacionamento_proibido": {
        "descricao": "Estacionamento em local proibido (calçada, faixa, garagem)",
        "valor": 2000.0,
        "pontos": 3,
        "patio": 1
    },
    "nao_uso_cinto": {
        "descricao": "Não utilização do cinto de segurança",
        "valor": 2000.0,
        "pontos": 3,
        "patio": 1
    },
    "abandono_veiculo": {
        "descricao": "Abandono de veículo em área inadequada",
        "valor": 2500.0,
        "pontos": 3,
        "patio": 1
    },
    "poluicao_sonora": {
        "descricao": "Poluição sonora (ex: som alto, escapamento modificado)",
        "valor": 2500.0,
        "pontos": 3,
        "patio": 1
    },
    "avancar_sinal_vermelho": {
        "descricao": "Avançar sinal vermelho",
        "valor": 3000.0,
        "pontos": 3,
        "patio": 1
    },
    "trafegar_contramao": {
        "descricao": "Trafegar na contramão",
        "valor": 3500.0,
        "pontos": 3,
        "patio": 1
    },
    "excesso_velocidade_ate_20": {
        "descricao": "Excesso de velocidade (até 20% acima do limite)",
        "valor": 3500.0,
        "pontos": 3,
        "patio": 1
    },
    "farois_desligados_noite": {
        "descricao": "Conduzir veículo com faróis desligados à noite",
        "valor": 3500.0,
        "pontos": 3,
        "patio": 1
    },
    "sem_documentos_veiculo": {
        "descricao": "Dirigir sem os documentos do veículo",
        "valor": 4000.0,
        "pontos": 3,
        "patio": 1
    },
    "nao_uso_capacete": {
        "descricao": "Não uso de capacete (motocicleta)",
        "valor": 4000.0,
        "pontos": 3,
        "patio": 1
    },

    # Capítulo II – Infrações Médias
    "excesso_velocidade_acima_20": {
        "descricao": "Excesso de velocidade grave (acima de 20% do limite)",
        "valor": 5000.0,
        "pontos": 4,
        "patio": 1
    },
    "transporte_irregular_passageiros": {
        "descricao": "Transporte irregular de passageiros ou carga",
        "valor": 6000.0,
        "pontos": 4,
        "patio": 1
    },
    "ultrapassagem_perigosa": {
        "descricao": "Ultrapassagem perigosa (curvas, faixa contínua)",
        "valor": 6500.0,
        "pontos": 4,
        "patio": 1
    },
    "direcao_perigosa_sem_abordagem": {
        "descricao": "Direção perigosa sem abordagem policial",
        "valor": 7000.0,
        "pontos": 4,
        "patio": 1
    },
    "fuga_blitz": {
        "descricao": "Fuga de blitz sem perseguição policial",
        "valor": 8000.0,
        "pontos": 4,
        "patio": 1
    },
    "farois_lanternas_adulterados": {
        "descricao": "Veículo com faróis ou lanternas adulteradas (xenônio ilegal)",
        "valor": 8000.0,
        "pontos": 4,
        "patio": 1
    },
    "uso_indevido_giroflex": {
        "descricao": "Uso indevido de giroflex ou sirene",
        "valor": 8000.0,
        "pontos": 4,
        "patio": 1
    },
    "cnh_vencida_suspensa": {
        "descricao": "Dirigir com CNH vencida ou suspensa",
        "valor": 9000.0,
        "pontos": 4,
        "patio": 1
    },
    "sem_placa_adulterada": {
        "descricao": "Veículo sem placa ou com placa adulterada",
        "valor": 9000.0,
        "pontos": 4,
        "patio": 1
    },
    "excesso_velocidade_rodovia_40": {
        "descricao": "Excesso de velocidade em rodovia (acima de 40% do limite)",
        "valor": 9000.0,
        "pontos": 4,
        "patio": 1
    },

    # Capítulo III – Infrações Graves
    "alcool_ou_drogas": {
        "descricao": "Condução sob influência de álcool ou drogas",
        "valor": 12000.0,
        "pontos": 5,
        "patio": 4
    },
    "recusa_bafometro": {
        "descricao": "Recusa ao teste do bafômetro",
        "valor": 12000.0,
        "pontos": 5,
        "patio": 4
    },
    "fuga_perseguicao": {
        "descricao": "Fuga de abordagem policial com perseguição",
        "valor": 15000.0,
        "pontos": 5,
        "patio": 4
    },
    "direcao_perigosa_perseguicao": {
        "descricao": "Direção perigosa durante perseguição policial",
        "valor": 15000.0,
        "pontos": 5,
        "patio": 4
    },
    "racha": {
        "descricao": "Participação em racha ou corrida ilegal",
        "valor": 15000.0,
        "pontos": 5,
        "patio": 4
    },
    "transporte_produto_ilicito": {
        "descricao": "Transporte de produto ilícito (drogas, contrabando)",
        "valor": 16000.0,
        "pontos": 5,
        "patio": 4
    },
    "obstrucao_via_publica": {
        "descricao": "Obstrução intencional de via pública",
        "valor": 16000.0,
        "pontos": 5,
        "patio": 4
    },
    "forcar_passagem_bloqueio": {
        "descricao": "Forçar passagem em bloqueio policial",
        "valor": 17000.0,
        "pontos": 5,
        "patio": 4
    },
    "resistencia_desacato": {
        "descricao": "Resistência ou desacato em abordagem veicular",
        "valor": 18000.0,
        "pontos": 5,
        "patio": 4
    },
    "fuga_crime_leve": {
        "descricao": "Utilização de veículo em fuga de crime leve",
        "valor": 19000.0,
        "pontos": 5,
        "patio": 4
    },

    # Capítulo IV – Infrações Gravíssimas
    "veiculo_em_assalto": {
        "descricao": "Uso de veículo em assalto",
        "valor": 20000.0,
        "pontos": 7,
        "patio": 24
    },
    "transporte_armas": {
        "descricao": "Transporte de armas ilegais no veículo",
        "valor": 22000.0,
        "pontos": 7,
        "patio": 24
    },
    "transporte_refem": {
        "descricao": "Transporte de refém em veículo",
        "valor": 25000.0,
        "pontos": 7,
        "patio": 24
    },
    "fuga_troca_tiros_pm": {
        "descricao": "Fuga com troca de tiros contra a Polícia Militar",
        "valor": 27000.0,
        "pontos": 7,
        "patio": 24
    },
    "veiculo_sequestro": {
        "descricao": "Veículo utilizado em sequestro",
        "valor": 28000.0,
        "pontos": 7,
        "patio": 24
    },
    "veiculo_blindado_clonado": {
        "descricao": "Condução de veículo fortemente blindado ou clonado",
        "valor": 28000.0,
        "pontos": 7,
        "patio": 24
    },
    "fuga_com_refem": {
        "descricao": "Utilização de veículo em fuga com refém",
        "valor": 30000.0,
        "pontos": 7,
        "patio": 24
    },
    "veiculo_atentado_autoridades": {
        "descricao": "Utilização de veículo em atentado contra autoridades",
        "valor": 30000.0,
        "pontos": 7,
        "patio": 24
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

