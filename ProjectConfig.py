import os

def Config_Project():
  # Idempotente: nao quebra se as pastas ja existirem (antes usava os.mkdir e
  # estourava FileExistsError ao rodar duas vezes).
  os.makedirs('response', exist_ok=True)
  os.makedirs('midia', exist_ok=True)
  # Cria o .env vazio se nao existir e fecha o handle (antes vazava o arquivo aberto).
  open('.env', 'a').close()

# pip install -r requirements.txt
# Guard de __main__: permite importar este modulo (ex.: em testes) sem disparar
# os efeitos colaterais de criar pastas/arquivo.
if __name__ == "__main__":
  Config_Project()