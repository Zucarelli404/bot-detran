import discord
from discord.ext import commands
from discord import app_commands
import os
from datetime import datetime
import sqlite3
from database import DetranDatabase, DB_PATH
from config import *
from utils import verificar_permissao, criar_embed, enviar_log

# Configuração dos intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Inicialização do bot
bot = commands.Bot(command_prefix='!', intents=intents)
db = DetranDatabase(db_path=DB_PATH)


class ComandoModal(discord.ui.Modal):
    """Modal genérico apresentado ao pressionar um botão do painel."""

    def __init__(self, titulo: str):
        super().__init__(title=titulo)
        self.informacoes = discord.ui.TextInput(
            label="Informações",
            style=discord.TextStyle.paragraph,
            placeholder="Insira os dados necessários",
            required=False,
        )
        self.add_item(self.informacoes)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"Modal '{self.title}' enviado.",
            ephemeral=True,
        )


class PainelFuncionarios(discord.ui.View):
    """Painel com atalhos para os comandos principais."""
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Registrar Jogador",
        style=discord.ButtonStyle.primary,
        custom_id="painel_registrar_jogador"
    )
    async def registrar_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ComandoModal("Registrar Jogador"))

    @discord.ui.button(
        label="Emitir CNH",
        style=discord.ButtonStyle.secondary,
        custom_id="painel_emitir_cnh"
    )
    async def cnh_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ComandoModal("Emitir CNH"))

    @discord.ui.button(
        label="Consultar CNH",
        style=discord.ButtonStyle.secondary,
        custom_id="painel_consultar_cnh"
    )
    async def cnh_consultar_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ComandoModal("Consultar CNH"))

    @discord.ui.button(
        label="Registrar Veículo",
        style=discord.ButtonStyle.success,
        custom_id="painel_registrar_veiculo"
    )
    async def veiculo_registrar_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ComandoModal("Registrar Veículo"))

    @discord.ui.button(
        label="Aplicar Multa",
        style=discord.ButtonStyle.danger,
        custom_id="painel_aplicar_multa"
    )
    async def multar_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ComandoModal("Aplicar Multa"))

    @discord.ui.button(
        label="Abrir Ticket",
        style=discord.ButtonStyle.secondary,
        custom_id="painel_ticket",
        row=1
    )
    async def ticket_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ComandoModal("Abrir Ticket"))


class RegistroModal(discord.ui.Modal, title="Registro"):
    nome = discord.ui.TextInput(label="Nome no jogo")
    rg = discord.ui.TextInput(label="RG no jogo")

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        role_registrado = guild.get_role(ROLE_REGISTRADO)
        role_inicial = guild.get_role(ROLE_INICIAL)
        try:
            await interaction.user.edit(nick=f"{self.nome.value} | {self.rg.value}")
        except discord.Forbidden:
            pass
        if role_registrado:
            await interaction.user.add_roles(role_registrado)
        if role_inicial:
            await interaction.user.remove_roles(role_inicial)
        embed = criar_embed("sucesso", "Registro concluído", f"Bem-vindo, {self.nome.value}!")
        await interaction.response.send_message(embed=embed, ephemeral=True)


