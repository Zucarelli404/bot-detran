import discord
from discord.ext import commands
from discord import app_commands
import os
from datetime import datetime
import sqlite3
from database import DetranDatabase
from config import *

# Configuração dos intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Inicialização do bot
bot = commands.Bot(command_prefix='!', intents=intents)
db = DetranDatabase()

def verificar_permissao(interaction: discord.Interaction, comando: str) -> bool:
    """Verifica se o usuário possui cargos necessários para o comando."""
    role_ids = [role.id for role in interaction.user.roles]

    # Gerência tem acesso total
    if ROLE_GERENCIA in role_ids:
        return True

    # Funcionários possuem acesso limitado
    if ROLE_FUNCIONARIOS in role_ids:
        return comando in PERMISSOES_FUNCIONARIOS

    return False

def criar_embed_erro(titulo: str, descricao: str) -> discord.Embed:
    """Cria um embed de erro"""
    embed = discord.Embed(
        title=f"❌ {titulo}",
        description=descricao,
        color=CORES["erro"]
    )
    return embed

def criar_embed_sucesso(titulo: str, descricao: str) -> discord.Embed:
    """Cria um embed de sucesso"""
    embed = discord.Embed(
        title=f"✅ {titulo}",
        description=descricao,
        color=CORES["sucesso"]
    )
    return embed

def criar_embed_info(titulo: str, descricao: str) -> discord.Embed:
    """Cria um embed informativo"""
    embed = discord.Embed(
        title=f"ℹ️ {titulo}",
        description=descricao,
        color=CORES["info"]
    )
    return embed


class PainelFuncionarios(discord.ui.View):
    """Painel com atalhos para os comandos principais."""
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Registrar Jogador", style=discord.ButtonStyle.primary)
    async def registrar_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "Use o comando /registrar_jogador para registrar um novo jogador.",
            ephemeral=True
        )

    @discord.ui.button(label="Emitir CNH", style=discord.ButtonStyle.secondary)
    async def cnh_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "Use o comando /cnh_emitir para emitir uma CNH.",
            ephemeral=True
        )

@bot.event
async def on_ready():
    print(f'{bot.user} está online!')
    try:
        synced = await bot.tree.sync()
        print(f'Sincronizados {len(synced)} comandos slash')
    except Exception as e:
        print(f'Erro ao sincronizar comandos: {e}')

    bot.add_view(PainelFuncionarios())
    canal = bot.get_channel(CANAL_PAINEL_FUNCIONARIOS)
    if canal:
        embed = discord.Embed(
            title="Painel de Controle",
            description="Utilize os botões abaixo para acessar funções rápidas.",
            color=CORES["info"]
        )
        await canal.send(embed=embed, view=PainelFuncionarios())


@bot.event
async def on_member_join(member: discord.Member):
    """Atribui cargo inicial aos novos membros."""
    role = member.guild.get_role(ROLE_INICIAL)
    if role:
        await member.add_roles(role)

# Comando para exibir o painel de controle
@bot.tree.command(name="painel", description="Exibe o painel de controle do Detran")
async def painel(interaction: discord.Interaction):
    if not verificar_permissao(interaction, "painel"):
        embed = criar_embed_erro("Sem Permissão", "Você não tem permissão para executar este comando.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    embed = discord.Embed(
        title="Painel de Controle",
        description="Utilize os botões abaixo para acessar funções rápidas.",
        color=CORES["info"]
    )
    await interaction.response.send_message(embed=embed, view=PainelFuncionarios(), ephemeral=True)

