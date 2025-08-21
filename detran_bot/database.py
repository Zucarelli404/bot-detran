import sqlite3
import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

class DetranDatabase:
    def __init__(self, db_path: str = "detran.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicializa o banco de dados com as tabelas necessárias"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Tabela de jogadores
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS players (
                    rg_game TEXT PRIMARY KEY,
                    nome_rp TEXT NOT NULL,
                    cnh_status TEXT DEFAULT 'inativo',
                    pontos_cnh INTEGER DEFAULT 0,
                    telefone TEXT
                )
            ''')
            
            # Tabela de membros do Detran
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS membros_detran (
                    discord_id TEXT PRIMARY KEY,
                    nome_discord TEXT NOT NULL,
                    rg_game TEXT,
                    cargo TEXT NOT NULL,
                    FOREIGN KEY (rg_game) REFERENCES players(rg_game)
                )
            ''')
            
            # Tabela de CNHs
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cnhs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    jogador_id TEXT NOT NULL,
                    numero_registro TEXT UNIQUE NOT NULL,
                    data_emissao TEXT NOT NULL,
                    data_validade TEXT NOT NULL,
                    categoria TEXT NOT NULL,
                    FOREIGN KEY (jogador_id) REFERENCES players(rg_game)
                )
            ''')
            
            # Tabela de veículos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS veiculos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    proprietario_id TEXT NOT NULL,
                    placa TEXT UNIQUE NOT NULL,
                    modelo TEXT,
                    cor TEXT,
                    ano INTEGER,
                    chassi TEXT UNIQUE,
                    crlv_status TEXT DEFAULT 'ativo',
                    FOREIGN KEY (proprietario_id) REFERENCES players(rg_game)
                )
            ''')
            
            # Tabela de multas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS multas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    jogador_id TEXT NOT NULL,
                    veiculo_id INTEGER,
                    agente_id TEXT NOT NULL,
                    tipo_infracao TEXT NOT NULL,
                    valor REAL NOT NULL,
                    pontos INTEGER NOT NULL,
                    data_ocorrencia TEXT NOT NULL,
                    status TEXT DEFAULT 'pendente',
                    FOREIGN KEY (jogador_id) REFERENCES players(rg_game),
                    FOREIGN KEY (veiculo_id) REFERENCES veiculos(id),
                    FOREIGN KEY (agente_id) REFERENCES membros_detran(discord_id)
                )
            ''')
            
            # Tabela de cursos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cursos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome_curso TEXT UNIQUE NOT NULL,
                    carga_horaria_teorica INTEGER,
                    carga_horaria_pratica INTEGER,
                    requisitos_aprovacao TEXT
                )
            ''')
            
            # Tabela de inscrições em cursos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS inscricoes_cursos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    jogador_id TEXT NOT NULL,
                    curso_id INTEGER NOT NULL,
                    data_inscricao TEXT NOT NULL,
                    status TEXT DEFAULT 'em_andamento',
                    FOREIGN KEY (jogador_id) REFERENCES players(rg_game),
                    FOREIGN KEY (curso_id) REFERENCES cursos(id)
                )
            ''')
            
            # Tabela de pagamentos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pagamentos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    jogador_id TEXT NOT NULL,
                    referencia_id INTEGER NOT NULL,
                    tipo_pagamento TEXT NOT NULL,
                    valor_pago REAL NOT NULL,
                    data_pagamento TEXT NOT NULL,
                    FOREIGN KEY (jogador_id) REFERENCES players(rg_game)
                )
            ''')

            # Tabela de configuração geral
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS config (
                    chave TEXT PRIMARY KEY,
                    valor TEXT NOT NULL
                )
            ''')

            # Tabela de permissões dinâmicas de comandos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS command_permissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    comando TEXT NOT NULL,
                    role_id TEXT NOT NULL
                )
            ''')
            
            conn.commit()
            
            # Inserir cursos padrão se não existirem
            self._insert_default_courses(cursor)
            conn.commit()
    
    def _insert_default_courses(self, cursor):
        """Insere os cursos padrão baseados nos documentos"""
        cursos_padrao = [
            ("Licença A", 60, 30, "Prova teórica (mínimo 7 acertos de 10) + Percurso prático sem quedas"),
            ("Licença B", 60, 60, "Prova teórica (mínimo 70% de acertos) + Percurso prático sem infrações"),
            ("Licença C", 60, 90, "Prova teórica (mínimo 8 acertos de 10) + Teste prático sem infrações"),
            ("Licença D", 60, 90, "Prova teórica (mínimo 8 acertos de 10) + Teste prático sem infrações"),
            ("Licença E", 60, 90, "Prova teórica (mínimo 8 acertos de 10) + Teste prático sem infrações"),
            ("Licença Náutica", 45, 30, "Prova teórica (mínimo 6 acertos) + Navegação prática sem colisões"),
            ("Licença Aérea", 90, 60, "Prova teórica (mínimo 8 acertos) + Voo prático seguro e controlado")
        ]
        
        for curso in cursos_padrao:
            cursor.execute('''
                INSERT OR IGNORE INTO cursos (nome_curso, carga_horaria_teorica, carga_horaria_pratica, requisitos_aprovacao)
                VALUES (?, ?, ?, ?)
            ''', curso)
    
    # Métodos para Players
    def registrar_player(self, rg_game: str, nome_rp: str, telefone: str = None) -> bool:
        """Registra um novo jogador"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO players (rg_game, nome_rp, telefone)
                    VALUES (?, ?, ?)
                ''', (rg_game, nome_rp, telefone))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False
    
    def get_player(self, rg_game: str) -> Optional[Dict[str, Any]]:
        """Busca um jogador pelo RG"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM players WHERE rg_game = ?', (rg_game,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def atualizar_pontos_cnh(self, rg_game: str, pontos: int) -> bool:
        """Atualiza os pontos da CNH de um jogador"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE players 
                SET pontos_cnh = pontos_cnh + ?
                WHERE rg_game = ?
            ''', (pontos, rg_game))
            
            # Verificar se excedeu o limite de pontos
            cursor.execute('SELECT pontos_cnh FROM players WHERE rg_game = ?', (rg_game,))
            pontos_atuais = cursor.fetchone()[0]
            
            if pontos_atuais >= 30:  # Limite para revogação
                cursor.execute('''
                    UPDATE players 
                    SET cnh_status = 'revogada'
                    WHERE rg_game = ?
                ''', (rg_game,))
            elif pontos_atuais >= 20:  # Limite para suspensão
                cursor.execute('''
                    UPDATE players 
                    SET cnh_status = 'suspensa'
                    WHERE rg_game = ?
                ''', (rg_game,))
            
            conn.commit()
            return True
    
    def atualizar_status_cnh(self, rg_game: str, status: str) -> bool:
        """Atualiza o status da CNH de um jogador"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE players 
                SET cnh_status = ?
                WHERE rg_game = ?
            ''', (status, rg_game))
            conn.commit()
            return cursor.rowcount > 0
    
    # Métodos para Membros do Detran
    def adicionar_membro_detran(self, discord_id: str, nome_discord: str, cargo: str, rg_game: str = None) -> bool:
        """Adiciona um membro à equipe do Detran"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO membros_detran (discord_id, nome_discord, cargo, rg_game)
                    VALUES (?, ?, ?, ?)
                ''', (discord_id, nome_discord, cargo, rg_game))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False
    
    def get_membro_detran(self, discord_id: str) -> Optional[Dict[str, Any]]:
        """Busca um membro do Detran pelo Discord ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM membros_detran WHERE discord_id = ?', (discord_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def listar_membros_detran(self, cargo: str = None) -> List[Dict[str, Any]]:
        """Lista membros do Detran, opcionalmente filtrado por cargo"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            if cargo:
                cursor.execute('SELECT * FROM membros_detran WHERE cargo = ?', (cargo,))
            else:
                cursor.execute('SELECT * FROM membros_detran')
            return [dict(row) for row in cursor.fetchall()]
    
    def remover_membro_detran(self, discord_id: str) -> bool:
        """Remove um membro da equipe do Detran"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM membros_detran WHERE discord_id = ?', (discord_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    # Métodos para CNH
    def emitir_cnh(self, rg_game: str, categoria: str) -> str:
        """Emite uma nova CNH para um jogador"""
        numero_registro = f"CNH{rg_game}{categoria}{datetime.now().strftime('%Y%m%d')}"
        data_emissao = datetime.now().strftime('%Y-%m-%d')
        data_validade = (datetime.now() + timedelta(days=1825)).strftime('%Y-%m-%d')  # 5 anos
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO cnhs (jogador_id, numero_registro, data_emissao, data_validade, categoria)
                VALUES (?, ?, ?, ?, ?)
            ''', (rg_game, numero_registro, data_emissao, data_validade, categoria))
            
            # Ativar CNH do jogador
            cursor.execute('''
                UPDATE players 
                SET cnh_status = 'ativo'
                WHERE rg_game = ?
            ''', (rg_game,))
            
            conn.commit()
            return numero_registro
    
    def get_cnhs_jogador(self, rg_game: str) -> List[Dict[str, Any]]:
        """Busca todas as CNHs de um jogador"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM cnhs WHERE jogador_id = ?', (rg_game,))
            return [dict(row) for row in cursor.fetchall()]
    
    # Métodos para Veículos
    def registrar_veiculo(self, rg_game: str, placa: str, modelo: str, cor: str, ano: int, chassi: str) -> bool:
        """Registra um novo veículo"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO veiculos (proprietario_id, placa, modelo, cor, ano, chassi)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (rg_game, placa, modelo, cor, ano, chassi))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False
    
    def get_veiculo(self, placa: str) -> Optional[Dict[str, Any]]:
        """Busca um veículo pela placa"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM veiculos WHERE placa = ?', (placa,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def transferir_veiculo(self, placa: str, novo_proprietario: str) -> bool:
        """Transfere a propriedade de um veículo"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE veiculos 
                SET proprietario_id = ?
                WHERE placa = ?
            ''', (novo_proprietario, placa))
            conn.commit()
            return cursor.rowcount > 0
    
    def atualizar_status_veiculo(self, placa: str, status: str) -> bool:
        """Atualiza o status do CRLV de um veículo"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE veiculos 
                SET crlv_status = ?
                WHERE placa = ?
            ''', (status, placa))
            conn.commit()
            return cursor.rowcount > 0
    
    # Métodos para Multas
    def aplicar_multa(self, rg_game: str, tipo_infracao: str, valor: float, pontos: int, 
                     agente_id: str, placa_veiculo: str = None) -> int:
        """Aplica uma multa a um jogador"""
        data_ocorrencia = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        veiculo_id = None
        
        if placa_veiculo:
            veiculo = self.get_veiculo(placa_veiculo)
            if veiculo:
                veiculo_id = veiculo['id']
        
        # Verificar reincidência (mesma infração nos últimos 12 meses)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            data_limite = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            cursor.execute('''
                SELECT COUNT(*) FROM multas 
                WHERE jogador_id = ? AND tipo_infracao = ? AND data_ocorrencia >= ?
            ''', (rg_game, tipo_infracao, data_limite))
            
            reincidencia = cursor.fetchone()[0] > 0
            valor_final = valor * 2 if reincidencia else valor
            
            cursor.execute('''
                INSERT INTO multas (jogador_id, veiculo_id, agente_id, tipo_infracao, valor, pontos, data_ocorrencia)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (rg_game, veiculo_id, agente_id, tipo_infracao, valor_final, pontos, data_ocorrencia))
            
            multa_id = cursor.lastrowid
            conn.commit()
            
            # Atualizar pontos da CNH
            self.atualizar_pontos_cnh(rg_game, pontos)
            
            return multa_id
    
    def get_multas_jogador(self, rg_game: str, status: str = None) -> List[Dict[str, Any]]:
        """Busca multas de um jogador"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            if status:
                cursor.execute('SELECT * FROM multas WHERE jogador_id = ? AND status = ?', (rg_game, status))
            else:
                cursor.execute('SELECT * FROM multas WHERE jogador_id = ?', (rg_game,))
            return [dict(row) for row in cursor.fetchall()]
    
    def pagar_multa(self, multa_id: int) -> bool:
        """Registra o pagamento de uma multa"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE multas 
                SET status = 'paga'
                WHERE id = ?
            ''', (multa_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def recorrer_multa(self, multa_id: int) -> bool:
        """Marca uma multa como em recurso"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE multas 
                SET status = 'recorrida'
                WHERE id = ?
            ''', (multa_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    # Métodos para Cursos
    def listar_cursos(self) -> List[Dict[str, Any]]:
        """Lista todos os cursos disponíveis"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM cursos')
            return [dict(row) for row in cursor.fetchall()]
    
    def inscrever_em_curso(self, rg_game: str, nome_curso: str) -> bool:
        """Inscreve um jogador em um curso"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Buscar ID do curso
            cursor.execute('SELECT id FROM cursos WHERE nome_curso = ?', (nome_curso,))
            curso = cursor.fetchone()
            if not curso:
                return False
            
            curso_id = curso[0]
            data_inscricao = datetime.now().strftime('%Y-%m-%d')
            
            try:
                cursor.execute('''
                    INSERT INTO inscricoes_cursos (jogador_id, curso_id, data_inscricao)
                    VALUES (?, ?, ?)
                ''', (rg_game, curso_id, data_inscricao))
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False
    
    def atualizar_status_curso(self, rg_game: str, nome_curso: str, status: str) -> bool:
        """Atualiza o status de um jogador em um curso"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Buscar ID do curso
            cursor.execute('SELECT id FROM cursos WHERE nome_curso = ?', (nome_curso,))
            curso = cursor.fetchone()
            if not curso:
                return False
            
            curso_id = curso[0]
            
            cursor.execute('''
                UPDATE inscricoes_cursos
                SET status = ?
                WHERE jogador_id = ? AND curso_id = ?
            ''', (status, rg_game, curso_id))
            conn.commit()
            return cursor.rowcount > 0

    # Métodos de configuração
    def set_config(self, chave: str, valor: str) -> None:
        """Define ou atualiza uma configuração do bot"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO config (chave, valor)
                VALUES (?, ?)
                ON CONFLICT(chave) DO UPDATE SET valor = excluded.valor
            ''', (chave, valor))
            conn.commit()

    def get_config(self, chave: str) -> Optional[str]:
        """Recupera o valor de uma configuração"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT valor FROM config WHERE chave = ?', (chave,))
            row = cursor.fetchone()
            return row[0] if row else None

    # Métodos de permissões dinâmicas
    def add_permission(self, comando: str, role_id: int) -> None:
        """Adiciona permissão de um cargo a um comando"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO command_permissions (comando, role_id)
                VALUES (?, ?)
            ''', (comando, str(role_id)))
            conn.commit()

    def remove_permission(self, comando: str, role_id: int) -> None:
        """Remove a permissão de um cargo para um comando"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM command_permissions WHERE comando = ? AND role_id = ?', (comando, str(role_id)))
            conn.commit()

    def get_command_permissions(self, comando: str) -> List[int]:
        """Retorna lista de cargos autorizados para um comando"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT role_id FROM command_permissions WHERE comando = ?', (comando,))
            return [int(row[0]) for row in cursor.fetchall()]

