---
name: robot-dom-explorer
description: Guia e melhores práticas para inspeção do DOM e geração de automação de testes com Robot Framework (Browser Library e SeleniumLibrary).
---

# Robot DOM Explorer - QA Automation Skill

Esta skill instrui o agente de IA a conduzir sessões de exploração do Document Object Model (DOM) em páginas web com foco na criação de automação de testes robusta e de alta manutenibilidade com o **Robot Framework**.

## 1. Fluxo de Trabalho Recomendado

1. **Inicialização**:
   - Chame a ferramenta `launch_browser(url="...")`. O navegador abrirá visível (*headful*) na tela do usuário com o inspetor ativado.
   - Oriente o usuário: *"O navegador foi aberto. Você pode navegar e clicar nos elementos que deseja automatizar. Ao clicar, o elemento será destacado e os metadados capturados."*

2. **Captura Interativa**:
   - Conforme o usuário clica em botões, campos de texto ou menus, use `get_selected_element()` para obter os metadados do elemento atual.
   - Use `get_selection_history()` para revisar a sequência de elementos já inspecionados.

3. **Varredura Textual / Semântica (Scan)**:
   - Se o usuário pedir para mapear uma tela ou formulário inteiro (ex: *"Mapeie o formulário de cadastro"*), utilize a ferramenta `scan_elements()`:
     - `scan_elements(tag="input")` para listar todos os inputs.
     - `scan_elements(text="Cadastrar")` para localizar elementos com determinado texto.
     - `scan_elements(role="button")` para localizar botões acessíveis.

4. **Validação de Unicidade**:
   - Antes de finalizar a escolha de um seletor, utilize `highlight_element(selector)` para garantir que `match_count == 1` e que o contorno visual é exibido no elemento correto.

5. **Geração de Recursos do Robot Framework**:
   - Utilize `export_robot_resource(page_name="NomeDaPagina", library="Browser")` para gerar a estrutura completa do Page Object.
   - Apresente ao usuário o arquivo `.resource` com variáveis padronizadas e Keywords de ação.

---

## 2. Pirâmide de Prioridade de Locators

Ao recomendar locators para o usuário ou nos scripts de teste, siga rigorosamente a ordem de resiliência:

| Prioridade | Tipo de Seletor | Exemplo Browser Library | Exemplo SeleniumLibrary | Motivo |
|---|---|---|---|---|
| **1 (Ideal)** | Test ID | `[data-testid="submit-login"]` | `css:[data-testid="submit-login"]` | Não quebra com mudanças de CSS ou texto |
| **2 (Excelente)**| ID Semântico Estável | `id=login-button` | `id:login-button` | Rápido e único (descartar IDs dinâmicos) |
| **3 (Muito Bom)**| Role + Acessibilidade | `role=button[name="Entrar"]` | `xpath://button[@aria-label='Entrar']` | Garante fidelidade com o usuário real |
| **4 (Bom)** | Texto Visível Estável | `text="Continuar"` | `link:Continuar` | Natural para botões e links |
| **5 (Aceitável)**| Atributo Name / Placeholder | `[name="username"]` | `name:username` | Comum em campos de formulários |
| **6 (Evitar se possível)** | CSS complexo / XPath relativo | `css=form.auth > button.btn` | `xpath://form//button[contains(@class,'btn')]` | Frágil a refatorações de layout |
| **PROIBIDO** | XPath Absoluto | `/html/body/div[2]/div[1]/...` | `/html/body/div[2]/div[1]/...` | Quebra na menor alteração do DOM |

> [!WARNING]
> **IDs Dinâmicos**: Sempre descarte IDs gerados por frameworks como `:r0:`, `ext-gen-123`, `ember432` ou números/hashes aleatórios. Nesses casos, priorize `role`, `data-testid` ou texto visível.

---

## 3. Padrão de Nomenclatura de Variáveis (.resource)

As variáveis no Robot Framework devem ser organizadas em seções `*** Variables ***` com nomes claros e descritivos:

- **Botões**: `${BTN_<ACAO_DESCRITIVA>}` (ex: `${BTN_SALVAR_CADASTRO}`)
- **Campos de Texto**: `${INPUT_<NOME_DO_CAMPO>}` (ex: `${INPUT_EMAIL_USUARIO}`)
- **Caixas de Seleção**: `${CHK_<NOME_DO_ITEM>}` (ex: `${CHK_TERMOS_DE_USO}`)
- **Botões de Opção**: `${RDO_<NOME_DO_ITEM>}` (ex: `${RDO_PESSOA_JURIDICA}`)
- **Listas Suspensas**: `${SELECT_<NOME_DA_LISTA>}` (ex: `${SELECT_ESTADO_CIVIL}`)
- **Links**: `${LINK_<TEXTO_DO_LINK>}` (ex: `${LINK_ESQUECI_SENHA}`)
- **Títulos/Labels**: `${TITLE_<TITULO>}` (ex: `${TITLE_DASHBOARD}`)

---

## 4. Exemplo de Arquivo de Recurso Gerado

```robot
*** Settings ***
Documentation    Page Object Resource para LoginPage
Library          Browser

*** Variables ***
${INPUT_USERNAME}                 id=user-name
${INPUT_PASSWORD}                 id=password
${BTN_LOGIN}                      id=login-button
${MSG_ERROR}                      [data-test="error"]

*** Keywords ***
Preencher Credenciais De Login
    [Arguments]    ${usuario}    ${senha}
    [Documentation]    Preenche o usuário e senha no formulário
    Fill Text    ${INPUT_USERNAME}    ${usuario}
    Fill Text    ${INPUT_PASSWORD}    ${senha}

Submeter Formulario De Login
    [Documentation]    Clica no botão de login
    Click    ${BTN_LOGIN}

Realizar Login Completo
    [Arguments]    ${usuario}    ${senha}
    Preencher Credenciais De Login    ${usuario}    ${senha}
    Submeter Formulario De Login
```
