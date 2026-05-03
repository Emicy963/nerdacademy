# Guia de Testes Locais — Matrika

> Guia completo para testar todas as funcionalidades localmente, verificar correções de segurança e identificar bugs ou melhorias.

---

## 1. Setup Inicial

### 1.1 Variáveis de ambiente

Copia `.env.example` para `.env` e preenche:

```bash
cd backend
cp .env.example .env
```

Valores mínimos para dev local:

```env
DJANGO_SETTINGS_MODULE=core.settings.development
SECRET_KEY=dev-secret-key-qualquer-string-longa
DEBUG=True

# Usa SQLite em vez de Postgres para dev rápido
# (deixa DB_* em branco ou aponta para Postgres local)

# Email — Gmail real (importante para testar verificação de instituição)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=teu-gmail@gmail.com
EMAIL_HOST_PASSWORD=app-password-do-gmail
DEFAULT_FROM_EMAIL=Matrika <teu-gmail@gmail.com>

FRONTEND_URL=http://localhost:3000
```

> **App Password Gmail:** Vai a myaccount.google.com → Segurança → Verificação em 2 etapas → Palavras-passe de apps. Gera uma para "Mail".

### 1.2 Instalar dependências

```bash
cd backend
pip install -r requirements/development.txt
```

### 1.3 Aplicar migrações (incluindo a nova migração de verificação)

```bash
python manage.py migrate
```

Confirma que a migração `0003_institution_verification` foi aplicada:

```bash
python manage.py showmigrations institutions
# Deve aparecer:
# [X] 0001_initial
# [X] 0002_...
# [X] 0003_institution_verification
```

### 1.4 Criar superuser (para aceder ao painel admin)

```bash
python manage.py createsuperuser
```

---

## 2. Arrancar os Servidores

### Backend

```bash
cd backend
python manage.py runserver
# Disponível em http://localhost:8000
```

### Frontend

Qualquer servidor estático serve. Opções:

```bash
# Opção A — Python (mais simples)
cd frontend
python -m http.server 3000

# Opção B — Node (se tiveres npx instalado)
cd frontend
npx serve -l 3000
```

Frontend disponível em `http://localhost:3000`.

---

## 3. Verificar Configuração Base

Antes de testar features, confirma que o ambiente está a funcionar:

```bash
# Health check
curl http://localhost:8000/api/health/
# Esperado: {"status": "ok"}
```

Admin panel (URL obfuscado por segurança):
- Abre `http://localhost:8000/mgmt-matrika/`
- Faz login com o superuser criado

---

## 4. Fluxo de Registo de Instituição + Verificação de Email

Este é o fluxo mais crítico introduzido na v0.7.0. Testa por esta ordem:

### 4.1 Registo

1. Abre `http://localhost:3000/pages/register.html`
2. Preenche: nome da instituição, nome do admin, email, password
3. Submete
4. **Esperado:**
   - Redirect para `verify-institution.html`
   - Email chegado na caixa de correio com link de ativação
   - Estado "Verifique o seu email" visível com o email correto

### 4.2 Verificação via email

1. Abre o email recebido
2. Clica no link de ativação (formato: `http://localhost:3000/pages/verify-institution.html#TOKEN`)
3. **Esperado:**
   - Estado "A verificar..." aparece brevemente
   - Estado "Conta verificada!" aparece
   - Botão "Ir para o login" disponível

### 4.3 Verificar bloqueio antes da verificação

1. Após o registo (sem clicar no link), tenta fazer login em `http://localhost:3000/pages/login.html`
2. Usa as credenciais do admin recém-registado
3. **Esperado:**
   - Redirect para `verify-institution.html` (estado "pending")
   - **NÃO** entra no dashboard

### 4.4 Verificar via admin Django (bypass manual para testes)

Se precisares de ativar manualmente uma instituição sem email:

1. Vai a `http://localhost:8000/mgmt-matrika/`
2. Abre a instituição em questão
3. Marca `is_verified = True` e limpa `verification_token`
4. Guarda

### Possíveis bugs a vigiar

