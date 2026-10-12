# Status do Minecraft Blocktopia

Referência documental: 11/10/2026 (America/Sao_Paulo).
Base auditada: [main em 3e52f72](https://github.com/alexcarlos06/blocktopia-minecraft/tree/3e52f72a8cc99a570945ba8ca1a69a1602790b75).
Esta atualização é exclusivamente documental; não houve acesso, implantação ou teste na VPS.

## Como interpretar

- **Implementado/versionado:** existe no código da base auditada; não comprova execução.
- **Executado e confirmado na VPS (relato):** evidência informada pelo administrador; não é uma nova inspeção do ambiente.
- **Histórico:** implantação/decisão registrada, sem garantia de permanência.
- **Proposto:** evolução ainda não executada.
- **Pendente:** falta validação ou evidência para concluir.

Fontes: arquivos reais da main; BLOCKTOPIA-CONTEXTO.md fornecido como referência local do projeto; conversa “Instruções para construir” (ID 6acba3af-c0c4-83e8-8024-5802d71930e0); confirmação explicitada pelo administrador nesta solicitação. A leitura recuperada da conversa retornou mensagens recentes do usuário, mas respostas antigas apareceram apenas como referências de conteúdo, sem texto integral. Não se inferiram resultados a partir dessas referências. O contexto local não foi copiado integralmente para o repositório, pois contém identificadores pessoais.

## Última feature implementada — importação da casa por Behavior Pack

- [x] **Versionado:** pack `packs/blocktopia-structures/`, manifest, licença e estruturas `casa_inicial.mcstructure` e `house1.mcstructure`.
- [x] **Executado e confirmado na VPS por relato do administrador:** importação da casa .mcstructure por Behavior Pack, com resposta **“Loaded a structure of name blocktopia:casa_inicial”**, na origem **137 120 176**.
- [ ] Inspecionar visualmente o resultado completo, encaixe no terreno, orientação, acessos e elementos internos.
- [x] Identificador esclarecido pelo administrador: `blocktopia:casa_inicial`, conforme linha exata acima.
- [ ] Vincular ao registro técnico versão do servidor, data, evidência sanitizada e backup anterior.
- [ ] Registrar a construção no catálogo após validação.

A resposta do console confirma o carregamento relatado; não comprova habitabilidade, ausência de sobreposição ou aprovação visual. Não repetir a carga apenas para obter evidência: pode sobrescrever o mundo.

## Feature atual — inspeção e registro pós-implantação

**Pendente.** Critérios de conclusão:

- [ ] Confirmar a versão Bedrock instalada e a ativação do pack no mundo correto.
- [ ] Visitar 137 120 176 com o administrador e verificar entorno, fundação, colisões, iluminação, portas e segurança para Survival.
- [ ] Registrar capturas/evidências revisadas, sem identificadores de jogadores ou dados privados.
- [ ] Documentar dimensões, orientação, nome/namespace da estrutura e resultado da inspeção.
- [ ] Cadastrar o local em `config/adventure-locations.json` somente após aprovação.
- [ ] Atualizar este checklist com data, evidência e commit do cadastro.

O catálogo versionado está vazio (`version: 1, locations: {}`). `LocationRegistry.register()` grava diretamente `CONFIRMADO`: usar somente depois da validação humana. A documentação não cadastrou a casa como validada.

## Inventário confirmado no repositório

| Área | Implementado/versionado | Limite da evidência |
| --- | --- | --- |
| Infraestrutura | Compose, exemplo de ambiente e regras de ignore | Configuração desejada/versionada; estado vivo não inspecionado |
| Administração | Wrapper restrito de console e ações específicas de tickingarea | Presença de ações não prova áreas ativas |
| Backup | Ciclo save, cópia por lista/tamanhos e retomada; probe separado | Sem novo backup nem restauração testada nesta revisão |
| Terreno | Leitor LevelDB/NBT experimental, alturas, materiais, análise de área e volume | Formatos limitados; análise não aprova implantação |
| Construção | Engine, planos, validação, autorização, fundação, prévia e simulação | Planejamento não significa construção realizada |
| Execução | Sender, runner com backup e verifier de setblock/fill | Runner executa um comando por chamada; fill limitado a 64 blocos |
| Locais | Catálogo e busca preliminar de candidatos | Catálogo vazio; busca não autoriza construção |
| Packs | Behavior Pack de estruturas e dois binários | Ativação e estado atuais não relidos na VPS |
| Testes | 24 arquivos `tests/test_*.py`, padrão unittest | Arquivos presentes não equivalem a testes aprovados |
| Mundos | README e .gitkeep | Sem save na árvore auditada; pasta não montada no Compose |

## Testes e evidências de execução

- [x] Histórico recuperado contém tentativa de `python -m pytest tests/ -q` que falhou com `No module named pytest`.
- [x] Testes consultados utilizam `unittest.TestCase` e `unittest.mock`; não é necessário introduzir pytest para executá-los.
- [ ] Executar a suíte completa em ambiente Linux preparado e registrar comando, revisão, resultado e dependências.
- [ ] Validar integração real do console, backup e retomada de salvamento em janela controlada.
- [ ] Testar restauração em ambiente isolado.

Comando previsto, da raiz do checkout: `python3 -m unittest discover -s tests -p 'test_*.py' -v`. Não foi executado nesta atualização. Testes com mocks não demonstram execução no Bedrock. Consulte [implementação e operação](IMPLEMENTACAO.md) para dependências e limites.

## Próximas features priorizadas — propostas

O [plano do Capítulo 1](PLANO-CAPITULO-01.md) prioriza concluir a casa e preparar acampamento, trilha, ponte, vila mínima e Missão 001 com condução manual, antes de ampliar automação. As prioridades técnicas abaixo permanecem como referência; automação completa não bloqueia o MVP.

1. **P0 — concluir a feature atual:** inspeção da casa, evidências e cadastro aprovado.
2. **P1 — continuidade:** comprovar backup/retomada e restauração isolada; definir retenção e cópia privada fora da VPS.
3. **P1 — reprodutibilidade:** registrar dependências Python e versão exata do Bedrock/imagem; executar unittest e guardar evidência sanitizada.
4. **P2 — packs reproduzíveis:** procedimento revisado de instalação/ativação, controle de versão e registro das estruturas, sem reenviar automaticamente ao mundo.
5. **P2 — construções controladas:** ampliar execução por etapas e verificação somente após validar limites, terreno e recuperação; não remover o limite de 64 por conveniência.
6. **P3 — aventuras cooperativas:** locais, pistas e tesouros adequados a Henry e Nicolas; vila/guilda e Fortaleza dos Heróis continuam propostas até evidência específica.

## Histórico e configuração desejada

O contexto registra VPS Hostinger/Ubuntu, Docker, conectividade PS4 via DNS/BedrockConnect e versão de referência 1.26.52. Também menciona baús, Fortaleza, reset e ajustes de gamerules/visão. Isso é histórico, não prova de estado atual nem de implantação completa de cada proposta. Survival, Easy, dia/noite, criaturas, exploração e receitas progressivas orientam a experiência. Proteções adicionais devem ser verificadas uma a uma; não estão declaradas como aplicadas.

## Regra para próximas atualizações

Registrar por feature: objetivo, arquivos, commit, execução (ou “não executada”), evidência, validação, riscos e reversão. Marcar concluído apenas o que foi comprovado; separar publicação Git de implantação na VPS.

## Continuidade — preparação do Capítulo 1

Plano documental alinhado à main em `24878ad8c03f014630fb3e6bbbb8f329a3c18629`: [PLANO-CAPITULO-01.md](PLANO-CAPITULO-01.md). A base histórica das seções anteriores foi preservada. Nenhum cenário novo foi construído ou confirmado nesta atualização; catálogo permanece vazio, inspeção visual da casa pendente e nenhuma operação na VPS. Próxima ação: inspecionar casa e decidir região da vila versus acampamento, seguindo backup, seleção, validação e construção manual controlada.

## Continuidade — organização da história inicial

Referência: 12/10/2026 (America/Sao_Paulo), sobre a base `e3a11c349eb2c0375a84c8bad0838c7342297279`. Entrega documental em [historia/README.md](historia/README.md): capítulo, missão, contexto, requisitos de construção, scripts planejados e validação. Os critérios e procedimentos de teste antes contidos no plano foram centralizados nessa pasta; o plano mantém sequência, dependências e preparação operacional. [AGENTS.md](../AGENTS.md) orienta futuras alterações sem reproduzir a documentação.

Os textos locais citados no histórico e BLOCKTOPIA-CONTEXTO.md não estavam disponíveis no checkout. A redação narrativa é proposta para revisão, com origem e limites registrados em [Contexto e decisões](historia/CONTEXTO-E-DECISOES.md).

- **Documentado:** Capítulo 1 — O Chamado de Blocktopia, Missão 001 — Um Lar em Blocktopia, Vila Central medieval, Guilda dos Exploradores e Desaparecimento dos Guardiões.
- **Pendente:** revisão editorial, aprovação da recompensa e ensaio futuro em Bedrock/PS4 conforme [Validação](historia/VALIDACAO.md).
- **Não executado nesta entrega:** scripts de jogo, testes de integração, acesso à VPS/containers/dados persistentes/backups, construção ou deploy. Verificações documentais efetivamente realizadas ficam registradas no PR.

Não há novas coordenadas ou confirmação de implantação. As pendências operacionais anteriores permanecem; não se cadastraram locais nem se alteraram configurações, packs ou scripts.
