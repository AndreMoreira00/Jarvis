"""Testes do ``manager.Manager`` (upload Google Photos via OAuth + requests).

Estrategia:
- As classes do google-auth (``Credentials``, ``InstalledAppFlow``, ``Request``)
  ja chegam como atributos MagicMock no modulo ``manager`` (stubadas pelo
  conftest). Reconfiguramos por teste via ``monkeypatch.setattr(manager, ...)``.
- ``requests`` e REAL: mockamos o comportamento de rede ponto a ponto com
  ``monkeypatch.setattr(manager.requests, ...)``.
- Disco: nada e escrito de verdade; ``open`` e substituido por ``mock_open``.

O foco e o NOSSO codigo (orquestracao OAuth, montagem de headers/URL/payload,
sequencia de chamadas HTTP), nao as libs stubadas.
"""

from unittest.mock import MagicMock, call, mock_open, patch

import pytest

import manager


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mgr():
    """Instancia limpa de ``Manager`` para cada teste."""
    return manager.Manager()


@pytest.fixture
def fake_requests(monkeypatch):
    """Substitui ``manager.requests`` por um MagicMock controlavel.

    Retorna o mock para o teste configurar ``.get``/``.post`` conforme o caso.
    """
    fake = MagicMock(name="requests")
    monkeypatch.setattr(manager, "requests", fake)
    return fake


# ---------------------------------------------------------------------------
# 1. __init__ — constantes de configuracao
# ---------------------------------------------------------------------------

class TestInit:
    """Garante que os caminhos e o escopo OAuth ficam corretos na construcao."""

    def test_client_secret_aponta_para_env(self, mgr):
        """O segredo OAuth deve vir de ./env/client_secret.json."""
        assert mgr.CLIENT_SECRET == "./env/client_secret.json"

    def test_credentials_file_aponta_para_token(self, mgr):
        """O token cacheado deve ser gravado/lido em ./env/token.json."""
        assert mgr.CREDENTIALS_FILE == "./env/token.json"

    def test_scopes_contem_url_do_photoslibrary(self, mgr):
        """O escopo precisa autorizar acesso ao Photos Library."""
        assert mgr.SCOPES == ["https://www.googleapis.com/auth/photoslibrary"]
        assert any("photoslibrary" in s for s in mgr.SCOPES)


# ---------------------------------------------------------------------------
# 2. authorize_credentials — fluxo OAuth (token cacheado / refresh / login)
# ---------------------------------------------------------------------------