- [ ] Email não chega → verificar `EMAIL_HOST_PASSWORD` no `.env`
- [ ] Link no email aponta para URL errada → verificar `FRONTEND_URL` no `.env`
- [ ] Token inválido → pode acontecer se o token foi usado ou a instituição já estava verificada
- [ ] Estado "pending" não mostra o email → `localStorage('matrika_verify_email')` pode estar vazio se não veio do register

---

## 5. Fluxo de Autenticação

### 5.1 Login normal

1. Abre `http://localhost:3000/pages/login.html`
2. Faz login com admin de instituição verificada
3. **Esperado:**
   - Redirect para `dashboard.html`
   - Access token em `localStorage('matrika_access')`
   - **Refresh token apenas como cookie HttpOnly** (não visível no localStorage)

### 5.2 Inspecionar o cookie HttpOnly

1. DevTools → Application → Cookies → `http://localhost:3000`
2. Procura por `refresh_token`
3. **Esperado:**
   - Cookie presente com `HttpOnly: true`
   - `SameSite: Lax`
   - **Não** marcado como `Secure` em localhost (correto — Secure só em produção)

### 5.3 Logout

1. Clica em logout no dashboard
2. **Esperado:**
   - Redirect para `login.html`
   - `localStorage('matrika_access')` removido
   - Cookie `refresh_token` removido (verifica no DevTools)

### 5.4 Silent Refresh (token expirado)

O access token expira em 15 minutos. Para testar sem esperar:

```python
# Reduz temporariamente em base.py para 1 minuto:
# "ACCESS_TOKEN_LIFETIME": timedelta(minutes=1),
```

1. Faz login
2. Espera 1 minuto
3. Faz qualquer ação na UI (ex: abre dashboard)
4. **Esperado:** Ação funciona sem pedir novo login (silent refresh usou o cookie)

### 5.5 Múltiplas memberships

Se um utilizador tiver acesso a várias instituições:

1. Abre `http://localhost:8000/mgmt-matrika/` e cria um utilizador com membership em duas instituições
2. Faz login com esse utilizador
3. **Esperado:**
   - Selector de instituição aparece no header
   - Trocar de instituição muda o contexto dos dados

---

## 6. Fluxo de Recuperação de Password

### 6.1 Pedido de reset

1. Abre `http://localhost:3000/pages/forgot-password.html`
2. Insere email de um utilizador existente
3. Submete
4. **Esperado:**
   - Mensagem de confirmação genérica (mesmo se email não existir — segurança)
   - Email recebido com link no formato `http://localhost:3000/pages/reset-password.html#UID:TOKEN`

### 6.2 Reset da password

1. Clica no link no email
2. Preenche nova password e confirmação
3. Submete
4. **Esperado:** Redirect para login com mensagem de sucesso

### 6.3 Casos edge

- [ ] Link já utilizado → deve mostrar erro "link inválido ou expirado"
- [ ] Email de utilizador `@local.academico` → pedido silencioso (não envia email — comportamento correto)
- [ ] Password fraca → validação Django rejeita

---

## 7. Fluxo de Alunos

**Pré-requisito:** Login como admin de instituição verificada.

### 7.1 Criar aluno

1. Vai para `http://localhost:3000/pages/students.html`
2. Clica em "Novo Aluno"
3. Preenche nome (email opcional)
4. **Esperado:**
   - Aluno aparece na lista com código gerado (ex: `MAT20260001`)
   - Se email fornecido: aluno recebe email com password temporária
   - Se sem email: conta `@local.academico` criada internamente

### 7.2 Editar aluno

1. Clica num aluno para abrir detalhe
2. Altera nome ou estado
3. **Esperado:** Alteração refletida na lista

### 7.3 Reset de password de aluno (pelo admin)

1. No detalhe do aluno, usa "Redefinir Password"
2. **Esperado:**
   - Email enviado para o aluno (se tiver email real)
   - Flag `must_change_password=True` ativada
   - Próximo login do aluno força mudança de password

### 7.4 Login do aluno

