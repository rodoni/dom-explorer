# 🌐 DOM Explorer MCP Server

Um servidor **MCP (Model Context Protocol)** e ecossistema de automação inteligente em **Python** para exploração interativa do Document Object Model (DOM) e geração de seletores e Page Objects resilientes para o **Robot Framework** (suportando tanto a **Browser Library** quanto a **SeleniumLibrary**).

---

## 🚀 Funcionalidades

- **Inspeção Interativa em Navegador Visível (*Headful*)**:
  - Abre uma janela real do Google Chrome / Chromium na URL fornecida.
  - Injeta automaticamente um script de overlay com destaque visual (*bounding box*), tooltip informativo e barra de controle flutuante.
  - Intercepta cliques de inspeção sem disparar navegações acidentais em botões ou links.
  - Alternância rápida entre **Modo Inspeção** e **Modo Navegação Livre**.
- **Extração Completa de Metadados do DOM**:
  - Tags HTML, IDs, classes, nomes, placeholders, tipos e textos visíveis.
  - Atributos de acessibilidade (`role`, `aria-label`) e de teste (`data-testid`, `data-test`, `data-cy`, `data-qa`).
  - Hierarquia de elementos pais (*parent chain*) e coordenadas de renderização (*bounding box*).
- **Gerador de Locators & Variáveis para Robot Framework**:
  - Converte seletores automaticamente para **Browser Library** (`id=...`, `role=button[name="..."]`, `text="..."`, `[data-testid="..."]`) e **SeleniumLibrary** (`id:...`, `name:...`, `xpath:...`, `css:...`).
  - Algoritmo de descarte de IDs dinâmicos de frameworks (como `:r0:`, `ext-gen-123`, `ember456`).
  - Nomenclatura padronizada de variáveis (ex: `${BTN_SUBMIT_LOGIN}`, `${INPUT_EMAIL_USUARIO}`).
- **Varredura Textual e Semântica (`scan_elements`)**:
  - Mapeia elementos em lote por tag, role ou texto visível direto pelo Agente sem precisar clicar em cada um manualmente.
- **Validação e Destaque Visual (`highlight_element`)**:
  - Testa qualquer seletor na página aberta, garantindo unicidade (`match_count == 1`) e destacando-o na cor vermelha.
- **Exportação de Page Objects (`export_robot_resource`)**:
  - Gera arquivos `.resource` completos contendo `*** Settings ***`, `*** Variables ***` e `*** Keywords ***` reutilizáveis.

---

## 📦 Instalação e Configuração

### Pré-requisitos

- Python 3.10 ou superior.
- Ferramenta [uv](https://docs.astral.sh/uv/) instalada.

### Instalação das Dependências

```bash
git clone <repo-url> dom-explorer
cd dom-explorer

# Sincronizar dependências do ambiente virtual
uv sync

# Instalar os binários do navegador Playwright
uv run playwright install chromium
```

---

## ⚙️ Configuração nos Clientes MCP

### 1. Kilo Code

No **Kilo Code**, os servidores MCP são configurados dentro do arquivo principal de configuração do Kilo (**`kilo.jsonc`** ou **`.kilo/kilo.jsonc`**), sob a chave raiz **`"mcp"`**.

#### Onde configurar:
- **Nível de Projeto (Recomendado)**: Crie ou edite `.kilo/kilo.jsonc` (ou `kilo.jsonc`) na raiz do seu projeto.
- **Nível Global**: `~/.config/kilo/kilo.jsonc` (aplica-se a todos os projetos).

#### Via Interface do Kilo Code (VS Code Extension):
1. Clique no ícone de **Configurações** (⚙️) na barra lateral do Kilo Code.
2. Clique na aba **Agent Behaviour** à esquerda.
3. Acesse a sub-aba **MCP Servers**.
4. Clique em **Add Server**, selecione **Local (stdio)** e informe o comando.

#### Configuração JSON (`.kilo/kilo.jsonc` ou `~/.config/kilo/kilo.jsonc`):

```jsonc
{
  "mcp": {
    "dom-explorer": {
      "type": "local",
      "command": [
        "uv",
        "run",
        "--directory",
        "/home/odoni_r/projects/dom-explorer",
        "dom-explorer"
      ],
      "enabled": true,
      "timeout": 30000
    }
  },
  "permission": {
    "dom-explorer_*": "allow"
  }
}
```

> [!TIP]
> - **Formato de comando**: O campo `"command"` deve ser uma lista com o executável e seus argumentos.
> - **Permissões automáticas**: A chave `"permission": { "dom-explorer_*": "allow" }` permite que o Kilo Code execute as ferramentas do DOM Explorer sem abrir caixas de diálogo para confirmação manual a cada inspeção de elemento.
> - **Verificação via CLI do Kilo**: Você pode listar e depurar a conexão executando:
>   ```bash
>   kilo mcp list
>   kilo mcp debug dom-explorer
>   ```

---

### 2. Antigravity IDE / Claude Desktop / Cursor

Adicione a entrada correspondente no seu arquivo de configuração (`mcp_config.json` ou `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "dom-explorer": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/home/odoni_r/projects/dom-explorer",
        "dom-explorer"
      ]
    }
  }
}
```

---

## 🛠️ Ferramentas Disponíveis no MCP (`Tools`)

| Ferramenta | Parâmetros | Descrição |
|---|---|---|
| `launch_browser` | `url: str`, `headless: bool = False`, `browser_type: str = "chromium"` | Abre o navegador na URL indicada e ativa o inspetor visual. |
| `get_selected_element` | *nenhum* | Retorna os dados detalhados do último elemento clicado/selecionado pelo usuário. |
| `get_selection_history` | *nenhum* | Lista o histórico de todos os elementos inspecionados durante a sessão atual. |
| `scan_elements` | `selector: str`, `tag: str`, `role: str`, `text: str`, `limit: int = 25` | Varre o DOM buscando elementos interativos por critérios textuais ou semânticos. |
| `highlight_element` | `selector: str` | Destaca visualmente um elemento na página e valida se o seletor é único. |
| `export_robot_resource`| `page_name: str`, `library: str = "Browser"` | Gera o conteúdo completo de um arquivo `.resource` com Page Object e Keywords. |
| `close_browser` | *nenhum* | Encerra o navegador e finaliza a sessão. |

---

## 🧪 Execução de Testes

Os testes cobrem unitariamente a geração de seletores, detecção de IDs dinâmicos, validação de schemas MCP e ciclo de vida Playwright:

```bash
uv run pytest -v
```

---

## 📝 Exemplo de Arquivo `.resource` Gerado

```robot
*** Settings ***
Documentation    Page Object Resource para LoginPage
Library          Browser

*** Variables ***
${INPUT_USER}                     id=user-name
${INPUT_PASSWORD}                 id=password
${BTN_LOGIN}                      [data-testid="login-submit-btn"]

*** Keywords ***
Fill Input User
    [Arguments]    ${value}
    [Documentation]    Preenche o campo Input User com o valor informado
    Fill Text    ${INPUT_USER}    ${value}

Fill Input Password
    [Arguments]    ${value}
    [Documentation]    Preenche o campo Input Password com o valor informado
    Fill Text    ${INPUT_PASSWORD}    ${value}

Click Btn Login
    [Documentation]    Clica no botão Btn Login
    Click    ${BTN_LOGIN}
```
