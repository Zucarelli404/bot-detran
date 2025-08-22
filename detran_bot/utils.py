"""Funções utilitárias para o bot do Detran."""

import discord
from discord.ext import commands

from config import (
    CORES,
    ROLE_GERENCIA,
    ROLE_FUNCIONARIOS,
    PERMISSOES_FUNCIONARIOS,
    CANAL_LOGS,
)


EMBED_ICONS = {
    "erro": "❌",
    "sucesso": "✅",
    "info": "ℹ️",
    "aviso": "⚠️",
}


def criar_embed(tipo: str, titulo: str, descricao: str) -> discord.Embed:
    """Cria um embed padronizado."""
    prefixo = EMBED_ICONS.get(tipo, "")
    embed = discord.Embed(
        title=f"{prefixo} {titulo}" if prefixo else titulo,
        description=descricao,
        color=CORES.get(tipo, CORES["info"]),
    )
    return embed


def verificar_permissao(interaction: discord.Interaction, comando: str) -> bool:
    """Verifica se o usuário possui permissão para executar o comando."""
    role_ids = [role.id for role in interaction.user.roles]

    if ROLE_GERENCIA in role_ids:
        return True

    if ROLE_FUNCIONARIOS in role_ids:
        return comando in PERMISSOES_FUNCIONARIOS

    return False


async def enviar_log(bot: commands.Bot, mensagem: str) -> None:
    """Envia uma mensagem de log para o canal configurado."""
    canal = bot.get_channel(CANAL_LOGS)
    if canal:
        await canal.send(mensagem)