class TestAuthorizeCredentials:
    """Cobre os tres caminhos do fluxo de credenciais."""

    def test_token_valido_retorna_sem_refletir_flow(self, mgr, monkeypatch):
        """Se token.json existe e a cred e valida, devolve creds.token direto.

        Nao deve disparar refresh nem o fluxo interativo (InstalledAppFlow),
        nem reescrever o arquivo de token.
        """
        creds = MagicMock(name="creds")
        creds.valid = True
        creds.token = "token-valido"

        from_file = MagicMock(return_value=creds)
        flow_cls = MagicMock(name="InstalledAppFlow")

        monkeypatch.setattr(manager.os.path, "exists", lambda p: True)
        monkeypatch.setattr(
            manager.Credentials, "from_authorized_user_file", from_file
        )
        monkeypatch.setattr(manager, "InstalledAppFlow", flow_cls)

        m = mock_open()
        with patch("builtins.open", m):
            resultado = mgr.authorize_credentials()

        assert resultado == "token-valido"
        # Carregou do arquivo correto, com o escopo correto.
        from_file.assert_called_once_with(mgr.CREDENTIALS_FILE, mgr.SCOPES)
        # Cred ja valida => nada de refresh, nada de fluxo interativo, nada de escrita.
        creds.refresh.assert_not_called()
        flow_cls.from_client_secrets_file.assert_not_called()
        m.assert_not_called()

    def test_token_expirado_chama_refresh_e_grava(self, mgr, monkeypatch):
        """Cred expirada com refresh_token: refresh(Request()) e regrava token.json."""
        creds = MagicMock(name="creds")
        creds.valid = False
        creds.expired = True
        creds.refresh_token = "refresh-abc"
        creds.token = "token-renovado"
        creds.to_json.return_value = '{"token": "renovado"}'

        request_cls = MagicMock(name="Request")
        request_instance = request_cls.return_value
        flow_cls = MagicMock(name="InstalledAppFlow")

        monkeypatch.setattr(manager.os.path, "exists", lambda p: True)
        monkeypatch.setattr(
            manager.Credentials,
            "from_authorized_user_file",
            MagicMock(return_value=creds),
        )
        monkeypatch.setattr(manager, "Request", request_cls)
        monkeypatch.setattr(manager, "InstalledAppFlow", flow_cls)

        m = mock_open()
        with patch("builtins.open", m):
            resultado = mgr.authorize_credentials()

        assert resultado == "token-renovado"
        # Renovou usando uma instancia de Request().
        creds.refresh.assert_called_once_with(request_instance)
        # Nao caiu no fluxo interativo.
        flow_cls.from_client_secrets_file.assert_not_called()
        # Regravou o token.json com o JSON da cred.
        m.assert_called_once_with(mgr.CREDENTIALS_FILE, "w")
        m().write.assert_called_once_with(creds.to_json.return_value)

    def test_sem_token_dispara_fluxo_interativo_e_grava(self, mgr, monkeypatch):
        """Sem token.json: roda InstalledAppFlow.run_local_server(port=0) e grava."""
        new_creds = MagicMock(name="new_creds")
        new_creds.token = "token-novo"
        new_creds.to_json.return_value = '{"token": "novo"}'

        flow = MagicMock(name="flow")
        flow.run_local_server.return_value = new_creds
        flow_cls = MagicMock(name="InstalledAppFlow")
        flow_cls.from_client_secrets_file.return_value = flow

        from_file = MagicMock(name="from_authorized_user_file")

        # Arquivo de token NAO existe => pula o load e cai no fluxo interativo.
        monkeypatch.setattr(manager.os.path, "exists", lambda p: False)
        monkeypatch.setattr(
            manager.Credentials, "from_authorized_user_file", from_file
        )
        monkeypatch.setattr(manager, "InstalledAppFlow", flow_cls)

        m = mock_open()
        with patch("builtins.open", m):
            resultado = mgr.authorize_credentials()

        assert resultado == "token-novo"
        # Como o arquivo nao existe, nao tentou carregar credencial do disco.
        from_file.assert_not_called()
        # Montou o fluxo a partir do client_secret e do escopo certos.
        flow_cls.from_client_secrets_file.assert_called_once_with(
            mgr.CLIENT_SECRET, mgr.SCOPES
        )
        flow.run_local_server.assert_called_once_with(port=0)
        # Persistiu o token novo.
        m.assert_called_once_with(mgr.CREDENTIALS_FILE, "w")
        m().write.assert_called_once_with(new_creds.to_json.return_value)


# ---------------------------------------------------------------------------
# 3. getPhotoUrl — GET no mediaItem e extracao do baseUrl
# ---------------------------------------------------------------------------

class TestGetPhotoUrl:
    """Cobre montagem de header/URL e extracao do baseUrl da resposta."""

    def test_monta_header_e_url_e_retorna_baseurl(self, mgr, fake_requests):
        """Authorization Bearer + URL do mediaItem; retorna response.json()['baseUrl']."""
        response = MagicMock(name="response")
        response.json.return_value = {"baseUrl": "https://lh3.googleusercontent.com/abc"}
        fake_requests.get.return_value = response

        url = mgr.getPhotoUrl("fake-token", "PHOTO123")

        assert url == "https://lh3.googleusercontent.com/abc"
        fake_requests.get.assert_called_once_with(
            "https://photoslibrary.googleapis.com/v1/mediaItems/PHOTO123",
            headers={
                "Authorization": "Bearer fake-token",
                "Content-type": "application/json",
            },
        )

    def test_id_diferente_muda_a_url(self, mgr, fake_requests):
        """O photo_id deve ser interpolado na URL do mediaItem."""
        response = MagicMock(name="response")
        response.json.return_value = {"baseUrl": "https://x/y"}
        fake_requests.get.return_value = response

        mgr.getPhotoUrl("tok", "OUTRO-ID")

        chamada_url = fake_requests.get.call_args.args[0]
        assert chamada_url.endswith("/mediaItems/OUTRO-ID")


# ---------------------------------------------------------------------------
# 4. uploadMidia — upload raw + batchCreate + resolucao da URL
# ---------------------------------------------------------------------------

