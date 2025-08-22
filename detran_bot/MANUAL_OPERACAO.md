# Manual de Operação - Bot Detran-SP

## 📋 Guia para Agentes, Instrutores e Diretores

Este manual descreve como usar o Bot Detran-SP para gerenciar as operações do departamento de trânsito no roleplay.

---

## 🚀 Primeiros Passos

### 1. Verificar Permissões
Certifique-se de que você possui o cargo correto para executar o comando.

### 2. Comandos Básicos de Consulta
Estes comandos podem ser usados por qualquer usuário:
- `/taxas` - Ver tabela de taxas oficiais
- `/infracoes` - Ver tabela de infrações e multas
- `/pop` - Consultar Protocolo Operacional Padrão
- `/regulamento` - Ver Regulamento Interno

---


## 📝 Registro de Jogadores

### Registrar Novo Jogador
```
/registrar_jogador UTC58846 "João Silva" "(11) 99999-9999"
```
- **RG**: Identificador único do jogador no jogo
- **Nome**: Nome do personagem no RP
- **Telefone**: Opcional

**Permissões:** Diretor, Instrutor

---

## 🚗 Gestão de CNH

### Emitir CNH
```
/cnh_emitir UTC58846 B
```
**Categorias disponíveis:**
- A: Motocicletas
- B: Automóveis
- C, D, E: Veículos pesados
- Náutica: Embarcações
- Aérea: Aeronaves

### Consultar CNH
```
/cnh_consultar UTC58846
```
Mostra status, pontos e todas as categorias do jogador.

### Suspender CNH
```
/cnh_suspender UTC58846 30
```
Suspende por número de dias especificado.

### Cassar CNH
```
/cnh_cassar UTC58846
```
Cassação definitiva da habilitação.

**Permissões:** Diretor (todos), Instrutor (emitir/renovar)

---

## 🚙 Gestão de Veículos

### Registrar Veículo
```
/veiculo_registrar UTC58846 ABC1234 "Honda Civic" Preto 2020 CHASSI123456
```

### Consultar Veículo
```
/veiculo_consultar ABC1234
```

### Transferir Propriedade
```
/veiculo_transferir ABC1234 UTC99999
```

### Apreender Veículo
```
/veiculo_apreender ABC1234
```

### Liberar Veículo
```
/veiculo_liberar ABC1234
```

**Permissões:** 
- Registrar/Transferir: Diretor, Instrutor
- Apreender/Liberar: Diretor, Agente

---

## 🚨 Sistema de Multas

### Aplicar Multa
```
/multar UTC58846 excesso_velocidade_leve ABC1234
```

**Tipos de Infração:**
- `excesso_velocidade_leve` - R$ 150, 3 pontos
- `excesso_velocidade_medio` - R$ 300, 5 pontos
- `excesso_velocidade_grave` - R$ 600, 7 pontos
- `conducao_sem_cnh` - R$ 800, 7 pontos
- `documentacao_irregular` - R$ 400, 5 pontos
- `recusa_bafometro` - R$ 1.000, 10 pontos
- `direcao_perigosa` - R$ 900, 7 pontos
- `estacionamento_proibido` - R$ 200, 3 pontos
- `sem_capacete` - R$ 350, 5 pontos
- `transporte_irregular` - R$ 700, 7 pontos

### Consultar Multas
```
/multa_consultar UTC58846 pendente
```
Status: pendente, paga, recorrida

### Processar Pagamento
```
/multa_pagar 123
```

### Registrar Recurso
```
/multa_recorrer 123
```

**Permissões:** Diretor, Agente

---


## 📊 Relatórios

### Relatório de Multas por Agente
```
/relatorio_multas_agente @agente
```

### CNHs Suspensas
```
/relatorio_cnhs_suspensas
```

**Permissões:** Diretor

---

## ⚠️ Regras Importantes

### Sistema de Pontuação
- **20 pontos**: CNH suspensa automaticamente
- **30 pontos**: CNH revogada automaticamente

### Reincidência
- Mesma infração em 12 meses = multa em dobro
- O sistema detecta automaticamente

### Valores Oficiais
- Baseados na tabela oficial do Detran-SP
- Multas: R$ 150 a R$ 1.000
- Taxas: R$ 200 a R$ 5.000

---

## 🔧 Dicas de Uso

### Para Agentes
1. Sempre verifique documentação antes de multar
2. Use `/veiculo_consultar` para verificar status do veículo
3. Registre todas as ocorrências durante blitz

### Para Instrutores
1. Registre jogadores quando necessário
2. Emita CNH apenas após verificar os requisitos
3. Use `/cnh_consultar` para verificar status antes de emitir

### Para Diretores
1. Monitore relatórios regularmente
2. Gerencie permissões da equipe
3. Supervisione operações de grande porte

---

## 🆘 Solução de Problemas

### "Sem Permissão"
- Confirme se seu cargo tem permissão para o comando

### "Jogador Não Encontrado"
- Verifique se o RG está correto
- Use `/registrar_jogador` se o jogador não estiver no sistema

### "Veículo Não Encontrado"
- Confirme a placa digitada
- Use `/veiculo_registrar` se necessário

### Multa Não Aplicada
- Verifique se o jogador existe
- Confirme se você tem permissão de agente

---

## 📞 Suporte

Para dúvidas ou problemas técnicos, entre em contato com a Direção Geral do Detran-SP.

**Lembre-se:** Sempre siga o POP e o Regulamento Interno durante as operações!

