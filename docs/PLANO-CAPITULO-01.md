# Plano de implementação — Capítulo 1

Referência: 11/10/2026 (America/Sao_Paulo). Base inspecionada: [main em 24878ad](https://github.com/alexcarlos06/blocktopia-minecraft/tree/24878ad8c03f014630fb3e6bbbb8f329a3c18629).
**Estado: planejamento versionado; nenhuma operação na VPS nesta entrega.**

## Objetivo e decisão de escopo

Preparar uma aventura cooperativa jogável para Henry e Nicolas: Acampamento Inicial → Trilha dos Exploradores → Ponte dos Viajantes → Vila Central mínima → Missão 001 — Um Lar em Blocktopia → celebração. O adulto conduz mensagens, valida a missão e entrega a recompensa manualmente. Não é necessário automatizar missões, NPCs, recompensas ou construções para iniciar.

A história inicial já existe no projeto. Este plano organiza sua preparação física e operacional; não substitui a narrativa por uma nova. A conversa “Instruções para construir” (6acba3af-c0c4-83e8-8024-5802d71930e0) foi consultada: o texto recuperado confirma construir a casa primeiro e planejar automação depois; respostas antigas vieram como referências internas sem conteúdo integral. O escopo MVP acima foi explicitado pelo administrador no pedido atual.

A revisão original deste plano registrou leitura do contexto local BLOCKTOPIA-CONTEXTO.md e dos arquivos locais historia/CONTEXTO-E-DECISOES.md, CAPITULO-01.md e MISSAO-001-UM-LAR.md. Esses originais não estavam disponíveis na revisão documental de 12/10/2026 e não foram recuperados. A organização atual em [docs/historia](historia/README.md) explicita as fontes disponíveis e apresenta redação narrativa proposta para revisão, sem atribuí-la aos originais. Detalhes operacionais abaixo continuam propostas até aprovação/validação.

## Evidências e checklist de continuidade

### Concluído no código ou por relato

- [x] Inspeção de README, STATUS, IMPLEMENTACAO, Compose, catálogo, buildings, terrain, manifest e testes da main.
- [x] Versionados: SiteLocator, TerrainReader, FoundationPlanner, LocationRegistry, planejamento/validação e testes unittest.
- [x] Versionados: backup online, transporte/verificação restritos e Behavior Pack com casa_inicial.mcstructure e house1.mcstructure.
- [x] **Última feature executada por relato do administrador:** importação com a linha exata `Loaded a structure of name blocktopia:casa_inicial`, na origem **X=137 Y=120 Z=176**.
- [x] Plano documental do MVP preparado; isso não representa implantação.

A linha identifica casa_inicial, sem confirmar visualmente o resultado, dimensões, orientação, fundação ou habitabilidade. Não há evidência de acampamento, trilha, ponte ou vila concluídos. A coordenada da casa não define automaticamente a região da vila nem do acampamento.

### Atual — concluir a casa e escolher a região

- [ ] Inspecionar a casa existente sem recarregar a estrutura.
- [ ] Confirmar versão Bedrock, mundo e pack ativos; registrar evidência sanitizada, dimensões, orientação e volume ocupado.
- [ ] Identificar o backup anterior e comprovar recuperação em cópia isolada antes de novas alterações.
- [ ] Decidir com o administrador se a casa será apoio público, parte da vila ou apenas teste.
- [ ] Escolher regiões distintas ou próximas para vila e acampamento; vistoriar trajeto e travessia.
- [ ] Cadastrar somente locais aprovados; catálogo atual permanece vazio.

### Próximas — ordem de execução

- [ ] P0: cumprir os itens atuais e aprovar mapa simples com origens, footprints, alturas, rotas e áreas preservadas.
- [ ] P1: construir Acampamento Inicial e vistoriar.
- [ ] P1: marcar Trilha dos Exploradores e construir Ponte dos Viajantes na travessia aprovada.
- [ ] P1: preparar Vila Central mínima e mural da Missão 001.
- [ ] P1: testar o percurso completo com adulto em Survival e acesso PS4.
- [ ] P1: iniciar sessão com Henry e Nicolas; registrar conclusão e recompensa sem repetição.
- [ ] P2: ajustar frustrações observadas e documentar evidências.
- [ ] P3: planejar automação apenas após o MVP funcionar; não ampliar runner ou remover limites para antecipar a aventura.

## Decisões pendentes e dependências

| Decisão | Como resolver | Bloqueia |
| --- | --- | --- |
| Região da vila x acampamento | Visita e mapa; escolher distância confortável, relevo e expansão, sem coordenadas inventadas | Construção dos cenários |
| Papel da casa 137 120 176 | Inspeção e decisão do adulto; não confundir carga técnica com cenário aprovado | Reuso da casa e registro |
| Local da ponte | Escolher travessia curta e segura; se não houver rio, aprovar travessia sobre desnível compatível com história | Ponte e trajeto completo |
| Dimensões/orientação dos assets | Medir em cópia isolada e conferir volume destino | Qualquer nova carga |
| Texto final e recompensa | Reutilizar capítulo existente; adulto aprova material legível no PS4 e recompensa pequena | Ensaio narrativo |
| Versão e permissões administrativas | Confirmar versão real e compatibilidade; crianças permanecem member | Comandos e pack, se necessários |

Dependências: backup recuperável → inspeção/seleção → revisão de volume e fundação → construção por etapa → inspeção → registro → ensaio completo → sessão. Uma falha interrompe somente a etapa dependente; não justifica reconstruir todo o mundo.

## Reaproveitamento da infraestrutura existente

| Caminho existente | Papel no MVP | Limite |
| --- | --- | --- |
| compose.yaml | Bedrock Docker, serviço minecraft/container blocktopia | Não alterar nem atualizar imagem neste plano; latest não fixa versão |
| scripts/backup/backup-world.py | Backup antes de cada etapa que altera cenário | Linux/fcntl, Docker e caminhos fixos; exige cópia e save resume confirmados |
| scripts/backup/probe-save-cycle.sh | Diagnóstico específico do ciclo save, se necessário | Não produz backup; não executar junto do backup |
| scripts/terrain/terrain_reader.py | TerrainReader sobre cópia consistente privada | Experimental, amulet_nbt/leveldb; nunca abrir banco ativo |
| scripts/terrain/{analyzer,materials,volume_analyzer,building_validation}.py | Análise preliminar de alturas, materiais, obstáculos e volume | Dados ausentes não são ar; análise não autoriza construção |
| scripts/buildings/site_locator.py | SiteLocator.find(reference, footprint_size, min_distance, max_distance) | Sugestões PENDENTE, execution_allowed=false; até 5.000 candidatos; alturas incompletas descartadas |
| scripts/buildings/foundation.py | FoundationPlanner.plan(footprint, base_y, strategy) | NATURAL/LEVEL/ELEVATED são planejamento; validar terreno real |
| scripts/buildings/{plan,validator,authorization,preview,foundation_commands}.py | Revisar plano, autorização, prévia e comandos | Não substituem inspeção humana; não são um instalador de aventuras |
| scripts/buildings/construction_runner.py | Eventual setblock/fill pontual com backup/verificação | Um comando por chamada, DRY_RUN/FORCE, fill até 64; não suporta structure load |
| scripts/buildings/{bedrock_sender,bedrock_verifier,executor,engine}.py | Transporte, verificações e geração existentes | Envio não confirma colocação; engine até 32.768 não amplia limite do runner |
| scripts/buildings/location_registry.py | LocationRegistry.register e reference | register escreve CONFIRMADO diretamente; usar após validação |
| config/adventure-locations.json | Catálogo versionado de locais aprovados | version=1, locations vazio; não inserir coordenadas candidatas como confirmadas |
| packs/blocktopia-structures/ | Pack existente, manifest e licença | Dois assets disponíveis; nenhum asset de ponte/vila/acampamento confirmado |
| scripts/admin/bedrock-command.sh | Operações administrativas restritas | Não assumir suporte a structure load; ações tickingarea têm coordenadas fixas |
| scripts/build-hero-base.py | Gerador histórico da Fortaleza | Fora do MVP; não usar como substituto da vila |
| tests/test_*.py | Regressão dos componentes existentes | Mocks não comprovam Bedrock nem cenário jogável |

Não criar wrappers, scripts de missão, instalador ou novos packs nesta entrega. Registrar futuras coordenadas aprovadas com IDs coerentes como acampamento_inicial, ponte_viajantes e vila_central; a trilha exige também seus pontos de passagem documentados, pois o catálogo atual registra um ponto por local.

Infraestrutura de referência: checkout /home/alexcsousa/projects/minecraft-bedrock-server; dados /home/alexcsousa/projects/minecraft-data; backups /home/alexcsousa/projects/minecraft-backups. São referências do projeto, não caminhos relidos nesta VPS.

## Critérios de aceite por cenário

Consultar [requisitos de construção](historia/REQUISITOS-DE-CONSTRUCAO.md) para os mínimos de cada cenário, critérios da Missão 001, direção medieval da vila e proposta de recompensa. Essa é a fonte dos requisitos; este plano mantém sequência, dependências e procedimento de preparação.

## Procedimento futuro de construção manual controlada

**Não executado nesta entrega.** Uma etapa por vez, conduzida pelo administrador:

1. Confirmar mundo/versão, regras Survival/Easy, acesso e permissões; revisar compatibilidade antes de usar comandos. A versão 1.26.52 é histórica.
2. Revisar backup-world.py e caminhos/montagem reais. Fazer backup concluído e confirmar salvamento retomado; preservar separadamente packs/listas de ativação/configurações privadas. Ensaiar restauração isolada.
3. Visitar casa atual. Não repetir carga para validar. Corrigir só após plano e novo backup quando necessário.
4. Selecionar candidatos com inspeção e, opcionalmente, SiteLocator/TerrainReader sobre cópia privada. Validar materiais, volume inteiro, obstáculos, acessos, fundação e sobreposições; aprovar origem e orientação.
5. Preferir construção manual simples de acampamento, trilha, ponte e praça. Para nova estrutura reutilizada, revisar licença, asset, dimensões e destino em cópia isolada primeiro. O pack existente não contém os quatro cenários prontos.
6. Se uma nova carga for aprovada, conferir ativação do pack e sintaxe na versão instalada; emitir um único comando revisado pelo console. O comando histórico foi `structure load blocktopia:casa_inicial 137 120 176`: referência da carga existente, **não instrução para repeti-la**. Para outro destino, gerar comando somente após coordenadas/volume aprovados.
7. Conferir resposta do console e resultado visual separadamente. Em timeout/resultado indeterminado, inspecionar antes de qualquer nova tentativa. Não contornar backup usando sender diretamente.
8. Aprovar o cenário, registrar coordenadas/evidência e atualizar catálogo/checklist em commit próprio; seguir para próxima etapa.

Comandos existentes, para futura operação revisada na raiz do checkout Linux:

```bash
# Altera o ciclo save e cria backup: executar somente na preparação operacional.
python3 scripts/backup/backup-world.py
# Acesso ao console quando necessário.
docker attach blocktopia
```

No console, comandos sem / inicial. Desconectar com Ctrl+P, depois Ctrl+Q; nunca Ctrl+C. O histórico registra falha de permissão com send-command. Não presumir que todo wrapper aceita importação.

## Testes e registro de evidências

Os procedimentos foram centralizados em [historia/VALIDACAO.md](historia/VALIDACAO.md): revisão documental, testes de código quando aplicáveis, ensaio futuro em Bedrock/PS4 e registro de evidências. A publicação deste plano não executa essas etapas no jogo.

## Riscos, implantação e rollback

- Carga de estrutura/fill/setblock pode sobrescrever blocos inclusive interiores. Revisar volume e proteger construções dos jogadores; nenhum reenvio automático.
- Terreno experimental pode estar incompleto ou incompatível. Falha/None bloqueia uso daquela análise; optar por inspeção manual, sem inventar dados.
- Backup online cobre mundo listado, não todo /data. Ausência de retomada ou backup parcial bloqueia construção; verificar console e recuperar salvamento antes de seguir.
- Cheats, OP, atualização de imagem e mudança de pack podem alterar experiência/interromper partidas. Não mudar configurações para publicar este plano; se necessárias no futuro, planejar separadamente.
- VPS compartilhada: restringir qualquer futura operação a minecraft/blocktopia. Não parar outros serviços, usar parada global ou limpeza Docker.
- Reverter Git não remove blocos. Desativar pack também não desfaz carga.

**Implantação desta entrega:** publicar Markdown por branch/PR e revisão; merge documental não exige acessar VPS, reiniciar container, baixar imagem ou executar scripts.

**Rollback documental:** após merge, usar `git revert SHA_DO_COMMIT` em checkout revisado e publicar a reversão. Antes do merge, basta não integrar/fechar o PR.

**Rollback de futura construção:** interromper novas alterações, preservar estado atual e avaliar reparo local controlado ou recuperação do backup anterior. Testar backup/versão/packs em ambiente isolado; confirmar caminhos absolutos e janela com administrador antes de parar somente minecraft e restaurar. Restauração global pode perder progresso posterior: explicitar impacto. Não limpar com fill air nem restaurar automaticamente. Ver [IMPLEMENTACAO.md](IMPLEMENTACAO.md#backup-e-recuperação).

## Entregas e commits futuros

| Ordem | Commit sugerido | Conteúdo e condição |
| --- | --- | --- |
| Atual | docs: planeja preparação do capítulo 1 | Este plano, links e status corrigido; sem operação |
| 1 | docs: valida casa inicial e decide regiões | Evidência visual sanitizada, versão, mapa e decisões reais |
| 2 | feat: registra locais aprovados do capítulo 1 | config/adventure-locations.json apenas para pontos confirmados; roteiro/footprints em docs |
| 3 | docs: registra preparação dos cenários do capítulo 1 | Uma etapa por vez; comandos revisados somente se necessários, backups referenciados sem conteúdo |
| 4 | docs: registra ensaio e aceite do capítulo 1 | Resultados reais dos unittests, ensaio PS4 e pendências resolvidas |
| 5 | docs: planeja automação após aventura validada | Escopo orientado por problemas observados; sem condicionar diversão a automação completa |

Cada commit futuro deve dizer o que foi somente planejado, executado e validado. Histórico não é evidência de permanência. STATUS acompanha implementação; este plano não promove nenhum cenário a concluído sem vistoria.
