"""Testes do bootstrap de pastas/.env do ProjectConfig.

Cobre o refactor que tornou ``Config_Project`` idempotente e protegeu os efeitos
colaterais atras de um guard ``__main__``:

- ``os.makedirs(..., exist_ok=True)`` no lugar de ``os.mkdir`` (antes estourava
  ``FileExistsError`` ao rodar duas vezes);
- ``.env`` aberto em modo append e fechado (antes vazava o handle e podia
  truncar conteudo);
- a criacao das pastas so acontece dentro de ``if __name__ == "__main__"``,
  entao um simples ``import ProjectConfig`` nao deve mexer no filesystem.

Como ``Config_Project`` usa caminhos relativos, cada teste roda isolado num
``tmp_path`` via ``monkeypatch.chdir`` para nao sujar o repo.
"""

import importlib
import sys

import pytest

import ProjectConfig


@pytest.fixture
def in_tmp_cwd(tmp_path, monkeypatch):
    """Roda o teste com o cwd apontando para um ``tmp_path`` limpo.

    Garante isolamento: os caminhos relativos de ``Config_Project`` ('response',
    'midia', '.env') sao resolvidos dentro do diretorio temporario.
    """
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_config_project_cria_pastas_e_env(in_tmp_cwd):
    """Config_Project deve criar 'response', 'midia' e o arquivo '.env'."""
    ProjectConfig.Config_Project()

    response_dir = in_tmp_cwd / "response"
    midia_dir = in_tmp_cwd / "midia"
    env_file = in_tmp_cwd / ".env"

    assert response_dir.is_dir(), "pasta 'response' nao foi criada"
    assert midia_dir.is_dir(), "pasta 'midia' nao foi criada"
    assert env_file.is_file(), "arquivo '.env' nao foi criado"


def test_config_project_e_idempotente(in_tmp_cwd):
    """Chamar Config_Project duas vezes nao deve levantar excecao.

    Ponto-chave do refactor: ``os.makedirs(exist_ok=True)`` e ``open('.env','a')``
    toleram que pastas/arquivo ja existam (antes ``os.mkdir`` estourava
    ``FileExistsError`` na segunda chamada).
    """
    ProjectConfig.Config_Project()
    # Segunda chamada nao pode explodir; se explodir, o teste falha por excecao.
    ProjectConfig.Config_Project()

    assert (in_tmp_cwd / "response").is_dir()
    assert (in_tmp_cwd / "midia").is_dir()
    assert (in_tmp_cwd / ".env").is_file()


def test_config_project_idempotente_com_pastas_preexistentes(in_tmp_cwd):
    """Com as pastas ja criadas a mao, Config_Project deve apenas seguir em frente.

    Cobre o caminho em que o diretorio existe antes da chamada (estado parcial,
    como apos um bootstrap anterior interrompido).
    """
    (in_tmp_cwd / "response").mkdir()
    (in_tmp_cwd / "midia").mkdir()

    # Nao pode levantar FileExistsError.
    ProjectConfig.Config_Project()

    assert (in_tmp_cwd / "response").is_dir()
    assert (in_tmp_cwd / "midia").is_dir()
    assert (in_tmp_cwd / ".env").is_file()


def test_env_em_modo_append_preserva_conteudo_existente(in_tmp_cwd):
    """O .env e aberto em 'a' e fechado: conteudo previo deve permanecer intacto.

    Se o codigo abrisse em 'w' (ou vazasse o handle truncando), o conteudo seria
    perdido. Aqui validamos que um .env preexistente sobrevive a chamada.
    """
    env_file = in_tmp_cwd / ".env"
    conteudo = "API_GEMINI=chave_secreta\n"
    env_file.write_text(conteudo, encoding="utf-8")

    ProjectConfig.Config_Project()

    assert env_file.read_text(encoding="utf-8") == conteudo


def test_import_do_modulo_nao_cria_pastas(tmp_path, monkeypatch):
    """Importar ProjectConfig (guard __main__) nao deve tocar no filesystem.

    O modulo provavelmente ja esta em ``sys.modules`` (importado no topo). Para
    exercitar o caminho de import "do zero" com o cwd ja no tmp_path, removemos o
    modulo do cache e reimportamos. Nenhuma pasta deve surgir, pois a criacao so
    ocorre sob ``if __name__ == '__main__'``.
    """
    monkeypatch.chdir(tmp_path)
    # Garante que o import abaixo execute o corpo do modulo de novo.
    monkeypatch.delitem(sys.modules, "ProjectConfig", raising=False)

    importlib.import_module("ProjectConfig")

    assert not (tmp_path / "response").exists(), "import criou 'response' indevidamente"
    assert not (tmp_path / "midia").exists(), "import criou 'midia' indevidamente"
    assert not (tmp_path / ".env").exists(), "import criou '.env' indevidamente"


def test_reload_do_modulo_nao_cria_pastas(tmp_path, monkeypatch):
    """Recarregar o modulo (importlib.reload) tambem nao pode disparar o bootstrap.

    Reforca o teste de import usando ``reload``, que reexecuta o corpo do modulo
    mantendo o nome ``ProjectConfig`` (e nao ``__main__``), entao o guard segue
    impedindo os efeitos colaterais.
    """
    monkeypatch.chdir(tmp_path)

    importlib.reload(ProjectConfig)

    assert not (tmp_path / "response").exists()
    assert not (tmp_path / "midia").exists()
    assert not (tmp_path / ".env").exists()