# Comandos de Registro e CNH
@bot.tree.command(name="registrar_jogador", description="Registra um novo jogador no sistema do Detran")
@app_commands.describe(
    rg_game="RG do jogador no jogo (ex: UTC58846)",
    nome_rp="Nome do jogador no roleplay",
    telefone="Telefone do jogador (opcional)"
)
async def registrar_jogador(interaction: discord.Interaction, rg_game: str, nome_rp: str, telefone: str = None):
    if not verificar_permissao(interaction, "registrar"):
        embed = criar_embed_erro("Sem Permissão", "Você não tem permissão para executar este comando.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    if db.registrar_player(rg_game, nome_rp, telefone):
        embed = criar_embed_sucesso(
            "Jogador Registrado",
            f"**RG:** {rg_game}\n**Nome:** {nome_rp}\n**Telefone:** {telefone or 'Não informado'}"
        )
    else:
        embed = criar_embed_erro("Erro no Registro", f"Jogador com RG {rg_game} já está registrado.")
    
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="registrar", description="Registre-se no servidor do Detran")
@app_commands.describe(nome="Seu nome no jogo", rg="Seu RG no jogo")
async def registrar(interaction: discord.Interaction, nome: str, rg: str):
    if interaction.channel_id != CANAL_REGISTRO:
        embed = criar_embed_erro("Canal incorreto", "Use este comando no canal de registro.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    guild = interaction.guild
    role_registrado = guild.get_role(ROLE_REGISTRADO)
    role_inicial = guild.get_role(ROLE_INICIAL)

    try:
        await interaction.user.edit(nick=f"{nome} | {rg}")
    except discord.Forbidden:
        pass

    if role_registrado:
        await interaction.user.add_roles(role_registrado)
    if role_inicial:
        await interaction.user.remove_roles(role_inicial)

    embed = criar_embed_sucesso("Registro concluído", f"Bem-vindo, {nome}!")
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="cnh_emitir", description="Emite uma nova CNH para um jogador")
@app_commands.describe(
    rg_game="RG do jogador no jogo",
    categoria="Categoria da CNH (A, B, C, D, E, Náutica, Aérea)"
)
@app_commands.choices(categoria=[
    app_commands.Choice(name="A - Motocicletas", value="A"),
    app_commands.Choice(name="B - Automóveis", value="B"),
    app_commands.Choice(name="C - Veículos Pesados", value="C"),
    app_commands.Choice(name="D - Veículos Pesados", value="D"),
    app_commands.Choice(name="E - Veículos Pesados", value="E"),
    app_commands.Choice(name="Náutica", value="Náutica"),
    app_commands.Choice(name="Aérea", value="Aérea")
])
async def cnh_emitir(interaction: discord.Interaction, rg_game: str, categoria: str):
    if not verificar_permissao(interaction, "cnh_emitir"):
        embed = criar_embed_erro("Sem Permissão", "Você não tem permissão para executar este comando.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    player = db.get_player(rg_game)
    if not player:
        embed = criar_embed_erro("Jogador Não Encontrado", f"Não foi encontrado jogador com RG {rg_game}.")
        await interaction.response.send_message(embed=embed)
        return
    
    numero_registro = db.emitir_cnh(rg_game, categoria)
    embed = criar_embed_sucesso(
        "CNH Emitida",
        f"**Jogador:** {player['nome_rp']}\n**RG:** {rg_game}\n**Categoria:** {categoria}\n**Número:** {numero_registro}"
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="cnh_consultar", description="Consulta o status e detalhes da CNH de um jogador")
@app_commands.describe(rg_game="RG do jogador no jogo")
async def cnh_consultar(interaction: discord.Interaction, rg_game: str):
    player = db.get_player(rg_game)
    if not player:
        embed = criar_embed_erro("Jogador Não Encontrado", f"Não foi encontrado jogador com RG {rg_game}.")
        await interaction.response.send_message(embed=embed)
        return
    
    cnhs = db.get_cnhs_jogador(rg_game)
    
    embed = discord.Embed(
        title=f"📋 Consulta CNH - {player['nome_rp']}",
        color=CORES["info"]
    )
    embed.add_field(name="RG", value=rg_game, inline=True)
    embed.add_field(name="Status CNH", value=player['cnh_status'].title(), inline=True)
    embed.add_field(name="Pontos", value=f"{player['pontos_cnh']}/30", inline=True)
    
    if cnhs:
        categorias = ", ".join([cnh['categoria'] for cnh in cnhs])
        embed.add_field(name="Categorias", value=categorias, inline=False)
        
        for cnh in cnhs:
            embed.add_field(
                name=f"CNH {cnh['categoria']}",
                value=f"**Número:** {cnh['numero_registro']}\n**Emissão:** {cnh['data_emissao']}\n**Validade:** {cnh['data_validade']}",
                inline=True
            )
    else:
        embed.add_field(name="CNHs", value="Nenhuma CNH emitida", inline=False)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="cnh_suspender", description="Suspende a CNH de um jogador")
@app_commands.describe(
    rg_game="RG do jogador no jogo",
    dias="Número de dias de suspensão"
)
async def cnh_suspender(interaction: discord.Interaction, rg_game: str, dias: int):
    if not verificar_permissao(interaction, "cnh_suspender"):
        embed = criar_embed_erro("Sem Permissão", "Você não tem permissão para executar este comando.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    player = db.get_player(rg_game)
    if not player:
        embed = criar_embed_erro("Jogador Não Encontrado", f"Não foi encontrado jogador com RG {rg_game}.")
        await interaction.response.send_message(embed=embed)
        return
    
    if db.atualizar_status_cnh(rg_game, "suspensa"):
        embed = criar_embed_sucesso(
            "CNH Suspensa",
            f"**Jogador:** {player['nome_rp']}\n**RG:** {rg_game}\n**Período:** {dias} dias"
        )
    else:
        embed = criar_embed_erro("Erro", "Não foi possível suspender a CNH.")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="cnh_cassar", description="Cassa a CNH de um jogador")