1. Abre `login.html` em aba incógnita
2. Faz login com as credenciais do aluno
3. **Esperado:**
   - Se `must_change_password=True`: redirect para `change-password.html`
   - Após mudança: acesso normal ao dashboard do aluno

---

## 8. Fluxo de Formadores

Idêntico ao de alunos mas com role `trainer`. Código gerado com `F` (ex: `MATF20260001`).

### 8.1 Verificar classes do formador

1. Abre detalhe de um formador
2. **Esperado:** Lista de turmas atribuídas ao formador

---

## 9. Fluxo de Cursos e Turmas

### 9.1 Criar curso

1. Vai para `http://localhost:3000/pages/courses.html`
2. Clica em "Novo Curso"
3. Preenche nome e descrição
4. **Esperado:** Curso aparece na lista

### 9.2 Criar turma

1. Vai para `http://localhost:3000/pages/classes.html`
2. Clica em "Nova Turma"
3. Seleciona curso e formador
4. **Esperado:** Turma criada com estado "aberta"

### 9.3 Matricular aluno

1. Abre a turma
2. Clica em "Matricular Aluno"
3. Seleciona um aluno
4. **Esperado:** Matrícula aparece na lista de matrículas da turma

### 9.4 Fechar turma

1. Na turma, usa "Fechar Turma"
2. **Esperado:** Estado muda para "fechada"; novas matrículas não permitidas

### 9.5 Verificar IDOR fix (segurança)

Testa que não é possível aceder a matrículas de outra turma por manipulação de URL:

```bash
# Matrícula de turma A acessada via URL da turma B
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/classes/TURMA_B_ID/enrollments/MATRICULA_TURMA_A_ID/
# Esperado: 404 Not Found
```

---

## 10. Fluxo de Notas

### 10.1 Lançar notas

1. Vai para `http://localhost:3000/pages/grades.html`
2. Seleciona turma
3. Lança nota para uma matrícula
4. **Esperado:** Nota gravada e visível

### 10.2 Ver relatório de notas

1. Abre `http://localhost:3000/pages/reports.html`
2. Filtra por turma ou aluno
3. **Esperado:** Relatório gerado com médias e totais

### 10.3 Vista do aluno (as minhas notas)

1. Login como aluno
2. Abre o perfil ou painel
3. **Esperado:** Apenas as suas próprias notas visíveis (sem acesso a notas de outros)

---

## 11. Notificações

1. Faz uma ação que gere notificação (ex: nova matrícula, reset de password)
2. Abre o painel de notificações (ícone no header)
3. **Esperado:** Notificação aparece na lista

### 11.1 Marcar como lida

1. Clica na notificação
2. **Esperado:** Estado muda para lida; contador no header atualiza

### 11.2 Marcar todas como lidas

1. Clica em "Marcar todas como lidas"
2. **Esperado:** Contador vai a zero

---

## 12. Verificações de Segurança

### 12.1 Rate Limiting

Testa que os endpoints críticos bloqueiam após múltiplas tentativas:

```bash
# Login — 5 tentativas/minuto (ajustar conforme throttle configurado)
for i in {1..6}; do
  curl -X POST http://localhost:8000/api/auth/login/ \
    -H "Content-Type: application/json" \
    -d '{"email":"test@test.com","password":"wrong"}' \
    -w "\nHTTP %{http_code}\n"
done
# Tentativas 6+ devem retornar: HTTP 429

# Registo de instituição
for i in {1..4}; do
  curl -X POST http://localhost:8000/api/institutions/register/ \
    -H "Content-Type: application/json" \
    -d '{"institution_name":"X","admin_name":"Y","email":"x@x.com","password":"Test1234!"}' \
    -w "\nHTTP %{http_code}\n"
done
# Tentativas 4+ devem retornar: HTTP 429
```

### 12.2 Injeção XSS (verificar correção)

1. Tenta criar um aluno com nome: `<img src=x onerror=alert(1)>`
2. **Esperado:** Texto renderizado literalmente (nunca executa o script)
3. Verifica no painel de notificações também