class TestUploadMidia:
    """Cobre o happy-path completo e o caminho de erro HTTP."""

    def test_happy_path_faz_upload_batchcreate_e_resolve_url(
        self, mgr, fake_requests, monkeypatch
    ):
        """Sequencia: POST upload (200) -> POST batchCreate -> getPhotoUrl.

        Verifica headers/payload de cada etapa e a ordem das chamadas requests.post.
        """
        # authorize_credentials e testado a parte; aqui so devolve um token fixo.
        monkeypatch.setattr(mgr, "authorize_credentials", lambda: "fake-token")
        # getPhotoUrl tambem testado a parte; isola a resolucao final.
        get_url = MagicMock(return_value="https://lh3/final")
        monkeypatch.setattr(mgr, "getPhotoUrl", get_url)

        # 1a resposta: upload raw -> 200 + upload_token no body.
        upload_resp = MagicMock(name="upload_resp")
        upload_resp.status_code = 200
        upload_resp.text = "UPLOAD-TOKEN-XYZ"
        # 2a resposta: batchCreate -> json com o id do mediaItem.
        batch_resp = MagicMock(name="batch_resp")
        batch_resp.json.return_value = {
            "newMediaItemResults": [
                {"mediaItem": {"id": "MEDIA-ID-9"}}
            ]
        }
        fake_requests.post.side_effect = [upload_resp, batch_resp]

        m = mock_open(read_data=b"bytes-da-imagem")
        with patch("builtins.open", m):
            mgr.uploadMidia("/midia/foto.jpg")

        # Abriu o arquivo em binario para ler os bytes.
        m.assert_called_once_with("/midia/foto.jpg", "rb")

        # Duas chamadas POST, nesta ordem: uploads, depois batchCreate.
        assert fake_requests.post.call_count == 2
        primeira, segunda = fake_requests.post.call_args_list

        # --- POST 1: upload raw dos bytes ---
        assert primeira.args[0] == "https://photoslibrary.googleapis.com/v1/uploads"
        assert primeira.kwargs["headers"] == {
            "Authorization": "Bearer fake-token",
            "Content-type": "application/octet-stream",
            "X-Goog-Upload-Content-Type": "image/jpeg",
            "X-Goog-Upload-Protocol": "raw",
        }
        assert primeira.kwargs["data"] == b"bytes-da-imagem"

        # --- POST 2: batchCreate com o upload_token e o basename do arquivo ---
        assert (
            segunda.args[0]
            == "https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate"
        )
        assert segunda.kwargs["headers"] == {
            "Authorization": "Bearer fake-token",
            "Content-type": "application/json",
        }
        assert segunda.kwargs["json"] == {
            "newMediaItems": [
                {
                    "simpleMediaItem": {
                        "fileName": "foto.jpg",
                        "uploadToken": "UPLOAD-TOKEN-XYZ",
                    }
                }
            ]
        }

        # Resolveu a URL final com o token e o id extraido do batchCreate.
        get_url.assert_called_once_with("fake-token", "MEDIA-ID-9")

    def test_filename_usa_basename_do_caminho(
        self, mgr, fake_requests, monkeypatch
    ):
        """fileName no payload deve ser apenas o basename, sem o diretorio."""
        monkeypatch.setattr(mgr, "authorize_credentials", lambda: "tok")
        monkeypatch.setattr(mgr, "getPhotoUrl", MagicMock(return_value="u"))

        upload_resp = MagicMock(status_code=200, text="UT")
        batch_resp = MagicMock()
        batch_resp.json.return_value = {
            "newMediaItemResults": [{"mediaItem": {"id": "ID"}}]
        }
        fake_requests.post.side_effect = [upload_resp, batch_resp]

        m = mock_open(read_data=b"x")
        # Caminho aninhado: so o nome do arquivo deve sobrar.
        with patch("builtins.open", m):
            mgr.uploadMidia("/var/data/midia/sub/imagem_final.jpg")

        payload = fake_requests.post.call_args_list[1].kwargs["json"]
        nome = payload["newMediaItems"][0]["simpleMediaItem"]["fileName"]
        assert nome == "imagem_final.jpg"

    def test_status_diferente_de_200_levanta_via_raise_for_status(
        self, mgr, fake_requests, monkeypatch
    ):
        """Upload != 200: chama raise_for_status e NAO faz batchCreate nem resolve URL."""
        monkeypatch.setattr(mgr, "authorize_credentials", lambda: "fake-token")
        get_url = MagicMock(name="getPhotoUrl")
        monkeypatch.setattr(mgr, "getPhotoUrl", get_url)

        upload_resp = MagicMock(name="upload_resp")
        upload_resp.status_code = 403
        upload_resp.raise_for_status.side_effect = RuntimeError("HTTP 403")
        fake_requests.post.return_value = upload_resp

        m = mock_open(read_data=b"bytes")
        with patch("builtins.open", m):
            with pytest.raises(RuntimeError, match="HTTP 403"):
                mgr.uploadMidia("/midia/foto.jpg")

        # So o POST de upload aconteceu; batchCreate nunca foi chamado.
        assert fake_requests.post.call_count == 1
        upload_resp.raise_for_status.assert_called_once_with()
        get_url.assert_not_called()