@app_commands.describe(rg_game="RG do jogador no jogo")
async def cnh_cassar(interaction: discord.Interaction, rg_game: str):
    if not verificar_permissao(interaction, "cnh_cassar"):
        embed = criar_embed_erro("Sem Permissão", "Você não tem permissão para executar este comando.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    player = db.get_player(rg_game)
    if not player:
        embed = criar_embed_erro("Jogador Não Encontrado", f"Não foi encontrado jogador com RG {rg_game}.")
        await interaction.response.send_message(embed=embed)
        return
    
    if db.atualizar_status_cnh(rg_game, "cassada"):
        embed = criar_embed_sucesso(
            "CNH Cassada",
            f"**Jogador:** {player['nome_rp']}\n**RG:** {rg_game}\n**Status:** Cassada definitivamente"
        )
    else:
        embed = criar_embed_erro("Erro", "Não foi possível cassar a CNH.")
    
    await interaction.response.send_message(embed=embed)

# Comandos de Membros do Detran
@bot.tree.command(name="membro_adicionar", description="Adiciona um membro à equipe do Detran")
@app_commands.describe(
    usuario="Usuário do Discord",
    cargo="Cargo no Detran",
    rg_game="RG do membro no jogo (opcional)"
)
@app_commands.choices(cargo=[
    app_commands.Choice(name="Diretor", value="Diretor"),
    app_commands.Choice(name="Instrutor", value="Instrutor"),
    app_commands.Choice(name="Agente", value="Agente")
])
async def membro_adicionar(interaction: discord.Interaction, usuario: discord.Member, cargo: str, rg_game: str = None):
    if not verificar_permissao(interaction, "membro_adicionar"):
        embed = criar_embed_erro("Sem Permissão", "Você não tem permissão para executar este comando.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    if db.adicionar_membro_detran(str(usuario.id), usuario.display_name, cargo, rg_game):
        embed = criar_embed_sucesso(
            "Membro Adicionado",
            f"**Usuário:** {usuario.mention}\n**Cargo:** {cargo}\n**RG:** {rg_game or 'Não informado'}"
        )
    else:
        embed = criar_embed_erro("Erro", f"Usuário {usuario.mention} já é membro do Detran.")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="membro_listar", description="Lista os membros do Detran")
@app_commands.describe(cargo="Filtrar por cargo (opcional)")
@app_commands.choices(cargo=[
    app_commands.Choice(name="Diretor", value="Diretor"),
    app_commands.Choice(name="Instrutor", value="Instrutor"),
    app_commands.Choice(name="Agente", value="Agente")
])
async def membro_listar(interaction: discord.Interaction, cargo: str = None):
    membros = db.listar_membros_detran(cargo)
    
    if not membros:
        embed = criar_embed_info("Lista de Membros", "Nenhum membro encontrado.")
        await interaction.response.send_message(embed=embed)
        return
    
    embed = discord.Embed(
        title=f"👥 Membros do Detran{f' - {cargo}' if cargo else ''}",
        color=CORES["detran"]
    )
    
    for membro in membros:
        try:
            user = bot.get_user(int(membro['discord_id']))
            nome = user.display_name if user else membro['nome_discord']
        except:
            nome = membro['nome_discord']
        
        embed.add_field(
            name=f"{membro['cargo']} - {nome}",
            value=f"**Discord ID:** {membro['discord_id']}\n**RG:** {membro['rg_game'] or 'Não informado'}",
            inline=True
        )
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="membro_remover", description="Remove um membro da equipe do Detran")
@app_commands.describe(usuario="Usuário do Discord")
async def membro_remover(interaction: discord.Interaction, usuario: discord.Member):
    if not verificar_permissao(interaction, "membro_remover"):
        embed = criar_embed_erro("Sem Permissão", "Você não tem permissão para executar este comando.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    if db.remover_membro_detran(str(usuario.id)):
        embed = criar_embed_sucesso("Membro Removido", f"Usuário {usuario.mention} foi removido da equipe do Detran.")
    else:
        embed = criar_embed_erro("Erro", f"Usuário {usuario.mention} não é membro do Detran.")
    
    await interaction.response.send_message(embed=embed)

# Comandos de Veículos
@bot.tree.command(name="veiculo_registrar", description="Registra um novo veículo")
@app_commands.describe(
    rg_game="RG do proprietário",
    placa="Placa do veículo",
    modelo="Modelo do veículo",
    cor="Cor do veículo",
    ano="Ano do veículo",
    chassi="Chassi do veículo"
)
async def veiculo_registrar(interaction: discord.Interaction, rg_game: str, placa: str, modelo: str, cor: str, ano: int, chassi: str):
    if not verificar_permissao(interaction, "veiculo_registrar"):
        embed = criar_embed_erro("Sem Permissão", "Você não tem permissão para executar este comando.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    player = db.get_player(rg_game)
    if not player:
        embed = criar_embed_erro("Proprietário Não Encontrado", f"Não foi encontrado jogador com RG {rg_game}.")
        await interaction.response.send_message(embed=embed)
        return
    
    if db.registrar_veiculo(rg_game, placa.upper(), modelo, cor, ano, chassi):
        embed = criar_embed_sucesso(
            "Veículo Registrado",
            f"**Proprietário:** {player['nome_rp']}\n**Placa:** {placa.upper()}\n**Modelo:** {modelo}\n**Cor:** {cor}\n**Ano:** {ano}"
        )
    else:
        embed = criar_embed_erro("Erro no Registro", f"Veículo com placa {placa.upper()} já está registrado.")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="veiculo_consultar", description="Consulta os detalhes de um veículo")
@app_commands.describe(placa="Placa do veículo")
async def veiculo_consultar(interaction: discord.Interaction, placa: str):
    veiculo = db.get_veiculo(placa.upper())
    if not veiculo:
        embed = criar_embed_erro("Veículo Não Encontrado", f"Não foi encontrado veículo com placa {placa.upper()}.")
        await interaction.response.send_message(embed=embed)
        return
    
    proprietario = db.get_player(veiculo['proprietario_id'])
    
    embed = discord.Embed(
        title=f"🚗 Consulta Veículo - {placa.upper()}",
        color=CORES["info"]
    )
    embed.add_field(name="Placa", value=veiculo['placa'], inline=True)
    embed.add_field(name="Modelo", value=veiculo['modelo'], inline=True)
    embed.add_field(name="Cor", value=veiculo['cor'], inline=True)
    embed.add_field(name="Ano", value=veiculo['ano'], inline=True)
    embed.add_field(name="Status CRLV", value=veiculo['crlv_status'].title(), inline=True)
    embed.add_field(name="Chassi", value=veiculo['chassi'], inline=True)
    
    if proprietario:
        embed.add_field(
            name="Proprietário",
            value=f"**Nome:** {proprietario['nome_rp']}\n**RG:** {proprietario['rg_game']}",
            inline=False
        )
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="veiculo_transferir", description="Transfere a propriedade de um veículo")
@app_commands.describe(
    placa="Placa do veículo",
    novo_rg="RG do novo proprietário"
)
async def veiculo_transferir(interaction: discord.Interaction, placa: str, novo_rg: str):
    if not verificar_permissao(interaction, "veiculo_transferir"):
        embed = criar_embed_erro("Sem Permissão", "Você não tem permissão para executar este comando.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    veiculo = db.get_veiculo(placa.upper())
    if not veiculo:
        embed = criar_embed_erro("Veículo Não Encontrado", f"Não foi encontrado veículo com placa {placa.upper()}.")
        await interaction.response.send_message(embed=embed)
        return
    
    novo_proprietario = db.get_player(novo_rg)
    if not novo_proprietario:
        embed = criar_embed_erro("Novo Proprietário Não Encontrado", f"Não foi encontrado jogador com RG {novo_rg}.")
        await interaction.response.send_message(embed=embed)
        return
    
    if db.transferir_veiculo(placa.upper(), novo_rg):
        embed = criar_embed_sucesso(
            "Transferência Realizada",
            f"**Veículo:** {placa.upper()}\n**Novo Proprietário:** {novo_proprietario['nome_rp']}\n**RG:** {novo_rg}"
        )
    else:
        embed = criar_embed_erro("Erro", "Não foi possível realizar a transferência.")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="veiculo_apreender", description="Marca um veículo como apreendido")