### 12.3 Admin URL obfuscado

- `http://localhost:8000/admin/` → **Deve retornar 404**
- `http://localhost:8000/mgmt-matrika/` → Funciona

### 12.4 Tokens fora de logs

Testa que o token de reset de password vai no fragmento (`#`) e não na query string:

1. Clica num link de reset de password
2. URL deve ser: `reset-password.html#UID:TOKEN` (não `?uid=...&token=...`)
3. O servidor nunca vê o fragmento → não fica em logs

---

## 13. Onboarding Wizard

Para novas instituições (primeiro login após verificação):

1. Login como admin de instituição recém-verificada (sem dados ainda)
2. **Esperado:** Wizard de onboarding aparece com passos guiados
3. Completa os passos do wizard
4. **Esperado:** Redirect para dashboard após completar

---

## 14. Perfil e Alteração de Password

### 14.1 Alterar password pelo próprio utilizador

1. Vai para `http://localhost:3000/pages/profile.html`
2. Usa a secção de alteração de password
3. Preenche password atual + nova password
4. **Esperado:**
   - Validação de força da password (Django validators)
   - Sessão mantida após alteração (token não é invalidado — nota para melhoria futura)

### 14.2 Alterar email

1. No perfil, altera o email
2. **Esperado:** Email atualizado; sem duplicados (validação de unicidade)

---

## 15. Testes via API Direta (curl / Postman)

Para testes mais rápidos sem UI:

### Autenticação completa

```bash
# 1. Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@exemplo.com","password":"Password123!"}' \
  -c cookies.txt

# Resposta tem "access" no body; "refresh_token" cookie guardado em cookies.txt

# 2. Usar access token
ACCESS=$(curl -s -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@exemplo.com","password":"Password123!"}' | python -c "import sys,json; print(json.load(sys.stdin)['access'])")

# 3. Chamar endpoint autenticado
curl http://localhost:8000/api/auth/me/ \
  -H "Authorization: Bearer $ACCESS"

# 4. Refresh (usa cookie)
curl -X POST http://localhost:8000/api/auth/refresh/ \
  -b cookies.txt \
  -c cookies.txt

# 5. Logout
curl -X POST http://localhost:8000/api/auth/logout/ \
  -H "Authorization: Bearer $ACCESS" \
  -b cookies.txt
```

---

## 16. Checklist de Regressão Rápida

Antes de cada release, percorre esta checklist:

- [ ] Registo de instituição → email chega → verificação funciona
- [ ] Login com instituição não verificada → bloqueado e redireccionado
- [ ] Login com instituição verificada → dashboard OK
- [ ] Logout → cookie removido, acesso negado
- [ ] Silent refresh → access token renovado sem login
- [ ] Reset de password → email com link hash → reset funciona
- [ ] Criar aluno sem email → código `@local.academico` gerado
- [ ] Criar aluno com email → email com password enviado
- [ ] Matricular aluno → nota lançada → relatório correto
- [ ] Rate limiting → 429 após exceder limite
- [ ] Admin URL `admin/` → 404
- [ ] XSS → texto literal, nunca script executado
- [ ] IDOR → matrícula de outra turma → 404

---

## 17. Melhorias Identificadas Para Futura Iteração

| # | Área | Descrição |
|---|------|-----------|
| 1 | Verificação | Adicionar endpoint real de reenvio de email de verificação (atualmente redireciona para login) |
| 2 | Auth | Invalidar access tokens na base de dados após logout (hoje só o refresh é blacklistado) |
| 3 | Auth | Após alterar password, invalidar sessões abertas noutros dispositivos |
| 4 | Email | Template HTML do email de verificação (atualmente texto plano) |
| 5 | UX | Loading state mais detalhado no wizard de onboarding |
| 6 | Segurança | Adicionar TOTP/2FA para admins de instituição |
| 7 | API | Paginação nos endpoints de lista (alunos, turmas, notas) |
| 8 | Logs | Audit log de ações sensíveis (criação/remoção de memberships, alterações de role) |