class PainelRegistro(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Registrar-se", style=discord.ButtonStyle.primary, custom_id="painel_registro")
    async def registrar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(RegistroModal())


class TicketView(discord.ui.View):
    def __init__(self, ticket_id: int):
        super().__init__(timeout=None)
        self.ticket_id = ticket_id

    @discord.ui.button(label="Fechar Ticket", style=discord.ButtonStyle.danger, custom_id="ticket_fechar_view")
    async def fechar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if db.fechar_ticket(self.ticket_id):
            await interaction.response.send_message("Ticket fechado.", ephemeral=True)
            await interaction.channel.delete()
        else:
            await interaction.response.send_message("Não foi possível fechar o ticket.", ephemeral=True)


class PainelTickets(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Abrir Ticket", style=discord.ButtonStyle.primary, custom_id="painel_ticket_abrir")
    async def abrir_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        ticket_id = db.criar_ticket(str(interaction.user.id), "Ticket aberto via painel")
        guild = interaction.guild
        categoria = guild.get_channel(CATEGORIA_TICKETS)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }
        func = guild.get_role(ROLE_FUNCIONARIOS)
        ger = guild.get_role(ROLE_GERENCIA)
        if func:
            overwrites[func] = discord.PermissionOverwrite(view_channel=True, send_messages=True)
        if ger:
            overwrites[ger] = discord.PermissionOverwrite(view_channel=True, send_messages=True)
        canal = await guild.create_text_channel(f"ticket-{ticket_id}", category=categoria, overwrites=overwrites)
        embed_ticket = discord.Embed(
            title=f"Ticket #{ticket_id}",
            description=f"{interaction.user.mention}, descreva seu problema.",
            color=CORES["info"]
        )
        await canal.send(embed=embed_ticket, view=TicketView(ticket_id))
        embed = criar_embed("sucesso", "Ticket Criado", f"Seu ticket foi aberto: {canal.mention}")
        await interaction.response.send_message(embed=embed, ephemeral=True)




class SugestaoModal(discord.ui.Modal, title="Enviar Sugestão"):
    sugestao = discord.ui.TextInput(label="Sua sugestão", style=discord.TextStyle.long)

    async def on_submit(self, interaction: discord.Interaction):
        sugestao_id = db.criar_sugestao(str(interaction.user.id), self.sugestao.value)
        canal = bot.get_channel(CANAL_SUGESTOES)
        embed = discord.Embed(
            title=f"Sugestão #{sugestao_id}",
            description=self.sugestao.value,
            color=CORES["info"]
        )
        embed.set_footer(text=f"Enviado por {interaction.user}")
        if canal:
            mensagem = await canal.send(embed=embed)
            await mensagem.add_reaction("✅")
            await mensagem.add_reaction("❌")
        await interaction.response.send_message(
            embed=criar_embed("sucesso", "Sugestão enviada", f"Sugestão #{sugestao_id} registrada."),
            ephemeral=True
        )


class PainelSugestao(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Enviar Sugestão", style=discord.ButtonStyle.primary, custom_id="painel_sugestao_enviar")
    async def enviar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SugestaoModal())

@bot.event
async def on_ready():
    print(f'{bot.user} está online!')
    try:
        synced = await bot.tree.sync()
        print(f'Sincronizados {len(synced)} comandos slash')
    except Exception as e:
        print(f'Erro ao sincronizar comandos: {e}')

    await enviar_log(bot, "Bot iniciado e online.")

    bot.add_view(PainelFuncionarios())
    bot.add_view(PainelRegistro())
    bot.add_view(PainelTickets())
    bot.add_view(PainelSugestao())

    canal = bot.get_channel(CANAL_PAINEL_FUNCIONARIOS)
    if canal:
        embed = discord.Embed(
            title="Painel de Controle",
            description="Utilize os botões abaixo para acessar funções rápidas.",
            color=CORES["info"]
        )
        embed.set_footer(text="Detran-SP Bot")
        embed.set_thumbnail(url=bot.user.display_avatar.url)
        await canal.send(embed=embed, view=PainelFuncionarios())

    canal_registro = bot.get_channel(CANAL_REGISTRO)
    if canal_registro:
        embed = discord.Embed(
            title="Registro",
            description="Clique no botão para se registrar.",
            color=CORES["info"]
        )
        await canal_registro.send(embed=embed, view=PainelRegistro())

    canal_ticket = bot.get_channel(CANAL_TICKETS)
    if canal_ticket:
        embed = discord.Embed(
            title="Suporte",
            description="Clique no botão para abrir um ticket.",
            color=CORES["info"]
        )
        await canal_ticket.send(embed=embed, view=PainelTickets())


    canal_sugestoes = bot.get_channel(CANAL_SUGESTOES)
    if canal_sugestoes:
        embed = discord.Embed(
            title="Sugestões",
            description="Envie suas sugestões pelo botão abaixo.",
            color=CORES["info"]
        )
        await canal_sugestoes.send(embed=embed, view=PainelSugestao())


@bot.event
async def on_app_command_completion(interaction: discord.Interaction, command: app_commands.Command):
    await enviar_log(bot, f"Comando /{command.name} executado por {interaction.user} ({interaction.user.id})")


@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    await enviar_log(bot, (
        f"Erro ao executar /{interaction.command.name} por {interaction.user} ({interaction.user.id}): {error}"
    ))
    embed = criar_embed("erro", "Erro", "Ocorreu um erro ao executar o comando.")
    try:
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except Exception:
        pass


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
        embed = criar_embed("erro", "Sem Permissão", "Você não tem permissão para executar este comando.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    embed = discord.Embed(
        title="Painel de Controle",
        description="Utilize os botões abaixo para acessar funções rápidas.",
        color=CORES["info"]
    )
    embed.set_footer(text="Detran-SP Bot")
    embed.set_thumbnail(url=bot.user.display_avatar.url)
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
        embed = criar_embed("erro", "Sem Permissão", "Você não tem permissão para executar este comando.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    if db.registrar_player(rg_game, nome_rp, telefone):
        embed = criar_embed("sucesso", 
            "Jogador Registrado",
            f"**RG:** {rg_game}\n**Nome:** {nome_rp}\n**Telefone:** {telefone or 'Não informado'}"
        )
    else:
        embed = criar_embed("erro", "Erro no Registro", f"Jogador com RG {rg_game} já está registrado.")
    
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="registrar", description="Registre-se no servidor do Detran")
@app_commands.describe(nome="Seu nome no jogo", rg="Seu RG no jogo")
async def registrar(interaction: discord.Interaction, nome: str, rg: str):
    if interaction.channel_id != CANAL_REGISTRO:
        embed = criar_embed("erro", "Canal incorreto", "Use este comando no canal de registro.")
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

    embed = criar_embed("sucesso", "Registro concluído", f"Bem-vindo, {nome}!")
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="cnh_emitir", description="Emite uma nova CNH para um jogador")
@app_commands.describe(
    rg_game="RG do jogador no jogo",
    categoria="Categoria da CNH (A, B, C, D, E, Náutica, Aérea)",
    nome_rp="Nome do jogador caso não esteja registrado"
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
async def cnh_emitir(interaction: discord.Interaction, rg_game: str, categoria: str, nome_rp: str = None):
    if not verificar_permissao(interaction, "cnh_emitir"):
        embed = criar_embed("erro", "Sem Permissão", "Você não tem permissão para executar este comando.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    player = db.get_player(rg_game)
    if not player:
        if nome_rp:
            db.registrar_player(rg_game, nome_rp)
            player = db.get_player(rg_game)
        else:
            embed = criar_embed("erro", "Jogador Não Encontrado", f"Jogador com RG {rg_game} não registrado. Informe o nome para registrá-lo.")
            await interaction.response.send_message(embed=embed)
            return
    
    numero_registro = db.emitir_cnh(rg_game, categoria)
    embed = criar_embed("sucesso", 
        "CNH Emitida",
        f"**Jogador:** {player['nome_rp']}\n**RG:** {rg_game}\n**Categoria:** {categoria}\n**Número:** {numero_registro}"
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="cnh_consultar", description="Consulta o status e detalhes da CNH de um jogador")
@app_commands.describe(rg_game="RG do jogador no jogo")
async def cnh_consultar(interaction: discord.Interaction, rg_game: str):
    player = db.get_player(rg_game)
    if not player:
        embed = criar_embed("erro", "Jogador Não Encontrado", f"Não foi encontrado jogador com RG {rg_game}.")
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
        embed = criar_embed("erro", "Sem Permissão", "Você não tem permissão para executar este comando.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    player = db.get_player(rg_game)
    if not player:
        embed = criar_embed("erro", "Jogador Não Encontrado", f"Não foi encontrado jogador com RG {rg_game}.")
        await interaction.response.send_message(embed=embed)
        return
    
    if db.atualizar_status_cnh(rg_game, "suspensa"):
        embed = criar_embed("sucesso", 
            "CNH Suspensa",
            f"**Jogador:** {player['nome_rp']}\n**RG:** {rg_game}\n**Período:** {dias} dias"
        )
    else:
        embed = criar_embed("erro", "Erro", "Não foi possível suspender a CNH.")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="cnh_cassar", description="Cassa a CNH de um jogador")
@app_commands.describe(rg_game="RG do jogador no jogo")
async def cnh_cassar(interaction: discord.Interaction, rg_game: str):
    if not verificar_permissao(interaction, "cnh_cassar"):
        embed = criar_embed("erro", "Sem Permissão", "Você não tem permissão para executar este comando.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    player = db.get_player(rg_game)
    if not player:
        embed = criar_embed("erro", "Jogador Não Encontrado", f"Não foi encontrado jogador com RG {rg_game}.")
        await interaction.response.send_message(embed=embed)
        return
    
    if db.atualizar_status_cnh(rg_game, "cassada"):
        embed = criar_embed("sucesso", 
            "CNH Cassada",
            f"**Jogador:** {player['nome_rp']}\n**RG:** {rg_game}\n**Status:** Cassada definitivamente"
        )
    else:
        embed = criar_embed("erro", "Erro", "Não foi possível cassar a CNH.")
    
    await interaction.response.send_message(embed=embed)

# Comandos de Membros do Detran
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
        embed = criar_embed("erro", "Sem Permissão", "Você não tem permissão para executar este comando.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    player = db.get_player(rg_game)
    if not player:
        embed = criar_embed("erro", "Proprietário Não Encontrado", f"Não foi encontrado jogador com RG {rg_game}.")
        await interaction.response.send_message(embed=embed)
        return
    
    if db.registrar_veiculo(rg_game, placa.upper(), modelo, cor, ano, chassi):
        embed = criar_embed("sucesso", 
            "Veículo Registrado",
            f"**Proprietário:** {player['nome_rp']}\n**Placa:** {placa.upper()}\n**Modelo:** {modelo}\n**Cor:** {cor}\n**Ano:** {ano}"
        )
    else:
        embed = criar_embed("erro", "Erro no Registro", f"Veículo com placa {placa.upper()} já está registrado.")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="veiculo_consultar", description="Consulta os detalhes de um veículo")
@app_commands.describe(placa="Placa do veículo")
async def veiculo_consultar(interaction: discord.Interaction, placa: str):
    veiculo = db.get_veiculo(placa.upper())
    if not veiculo:
        embed = criar_embed("erro", "Veículo Não Encontrado", f"Não foi encontrado veículo com placa {placa.upper()}.")
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
        embed = criar_embed("erro", "Sem Permissão", "Você não tem permissão para executar este comando.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    veiculo = db.get_veiculo(placa.upper())
    if not veiculo:
        embed = criar_embed("erro", "Veículo Não Encontrado", f"Não foi encontrado veículo com placa {placa.upper()}.")
        await interaction.response.send_message(embed=embed)
        return
    
    novo_proprietario = db.get_player(novo_rg)
    if not novo_proprietario:
        embed = criar_embed("erro", "Novo Proprietário Não Encontrado", f"Não foi encontrado jogador com RG {novo_rg}.")
        await interaction.response.send_message(embed=embed)
        return
    
    if db.transferir_veiculo(placa.upper(), novo_rg):
        embed = criar_embed("sucesso", 
            "Transferência Realizada",
            f"**Veículo:** {placa.upper()}\n**Novo Proprietário:** {novo_proprietario['nome_rp']}\n**RG:** {novo_rg}"
        )
    else:
        embed = criar_embed("erro", "Erro", "Não foi possível realizar a transferência.")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="veiculo_apreender", description="Marca um veículo como apreendido")
@app_commands.describe(placa="Placa do veículo")
async def veiculo_apreender(interaction: discord.Interaction, placa: str):
    if not verificar_permissao(interaction, "veiculo_apreender"):
        embed = criar_embed("erro", "Sem Permissão", "Você não tem permissão para executar este comando.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    veiculo = db.get_veiculo(placa.upper())
    if not veiculo:
        embed = criar_embed("erro", "Veículo Não Encontrado", f"Não foi encontrado veículo com placa {placa.upper()}.")
        await interaction.response.send_message(embed=embed)
        return
    
    if db.atualizar_status_veiculo(placa.upper(), "apreendido"):
        embed = criar_embed("sucesso", 
            "Veículo Apreendido",
            f"**Placa:** {placa.upper()}\n**Status:** Apreendido\n**Agente:** {interaction.user.mention}"
        )
    else:
        embed = criar_embed("erro", "Erro", "Não foi possível apreender o veículo.")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="veiculo_liberar", description="Libera um veículo apreendido")
@app_commands.describe(placa="Placa do veículo")
async def veiculo_liberar(interaction: discord.Interaction, placa: str):
    if not verificar_permissao(interaction, "veiculo_liberar"):
        embed = criar_embed("erro", "Sem Permissão", "Você não tem permissão para executar este comando.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    veiculo = db.get_veiculo(placa.upper())
    if not veiculo:
        embed = criar_embed("erro", "Veículo Não Encontrado", f"Não foi encontrado veículo com placa {placa.upper()}.")
        await interaction.response.send_message(embed=embed)
        return
    
    if db.atualizar_status_veiculo(placa.upper(), "ativo"):
        embed = criar_embed("sucesso", 
            "Veículo Liberado",
            f"**Placa:** {placa.upper()}\n**Status:** Liberado\n**Agente:** {interaction.user.mention}"
        )
    else:
        embed = criar_embed("erro", "Erro", "Não foi possível liberar o veículo.")
    
    await interaction.response.send_message(embed=embed)

# Comandos de Multas e Infrações
@bot.tree.command(name="multar", description="Aplica uma multa a um jogador")
@app_commands.describe(
    rg_game="RG do jogador",
    tipo_infracao="Tipo de infração",
    placa_veiculo="Placa do veículo (opcional)"
)
async def multar(interaction: discord.Interaction, rg_game: str, tipo_infracao: str, placa_veiculo: str = None):
    if not verificar_permissao(interaction, "multar"):
        embed = criar_embed("erro", "Sem Permissão", "Você não tem permissão para executar este comando.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    player = db.get_player(rg_game)
    if not player:
        embed = criar_embed("erro", "Jogador Não Encontrado", f"Não foi encontrado jogador com RG {rg_game}.")
        await interaction.response.send_message(embed=embed)
        return
    
    if placa_veiculo:
        veiculo = db.get_veiculo(placa_veiculo.upper())
        if not veiculo:
            embed = criar_embed("erro", "Veículo Não Encontrado", f"Não foi encontrado veículo com placa {placa_veiculo.upper()}.")
            await interaction.response.send_message(embed=embed)
            return
        placa_veiculo = placa_veiculo.upper()
    
    infracao = TABELA_INFRACOES.get(tipo_infracao)
    if not infracao:
        embed = criar_embed("erro", "Infração Inválida", "O código de infração informado não existe.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
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

    # Verificar se foi multa em dobro por reincidência
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT valor FROM multas WHERE id = ?', (multa_id,))
        valor_aplicado = cursor.fetchone()[0]
        reincidencia = valor_aplicado > infracao['valor']

    valor_desconto = valor_aplicado * 0.85
    
    embed = discord.Embed(
        title="🚨 Multa Aplicada",
        color=CORES["aviso"]
    )
    embed.add_field(name="Jogador", value=f"{player['nome_rp']} ({rg_game})", inline=True)
    embed.add_field(name="Infração", value=infracao['descricao'], inline=False)
    embed.add_field(name="Valor", value=f"R$ {valor_aplicado:.2f}", inline=True)
    embed.add_field(name="Valor com desconto", value=f"R$ {valor_desconto:.2f}", inline=True)
    embed.add_field(name="Pontos", value=infracao['pontos'], inline=True)
    embed.add_field(name="Pátio", value=f"{infracao['patio']}h", inline=True)
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


@multar.autocomplete("tipo_infracao")
async def multar_autocomplete(interaction: discord.Interaction, current: str):
    resultados = []
    for codigo, infracao in TABELA_INFRACOES.items():
        if current.lower() in infracao["descricao"].lower():
            resultados.append(app_commands.Choice(name=infracao["descricao"], value=codigo))
        if len(resultados) >= 25:
            break
    return resultados

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
        embed = criar_embed("erro", "Jogador Não Encontrado", f"Não foi encontrado jogador com RG {rg_game}.")
        await interaction.response.send_message(embed=embed)
        return
    
    multas = db.get_multas_jogador(rg_game, status)
    
    if not multas:
        status_texto = f" ({status})" if status else ""
        embed = criar_embed("info", "Consulta de Multas", f"Nenhuma multa encontrada para {player['nome_rp']}{status_texto}.")
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
        embed = criar_embed("erro", "Sem Permissão", "Você não tem permissão para executar este comando.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    if db.pagar_multa(multa_id):
        embed = criar_embed("sucesso", 
            "Multa Paga",
            f"**ID da Multa:** {multa_id}\n**Processado por:** {interaction.user.mention}"
        )
    else:
        embed = criar_embed("erro", "Erro", f"Não foi possível processar o pagamento da multa #{multa_id}.")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="multa_recorrer", description="Marca uma multa como em recurso")
@app_commands.describe(multa_id="ID da multa")
async def multa_recorrer(interaction: discord.Interaction, multa_id: int):
    if not verificar_permissao(interaction, "multa_recorrer"):
        embed = criar_embed("erro", "Sem Permissão", "Você não tem permissão para executar este comando.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    if db.recorrer_multa(multa_id):
        embed = criar_embed("sucesso", 
            "Recurso Registrado",
            f"**ID da Multa:** {multa_id}\n**Status:** Em recurso\n**Processado por:** {interaction.user.mention}"
        )
    else:
        embed = criar_embed("erro", "Erro", f"Não foi possível processar o recurso da multa #{multa_id}.")
    
    await interaction.response.send_message(embed=embed)

# Comandos de Cursos
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
    
    categorias = {"Leves": [], "Médias": [], "Graves": [], "Gravíssimas": []}
    for infracao in TABELA_INFRACOES.values():
        valor_desconto = infracao['valor'] * 0.85
        linha = (
            f"• {infracao['descricao']}\n"
            f"  Valor: R$ {infracao['valor']:.2f} (desc: R$ {valor_desconto:.2f})\n"
            f"  Pontos: {infracao['pontos']} | Pátio: {infracao['patio']}h"
        )
        if infracao['pontos'] == 3:
            categorias["Leves"].append(linha)
        elif infracao['pontos'] == 4:
            categorias["Médias"].append(linha)
        elif infracao['pontos'] == 5:
            categorias["Graves"].append(linha)
        else:
            categorias["Gravíssimas"].append(linha)

    for nome, itens in categorias.items():
        if itens:
            embed.add_field(name=nome, value="\n".join(itens), inline=False)
    
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
        embed = criar_embed("erro", "Sem Permissão", "Você não tem permissão para executar este comando.")
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
        embed = criar_embed("erro", "Sem Permissão", "Você não tem permissão para executar este comando.")
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
        embed = criar_embed("info", "CNHs Suspensas", "Nenhuma CNH suspensa, revogada ou cassada encontrada.")
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

# Sistema de Tickets
@bot.tree.command(name="ticket_criar", description="Cria um ticket de suporte")
@app_commands.describe(descricao="Descreva seu problema")
async def ticket_criar(interaction: discord.Interaction, descricao: str):
    ticket_id = db.criar_ticket(str(interaction.user.id), descricao)
    embed = criar_embed("sucesso", "Ticket Criado", f"Ticket #{ticket_id} registrado com sucesso.")
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="ticket_listar", description="Lista tickets de suporte")
@app_commands.describe(status="Filtrar por status")
@app_commands.choices(status=[
    app_commands.Choice(name="aberto", value="aberto"),
    app_commands.Choice(name="fechado", value="fechado")
])
async def ticket_listar(interaction: discord.Interaction, status: str = "aberto"):
    if not verificar_permissao(interaction, "ticket_listar"):
        embed = criar_embed("erro", "Sem Permissão", "Você não tem permissão para executar este comando.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    tickets = db.listar_tickets(status)
    if tickets:
        descricao = "\n".join([
            f"ID {t['id']}: {t['descricao']} (Autor: <@{t['autor_id']}>)" for t in tickets
        ])
    else:
        descricao = "Nenhum ticket encontrado."

    embed = criar_embed("info", "Tickets", descricao)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="ticket_fechar", description="Fecha um ticket de suporte")
@app_commands.describe(ticket_id="ID do ticket")
async def ticket_fechar(interaction: discord.Interaction, ticket_id: int):
    if not verificar_permissao(interaction, "ticket_fechar"):
        embed = criar_embed("erro", "Sem Permissão", "Você não tem permissão para executar este comando.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    if db.fechar_ticket(ticket_id):
        embed = criar_embed("sucesso", "Ticket Fechado", f"Ticket #{ticket_id} foi fechado.")
    else:
        embed = criar_embed("erro", "Erro", f"Ticket #{ticket_id} não encontrado ou já fechado.")

    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="aviso", description="Envia um aviso para o canal de avisos")
@app_commands.describe(mensagem="Conteúdo do aviso")
async def aviso(interaction: discord.Interaction, mensagem: str):
    if not verificar_permissao(interaction, "aviso"):
        embed = criar_embed("erro", "Sem Permissão", "Você não tem permissão para executar este comando.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    canal = bot.get_channel(CANAL_AVISOS)
    if canal:
        embed = discord.Embed(title="📢 Aviso", description=mensagem, color=CORES["info"])
        await canal.send(embed=embed)
        resposta = criar_embed("sucesso", "Aviso enviado", f"Aviso publicado em {canal.mention}.")
    else:
        resposta = criar_embed("erro", "Erro", "Canal de avisos não encontrado.")
    await interaction.response.send_message(embed=resposta, ephemeral=True)

# Comando para executar o bot
if __name__ == "__main__":
    # Verificar se o token foi definido
    if DISCORD_TOKEN == "SEU_TOKEN_AQUI":
        print("❌ ERRO: Token do Discord não configurado!")
        print("Edite o arquivo config.py e defina seu token do Discord.")
    else:
        bot.run(DISCORD_TOKEN)