@app_commands.describe(placa="Placa do veículo")
async def veiculo_apreender(interaction: discord.Interaction, placa: str):
    if not verificar_permissao(interaction, "veiculo_apreender"):
        embed = criar_embed_erro("Sem Permissão", "Você não tem permissão para executar este comando.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    veiculo = db.get_veiculo(placa.upper())
    if not veiculo:
        embed = criar_embed_erro("Veículo Não Encontrado", f"Não foi encontrado veículo com placa {placa.upper()}.")
        await interaction.response.send_message(embed=embed)
        return
    
    if db.atualizar_status_veiculo(placa.upper(), "apreendido"):
        embed = criar_embed_sucesso(
            "Veículo Apreendido",
            f"**Placa:** {placa.upper()}\n**Status:** Apreendido\n**Agente:** {interaction.user.mention}"
        )
    else:
        embed = criar_embed_erro("Erro", "Não foi possível apreender o veículo.")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="veiculo_liberar", description="Libera um veículo apreendido")
@app_commands.describe(placa="Placa do veículo")
async def veiculo_liberar(interaction: discord.Interaction, placa: str):
    if not verificar_permissao(interaction, "veiculo_liberar"):
        embed = criar_embed_erro("Sem Permissão", "Você não tem permissão para executar este comando.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    veiculo = db.get_veiculo(placa.upper())
    if not veiculo:
        embed = criar_embed_erro("Veículo Não Encontrado", f"Não foi encontrado veículo com placa {placa.upper()}.")
        await interaction.response.send_message(embed=embed)
        return
    
    if db.atualizar_status_veiculo(placa.upper(), "ativo"):
        embed = criar_embed_sucesso(
            "Veículo Liberado",
            f"**Placa:** {placa.upper()}\n**Status:** Liberado\n**Agente:** {interaction.user.mention}"
        )
    else:
        embed = criar_embed_erro("Erro", "Não foi possível liberar o veículo.")
    
    await interaction.response.send_message(embed=embed)

# Comandos de Multas e Infrações
@bot.tree.command(name="multar", description="Aplica uma multa a um jogador")
@app_commands.describe(
    rg_game="RG do jogador",
    tipo_infracao="Tipo de infração",
    placa_veiculo="Placa do veículo (opcional)"
)
@app_commands.choices(tipo_infracao=[
    app_commands.Choice(name="Excesso de velocidade (leve)", value="excesso_velocidade_leve"),
    app_commands.Choice(name="Excesso de velocidade (médio)", value="excesso_velocidade_medio"),
    app_commands.Choice(name="Excesso de velocidade (grave)", value="excesso_velocidade_grave"),
    app_commands.Choice(name="Condução sem CNH", value="conducao_sem_cnh"),
    app_commands.Choice(name="Documentação irregular", value="documentacao_irregular"),
    app_commands.Choice(name="Recusa ao bafômetro", value="recusa_bafometro"),
    app_commands.Choice(name="Direção perigosa", value="direcao_perigosa"),
    app_commands.Choice(name="Estacionamento proibido", value="estacionamento_proibido"),
    app_commands.Choice(name="Sem capacete", value="sem_capacete"),
    app_commands.Choice(name="Transporte irregular", value="transporte_irregular")
])
async def multar(interaction: discord.Interaction, rg_game: str, tipo_infracao: str, placa_veiculo: str = None):
    if not verificar_permissao(interaction, "multar"):
        embed = criar_embed_erro("Sem Permissão", "Você não tem permissão para executar este comando.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    player = db.get_player(rg_game)
    if not player:
        embed = criar_embed_erro("Jogador Não Encontrado", f"Não foi encontrado jogador com RG {rg_game}.")
        await interaction.response.send_message(embed=embed)
        return
    
    if placa_veiculo:
        veiculo = db.get_veiculo(placa_veiculo.upper())
        if not veiculo:
            embed = criar_embed_erro("Veículo Não Encontrado", f"Não foi encontrado veículo com placa {placa_veiculo.upper()}.")
            await interaction.response.send_message(embed=embed)
            return
        placa_veiculo = placa_veiculo.upper()
    
    infracao = TABELA_INFRACOES[tipo_infracao]
    multa_id = db.aplicar_multa(
        rg_game, 
        infracao['descricao'], 
        infracao['valor'], 
        infracao['pontos'], 
        str(interaction.user.id), 
        placa_veiculo
    )
    
    # Verificar se houve reincidência
    player_atualizado = db.get_player(rg_game)
    valor_final = infracao['valor']
    
    # Verificar se foi multa em dobro por reincidência
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT valor FROM multas WHERE id = ?', (multa_id,))
        valor_aplicado = cursor.fetchone()[0]
        reincidencia = valor_aplicado > infracao['valor']
    
    embed = discord.Embed(
        title="🚨 Multa Aplicada",
        color=CORES["aviso"]
    )
    embed.add_field(name="Jogador", value=f"{player['nome_rp']} ({rg_game})", inline=True)
    embed.add_field(name="Infração", value=infracao['descricao'], inline=False)
    embed.add_field(name="Valor", value=f"R$ {valor_aplicado:.2f}", inline=True)
    embed.add_field(name="Pontos", value=infracao['pontos'], inline=True)
    embed.add_field(name="Agente", value=interaction.user.mention, inline=True)
    
    if placa_veiculo:
        embed.add_field(name="Veículo", value=placa_veiculo, inline=True)
    
    if reincidencia:
        embed.add_field(name="⚠️ Reincidência", value="Multa aplicada em dobro", inline=False)
    
    embed.add_field(name="Pontos Atuais", value=f"{player_atualizado['pontos_cnh']}/30", inline=True)
    embed.add_field(name="Status CNH", value=player_atualizado['cnh_status'].title(), inline=True)
    embed.add_field(name="ID da Multa", value=multa_id, inline=True)
    
    # Avisos sobre status da CNH
    if player_atualizado['cnh_status'] == 'suspensa':
        embed.add_field(name="🚫 CNH Suspensa", value="CNH suspensa automaticamente por excesso de pontos", inline=False)
    elif player_atualizado['cnh_status'] == 'revogada':
        embed.add_field(name="❌ CNH Revogada", value="CNH revogada automaticamente por excesso de pontos", inline=False)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="multa_consultar", description="Lista as multas de um jogador")
@app_commands.describe(
    rg_game="RG do jogador",
    status="Status das multas (opcional)"
)
@app_commands.choices(status=[
    app_commands.Choice(name="Pendentes", value="pendente"),
    app_commands.Choice(name="Pagas", value="paga"),
    app_commands.Choice(name="Em recurso", value="recorrida")
])
async def multa_consultar(interaction: discord.Interaction, rg_game: str, status: str = None):
    player = db.get_player(rg_game)
    if not player:
        embed = criar_embed_erro("Jogador Não Encontrado", f"Não foi encontrado jogador com RG {rg_game}.")
        await interaction.response.send_message(embed=embed)
        return
    
    multas = db.get_multas_jogador(rg_game, status)
    
    if not multas:
        status_texto = f" ({status})" if status else ""
        embed = criar_embed_info("Consulta de Multas", f"Nenhuma multa encontrada para {player['nome_rp']}{status_texto}.")
        await interaction.response.send_message(embed=embed)
        return
    
    embed = discord.Embed(
        title=f"📋 Multas - {player['nome_rp']}",
        color=CORES["info"]
    )
    
    total_pendente = sum(multa['valor'] for multa in multas if multa['status'] == 'pendente')
    
    embed.add_field(name="RG", value=rg_game, inline=True)
    embed.add_field(name="Total de Multas", value=len(multas), inline=True)
    embed.add_field(name="Total Pendente", value=f"R$ {total_pendente:.2f}", inline=True)
    
    for i, multa in enumerate(multas[:10]):  # Limitar a 10 multas para não exceder limite do embed
        data = multa['data_ocorrencia'].split(' ')[0]  # Apenas a data
        status_emoji = {"pendente": "🔴", "paga": "🟢", "recorrida": "🟡"}
        
        embed.add_field(
            name=f"{status_emoji.get(multa['status'], '⚪')} Multa #{multa['id']}",
            value=f"**Infração:** {multa['tipo_infracao']}\n**Valor:** R$ {multa['valor']:.2f}\n**Data:** {data}",
            inline=True
        )
    
    if len(multas) > 10:
        embed.add_field(name="⚠️ Aviso", value=f"Mostrando apenas 10 de {len(multas)} multas.", inline=False)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="multa_pagar", description="Registra o pagamento de uma multa")
