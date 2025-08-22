import sqlite3
import os.path
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

DB_PATH = os.path.join(os.path.dirname(__file__), "detran.db")

class DetranDatabase:
    def __init__(self, db_path: str = DB_PATH):
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
                    FOREIGN KEY (veiculo_id) REFERENCES veiculos(id)
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

            # Tabela de tickets de suporte
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tickets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    autor_id TEXT NOT NULL,
                    descricao TEXT NOT NULL,
                    status TEXT DEFAULT 'aberto',
                    data_criacao TEXT NOT NULL
                )
            ''')

            # Tabela de sugestões
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sugestoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    autor_id TEXT NOT NULL,
                    sugestao TEXT NOT NULL,
                    data_criacao TEXT NOT NULL
                )
            ''')
            
            conn.commit()

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
    
    # Métodos para CNH
    def emitir_cnh(self, rg_game: str, categoria: str) -> str:
        """Emite uma nova CNH para um jogador"""
        numero_registro = f"CNH{rg_game}{categoria}{datetime.now().strftime('%Y%m%d')}"
        data_emissao = datetime.now().strftime('%Y-%m-%d')
        data_validade = (datetime.now() + timedelta(days=15)).strftime('%Y-%m-%d')  # 15 dias
        
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
    

    # Métodos para Tickets de Suporte
    def criar_ticket(self, autor_id: str, descricao: str) -> int:
        """Cria um novo ticket de suporte"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            data_criacao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
                INSERT INTO tickets (autor_id, descricao, data_criacao)
                VALUES (?, ?, ?)
            ''', (autor_id, descricao, data_criacao))
            conn.commit()
            return cursor.lastrowid

    def listar_tickets(self, status: str = None) -> List[Dict[str, Any]]:
        """Lista tickets de suporte, opcionalmente filtrados por status"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            if status:
                cursor.execute('SELECT * FROM tickets WHERE status = ?', (status,))
            else:
                cursor.execute('SELECT * FROM tickets')
            return [dict(row) for row in cursor.fetchall()]

    def fechar_ticket(self, ticket_id: int) -> bool:
        """Fecha um ticket de suporte"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE tickets
                SET status = 'fechado'
                WHERE id = ? AND status != 'fechado'
            ''', (ticket_id,))
            conn.commit()
            return cursor.rowcount > 0

    # Métodos para Sugestões
    def criar_sugestao(self, autor_id: str, sugestao: str) -> int:
        """Registra uma nova sugestão"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            data_criacao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
                INSERT INTO sugestoes (autor_id, sugestao, data_criacao)
                VALUES (?, ?, ?)
            ''', (autor_id, sugestao, data_criacao))
            conn.commit()
            return cursor.lastrowid

