
# Deploy no Railway — Bot Discord DETRAN

## Passos
1) Envie este repositório para o GitHub (ou importe o ZIP diretamente no Railway).
2) No Railway, crie um **New Project** → **Deploy from GitHub** (ou **Empty Project** e faça o upload).
3) Em **Variables**, adicione:
   - `TOKEN` = *seu Bot Token do Discord* (não é o Client Secret).
4) Faça o deploy. O Railway vai instalar `requirements.txt` e iniciar com o `Procfile`:
   ```
   worker: python detran_bot/bot.py
   ```

> Observação: O arquivo `detran_bot/config.py` foi ajustado para ler `TOKEN` de variável de ambiente.