@app_commands.describe(multa_id="ID da multa")
async def multa_pagar(interaction: discord.Interaction, multa_id: int):
    if not verificar_permissao(interaction, "multa_pagar"):
        embed = criar_embed_erro("Sem Permissão", "Você não tem permissão para executar este comando.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    if db.pagar_multa(multa_id):
        embed = criar_embed_sucesso(
            "Multa Paga",
            f"**ID da Multa:** {multa_id}\n**Processado por:** {interaction.user.mention}"
        )
    else:
        embed = criar_embed_erro("Erro", f"Não foi possível processar o pagamento da multa #{multa_id}.")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="multa_recorrer", description="Marca uma multa como em recurso")
@app_commands.describe(multa_id="ID da multa")
async def multa_recorrer(interaction: discord.Interaction, multa_id: int):
    if not verificar_permissao(interaction, "multa_recorrer"):
        embed = criar_embed_erro("Sem Permissão", "Você não tem permissão para executar este comando.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    if db.recorrer_multa(multa_id):
        embed = criar_embed_sucesso(
            "Recurso Registrado",
            f"**ID da Multa:** {multa_id}\n**Status:** Em recurso\n**Processado por:** {interaction.user.mention}"
        )
    else:
        embed = criar_embed_erro("Erro", f"Não foi possível processar o recurso da multa #{multa_id}.")
    
    await interaction.response.send_message(embed=embed)

# Comandos de Cursos
@bot.tree.command(name="curso_listar", description="Lista todos os cursos disponíveis")
async def curso_listar(interaction: discord.Interaction):
    cursos = db.listar_cursos()
    
    embed = discord.Embed(
        title="📚 Cursos Disponíveis - Detran-SP",
        color=CORES["detran"]
    )
    
    for curso in cursos:
        embed.add_field(
            name=curso['nome_curso'],
            value=f"**Teoria:** {curso['carga_horaria_teorica']}min\n**Prática:** {curso['carga_horaria_pratica']}min\n**Requisitos:** {curso['requisitos_aprovacao']}",
            inline=True
        )
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="curso_inscrever", description="Inscreve um jogador em um curso")
@app_commands.describe(
    rg_game="RG do jogador",
    nome_curso="Nome do curso"
)
@app_commands.choices(nome_curso=[
    app_commands.Choice(name="Licença A", value="Licença A"),
    app_commands.Choice(name="Licença B", value="Licença B"),
    app_commands.Choice(name="Licença C", value="Licença C"),
    app_commands.Choice(name="Licença D", value="Licença D"),
    app_commands.Choice(name="Licença E", value="Licença E"),
    app_commands.Choice(name="Licença Náutica", value="Licença Náutica"),
    app_commands.Choice(name="Licença Aérea", value="Licença Aérea")
])
async def curso_inscrever(interaction: discord.Interaction, rg_game: str, nome_curso: str):
    if not verificar_permissao(interaction, "curso_inscrever"):
        embed = criar_embed_erro("Sem Permissão", "Você não tem permissão para executar este comando.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    player = db.get_player(rg_game)
    if not player:
        embed = criar_embed_erro("Jogador Não Encontrado", f"Não foi encontrado jogador com RG {rg_game}.")
        await interaction.response.send_message(embed=embed)
        return
    
    if db.inscrever_em_curso(rg_game, nome_curso):
        embed = criar_embed_sucesso(
            "Inscrição Realizada",
            f"**Jogador:** {player['nome_rp']}\n**RG:** {rg_game}\n**Curso:** {nome_curso}\n**Instrutor:** {interaction.user.mention}"
        )
    else:
        embed = criar_embed_erro("Erro na Inscrição", "Não foi possível realizar a inscrição. Verifique se o jogador já está inscrito neste curso.")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="curso_aprovar", description="Marca um jogador como aprovado em um curso")
