# Frontend — Login com passkey

## Desenvolvimento sem Node (recomendado neste projeto)

O `RP_ORIGIN` aponta para `http://localhost:8000`. Para manter exatamente essa origem sem alterar o backend, execute a API na porta interna 8001 e o frontend/proxy na porta 8000:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8001
# Noutro terminal:
.\.venv\Scripts\python.exe frontend\serve.py
```

Abra **exatamente** `http://localhost:8000` (não use `127.0.0.1`). O servidor encaminha `/api/*` ao FastAPI, mantendo a sessão do desafio WebAuthn sem alterações de CORS.

Para usar outro endereço interno da API, defina `PASSKEY_BACKEND_URL` antes de executar `serve.py`.

> WebAuthn exige que o hostname aberto no navegador, o hostname de `RP_ORIGIN` e o `RP_ID` sejam compatíveis. No desenvolvimento, os três devem usar `localhost`.

## Desenvolvimento com Vite (opcional)

```powershell
cd frontend
npm install
npm run dev
```

O proxy do Vite usa as mesmas portas. Se necessário, copie `.env.example` para `.env` e altere `VITE_API_PROXY_TARGET`.

## Produção

```powershell
npm run build
```

Os ficheiros ficam em `dist/`. Configure o servidor web para encaminhar `/api/*` ao FastAPI ou defina `VITE_API_BASE_URL` antes do build.

## Integração atual

- Cadastro: consome `Registrar/Opcoes`, invoca a API WebAuthn do navegador e envia a credencial a `Registrar/Verificar`.
- Login: já está ligado a `Autenticar/Opcoes` e `Autenticar/Verificar`; enquanto essas rotas devolverem `null`, a interface informa que a funcionalidade está em preparação.
- A conversão aceita tanto opções WebAuthn devolvidas como objeto quanto a string JSON produzida atualmente por `options_to_json()`.
