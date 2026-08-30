*** Settings ***
Documentation    Page Object Resource para PocketFitPage
Library          Browser

*** Variables ***
${ELEM_DIV}                         css=div
${ELEM_PULAR}                       css=div
${BTN_PULAR}                        role=button[name="Pular"]
${ELEM_FITPRO}                      css=div
${ELEM_DIV_1}                       css=div
${ELEM_SVG}                         css=svg
${ELEM_PATH}                        css=path
${ELEM_PATH_1}                      css=path
${ELEM_PATH_2}                      css=path
${ELEM_PATH_3}                      css=path
${ELEM_PATH_4}                      css=path
${ELEM_FITPRO_1}                    text="FitPro"
${ELEM_PRO}                         text="Pro"
${ELEM_DIV_2}                       css=div
${ELEM_DIV_3}                       css=div
${ELEM_DIV_4}                       css=div
${ELEM_SVG_1}                       css=svg
${ELEM_CIRCLE}                      css=circle
${ELEM_CIRCLE_1}                    css=circle
${ELEM_CIRCLE_2}                    css=circle
${TITLE_TREINOS_PERSONALIZADOS}     text="Treinos Personalizados"
${ELEM_P}                           css=p
${ELEM_DIV_5}                       css=div
${BTN_BUTTON}                       css=button
${BTN_BUTTON_1}                     css=button
${BTN_BUTTON_2}                     css=button
${BTN_PROXIMO}                      role=button[name="Próximo"]
${ELEM_SVG_2}                       css=svg
${ELEM_PATH_5}                      css=path

*** Keywords ***

Validate Elem Div Is Visible
    [Documentation]    Verifica se Elem Div está visível na tela
    Wait For Elements State    ${ELEM_DIV}    visible    timeout=10s

Validate Elem Pular Is Visible
    [Documentation]    Verifica se Elem Pular está visível na tela
    Wait For Elements State    ${ELEM_PULAR}    visible    timeout=10s

Click Btn Pular
    [Documentation]    Clica no botão Btn Pular
    Click    ${BTN_PULAR}

Validate Elem Fitpro Is Visible
    [Documentation]    Verifica se Elem Fitpro está visível na tela
    Wait For Elements State    ${ELEM_FITPRO}    visible    timeout=10s

Validate Elem Div 1 Is Visible
    [Documentation]    Verifica se Elem Div 1 está visível na tela
    Wait For Elements State    ${ELEM_DIV_1}    visible    timeout=10s

Validate Elem Svg Is Visible
    [Documentation]    Verifica se Elem Svg está visível na tela
    Wait For Elements State    ${ELEM_SVG}    visible    timeout=10s

Validate Elem Path Is Visible
    [Documentation]    Verifica se Elem Path está visível na tela
    Wait For Elements State    ${ELEM_PATH}    visible    timeout=10s

Validate Elem Path 1 Is Visible
    [Documentation]    Verifica se Elem Path 1 está visível na tela
    Wait For Elements State    ${ELEM_PATH_1}    visible    timeout=10s

Validate Elem Path 2 Is Visible
    [Documentation]    Verifica se Elem Path 2 está visível na tela
    Wait For Elements State    ${ELEM_PATH_2}    visible    timeout=10s

Validate Elem Path 3 Is Visible
    [Documentation]    Verifica se Elem Path 3 está visível na tela
    Wait For Elements State    ${ELEM_PATH_3}    visible    timeout=10s

Validate Elem Path 4 Is Visible
    [Documentation]    Verifica se Elem Path 4 está visível na tela
    Wait For Elements State    ${ELEM_PATH_4}    visible    timeout=10s

Validate Elem Fitpro 1 Is Visible
    [Documentation]    Verifica se Elem Fitpro 1 está visível na tela
    Wait For Elements State    ${ELEM_FITPRO_1}    visible    timeout=10s

Validate Elem Pro Is Visible
    [Documentation]    Verifica se Elem Pro está visível na tela
    Wait For Elements State    ${ELEM_PRO}    visible    timeout=10s

Validate Elem Div 2 Is Visible
    [Documentation]    Verifica se Elem Div 2 está visível na tela
    Wait For Elements State    ${ELEM_DIV_2}    visible    timeout=10s

Validate Elem Div 3 Is Visible
    [Documentation]    Verifica se Elem Div 3 está visível na tela
    Wait For Elements State    ${ELEM_DIV_3}    visible    timeout=10s

Validate Elem Div 4 Is Visible
    [Documentation]    Verifica se Elem Div 4 está visível na tela
    Wait For Elements State    ${ELEM_DIV_4}    visible    timeout=10s

Validate Elem Svg 1 Is Visible
    [Documentation]    Verifica se Elem Svg 1 está visível na tela
    Wait For Elements State    ${ELEM_SVG_1}    visible    timeout=10s

Validate Elem Circle Is Visible
    [Documentation]    Verifica se Elem Circle está visível na tela
    Wait For Elements State    ${ELEM_CIRCLE}    visible    timeout=10s

Validate Elem Circle 1 Is Visible
    [Documentation]    Verifica se Elem Circle 1 está visível na tela
    Wait For Elements State    ${ELEM_CIRCLE_1}    visible    timeout=10s

Validate Elem Circle 2 Is Visible
    [Documentation]    Verifica se Elem Circle 2 está visível na tela
    Wait For Elements State    ${ELEM_CIRCLE_2}    visible    timeout=10s

Validate Title Treinos Personalizados Is Visible
    [Documentation]    Verifica se Title Treinos Personalizados está visível na tela
    Wait For Elements State    ${TITLE_TREINOS_PERSONALIZADOS}    visible    timeout=10s

Validate Elem P Is Visible
    [Documentation]    Verifica se Elem P está visível na tela
    Wait For Elements State    ${ELEM_P}    visible    timeout=10s

Validate Elem Div 5 Is Visible
    [Documentation]    Verifica se Elem Div 5 está visível na tela
    Wait For Elements State    ${ELEM_DIV_5}    visible    timeout=10s

Click Btn Button
    [Documentation]    Clica no botão Btn Button
    Click    ${BTN_BUTTON}

Click Btn Button 1
    [Documentation]    Clica no botão Btn Button 1
    Click    ${BTN_BUTTON_1}

Click Btn Button 2
    [Documentation]    Clica no botão Btn Button 2
    Click    ${BTN_BUTTON_2}

Click Btn Proximo
    [Documentation]    Clica no botão Btn Proximo
    Click    ${BTN_PROXIMO}

Validate Elem Svg 2 Is Visible
    [Documentation]    Verifica se Elem Svg 2 está visível na tela
    Wait For Elements State    ${ELEM_SVG_2}    visible    timeout=10s

Validate Elem Path 5 Is Visible
    [Documentation]    Verifica se Elem Path 5 está visível na tela
    Wait For Elements State    ${ELEM_PATH_5}    visible    timeout=10s