@app_commands.describe(
    rg_game="RG do jogador",
    nome_curso="Nome do curso"
)
@app_commands.choices(nome_curso=[
    app_commands.Choice(name="Licença A", value="Licença A"),
    app_commands.Choice(name="Licença B", value="Licença B"),
    app_commands.Choice(name="Licença C", value="Licença C"),
    app_commands.Choice(name="Licença D", value="Licença D"),
    app_commands.Choice(name="Licença E", value="Licença E"),
    app_commands.Choice(name="Licença Náutica", value="Licença Náutica"),
    app_commands.Choice(name="Licença Aérea", value="Licença Aérea")
])
async def curso_aprovar(interaction: discord.Interaction, rg_game: str, nome_curso: str):
    if not verificar_permissao(interaction, "curso_aprovar"):
        embed = criar_embed_erro("Sem Permissão", "Você não tem permissão para executar este comando.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    player = db.get_player(rg_game)
    if not player:
        embed = criar_embed_erro("Jogador Não Encontrado", f"Não foi encontrado jogador com RG {rg_game}.")
        await interaction.response.send_message(embed=embed)
        return
    
    if db.atualizar_status_curso(rg_game, nome_curso, "aprovado"):
        embed = criar_embed_sucesso(
            "Aprovação Registrada",
            f"**Jogador:** {player['nome_rp']}\n**RG:** {rg_game}\n**Curso:** {nome_curso}\n**Status:** Aprovado\n**Instrutor:** {interaction.user.mention}"
        )
        embed.add_field(name="📋 Próximo Passo", value="Use `/cnh_emitir` para emitir a CNH correspondente.", inline=False)
    else:
        embed = criar_embed_erro("Erro", "Não foi possível registrar a aprovação. Verifique se o jogador está inscrito neste curso.")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="curso_reprovar", description="Marca um jogador como reprovado em um curso")
@app_commands.describe(
    rg_game="RG do jogador",
    nome_curso="Nome do curso"
)
@app_commands.choices(nome_curso=[
    app_commands.Choice(name="Licença A", value="Licença A"),
    app_commands.Choice(name="Licença B", value="Licença B"),
    app_commands.Choice(name="Licença C", value="Licença C"),
    app_commands.Choice(name="Licença D", value="Licença D"),
    app_commands.Choice(name="Licença E", value="Licença E"),
    app_commands.Choice(name="Licença Náutica", value="Licença Náutica"),
    app_commands.Choice(name="Licença Aérea", value="Licença Aérea")
])
async def curso_reprovar(interaction: discord.Interaction, rg_game: str, nome_curso: str):
    if not verificar_permissao(interaction, "curso_reprovar"):
        embed = criar_embed_erro("Sem Permissão", "Você não tem permissão para executar este comando.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    player = db.get_player(rg_game)
    if not player:
        embed = criar_embed_erro("Jogador Não Encontrado", f"Não foi encontrado jogador com RG {rg_game}.")
        await interaction.response.send_message(embed=embed)
        return
    
    if db.atualizar_status_curso(rg_game, nome_curso, "reprovado"):
        embed = discord.Embed(
            title="❌ Reprovação Registrada",
            color=CORES["erro"]
        )
        embed.add_field(name="Jogador", value=f"{player['nome_rp']} ({rg_game})", inline=True)
        embed.add_field(name="Curso", value=nome_curso, inline=True)
        embed.add_field(name="Instrutor", value=interaction.user.mention, inline=True)
        embed.add_field(name="📋 Próximo Passo", value="O jogador pode se inscrever novamente após 24h.", inline=False)
    else:
        embed = criar_embed_erro("Erro", "Não foi possível registrar a reprovação. Verifique se o jogador está inscrito neste curso.")
    
    await interaction.response.send_message(embed=embed)

# Comandos de Consulta Geral
@bot.tree.command(name="taxas", description="Exibe a tabela de taxas de serviços")
async def taxas(interaction: discord.Interaction):
    embed = discord.Embed(
        title="💰 Tabela Oficial de Taxas - Detran-SP",
        color=CORES["detran"]
    )
    
    for codigo, taxa in TABELA_TAXAS.items():
        embed.add_field(
            name=taxa['descricao'],
            value=f"R$ {taxa['valor']:.2f}",
            inline=True
        )
    
    embed.set_footer(text="Valores em dinheiro virtual do servidor")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="infracoes", description="Exibe a tabela de infrações e multas")
async def infracoes(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🚨 Tabela Oficial de Infrações e Multas",
        color=CORES["aviso"]
    )
    
    for codigo, infracao in TABELA_INFRACOES.items():
        embed.add_field(
            name=infracao['descricao'],
            value=f"**Valor:** R$ {infracao['valor']:.2f}\n**Pontos:** {infracao['pontos']}",
            inline=True
        )
    
    embed.add_field(
        name="⚠️ Observações",
        value="• Reincidência em 12 meses: multa em dobro\n• 20 pontos: CNH suspensa\n• 30 pontos: CNH revogada",
        inline=False
    )
    embed.set_footer(text="Valores em dinheiro virtual do servidor")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="pop", description="Exibe um resumo do Protocolo Operacional Padrão")
async def pop(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📋 Protocolo Operacional Padrão (POP)",
        description=POP_RESUMO,
        color=CORES["detran"]
    )
    embed.set_footer(text="Detran-SP - Cidade Salve RP")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="regulamento", description="Exibe um resumo do Regulamento Interno")
async def regulamento(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📜 Regulamento Interno do Detran-SP",
        description=REGULAMENTO_RESUMO,
        color=CORES["detran"]
    )
    embed.set_footer(text="Detran-SP - Cidade Salve RP")
    await interaction.response.send_message(embed=embed)

# Comandos de Operações e Relatórios
@bot.tree.command(name="relatorio_multas_agente", description="Gera relatório de multas aplicadas por um agente")
@app_commands.describe(agente="Usuário do Discord (agente)")
async def relatorio_multas_agente(interaction: discord.Interaction, agente: discord.Member):
    if not verificar_permissao(interaction, "relatorios"):
        embed = criar_embed_erro("Sem Permissão", "Você não tem permissão para executar este comando.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    with sqlite3.connect(db.db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) as total, SUM(valor) as valor_total
            FROM multas 
            WHERE agente_id = ?
        ''', (str(agente.id),))
        
        resultado = cursor.fetchone()
        total_multas = resultado['total']
        valor_total = resultado['valor_total'] or 0
        
        cursor.execute('''
            SELECT tipo_infracao, COUNT(*) as quantidade
            FROM multas 
            WHERE agente_id = ?
            GROUP BY tipo_infracao
            ORDER BY quantidade DESC
        ''', (str(agente.id),))
        
        infracoes_por_tipo = cursor.fetchall()
    
    embed = discord.Embed(
        title=f"📊 Relatório de Multas - {agente.display_name}",
        color=CORES["info"]
    )
    
    embed.add_field(name="Total de Multas", value=total_multas, inline=True)
    embed.add_field(name="Valor Total", value=f"R$ {valor_total:.2f}", inline=True)
    embed.add_field(name="Agente", value=agente.mention, inline=True)
    
    if infracoes_por_tipo:
        top_infracoes = "\n".join([f"• {row['tipo_infracao']}: {row['quantidade']}" for row in infracoes_por_tipo[:5]])
        embed.add_field(name="Top 5 Infrações", value=top_infracoes, inline=False)
    
    embed.set_footer(text=f"Relatório gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="relatorio_cnhs_suspensas", description="Lista todas as CNHs suspensas")
async def relatorio_cnhs_suspensas(interaction: discord.Interaction):
    if not verificar_permissao(interaction, "relatorios"):
        embed = criar_embed_erro("Sem Permissão", "Você não tem permissão para executar este comando.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    with sqlite3.connect(db.db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT rg_game, nome_rp, cnh_status, pontos_cnh
            FROM players 
            WHERE cnh_status IN ('suspensa', 'revogada', 'cassada')
            ORDER BY pontos_cnh DESC
        ''')
        
        cnhs_problematicas = cursor.fetchall()
    
    if not cnhs_problematicas:
        embed = criar_embed_info("CNHs Suspensas", "Nenhuma CNH suspensa, revogada ou cassada encontrada.")
        await interaction.response.send_message(embed=embed)
        return
    
    embed = discord.Embed(
        title="🚫 Relatório de CNHs com Restrições",
        color=CORES["aviso"]
    )
    
    for cnh in cnhs_problematicas[:15]:  # Limitar a 15 para não exceder limite
        status_emoji = {"suspensa": "🟡", "revogada": "🔴", "cassada": "❌"}
        embed.add_field(
            name=f"{status_emoji.get(cnh['cnh_status'], '⚪')} {cnh['nome_rp']}",
            value=f"**RG:** {cnh['rg_game']}\n**Status:** {cnh['cnh_status'].title()}\n**Pontos:** {cnh['pontos_cnh']}",
            inline=True
        )
    
    if len(cnhs_problematicas) > 15:
        embed.add_field(name="⚠️ Aviso", value=f"Mostrando apenas 15 de {len(cnhs_problematicas)} CNHs.", inline=False)
    
    embed.set_footer(text=f"Relatório gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    await interaction.response.send_message(embed=embed)

# Comando para executar o bot
if __name__ == "__main__":
    # Verificar se o token foi definido
    if DISCORD_TOKEN == "SEU_TOKEN_AQUI":
        print("❌ ERRO: Token do Discord não configurado!")
        print("Edite o arquivo config.py e defina seu token do Discord.")
    else:
        bot.run(DISCORD_TOKEN)

