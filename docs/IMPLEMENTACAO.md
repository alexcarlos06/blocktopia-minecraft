# Implementação e operação do Blocktopia

Consulte [STATUS.md](STATUS.md) antes de operar: código versionado, histórico e estado confirmado são categorias diferentes. Esta documentação descreve a main em `3e52f72a8cc99a570945ba8ca1a69a1602790b75`; nenhum comando operacional abaixo foi executado nesta atualização.

## Objetivo e arquitetura

Servidor privado Minecraft Bedrock para Henry, Nicolas, amigos e familiares, com cooperação, exploração e criatividade em Survival/Easy. Administração por SSH e Docker em VPS Hostinger/Ubuntu compartilhada com outros serviços de produção.

| Papel | Referência |
| --- | --- |
| Checkout na VPS | `/home/alexcsousa/projects/minecraft-bedrock-server` |
| Dados persistentes | `/home/alexcsousa/projects/minecraft-data` |
| Backups privados | `/home/alexcsousa/projects/minecraft-backups` |
| Serviço / container | `minecraft` / `blocktopia` |
| Imagem versionada no Compose | `itzg/minecraft-bedrock-server:latest` |

`latest` não fixa uma versão. 1.26.52 é referência histórica, não versão atual verificada. Confirmar logs e compatibilidade antes de atualização ou add-on.

## Estrutura real da base auditada

- `compose.yaml`: serviço, rede, persistência, limites e console.
- `.env.example`: parâmetros ilustrativos; `.env` é privado.
- `.gitignore`: segredos, backups e parte dos arquivos gerados.
- `config/adventure-locations.json`: catálogo vazio de locais.
- `scripts/admin/bedrock-command.sh`: comandos administrativos restritos.
- `scripts/backup/backup-world.py`: backup online.
- `scripts/backup/probe-save-cycle.sh`: sonda do ciclo de salvamento, sem cópia.
- `scripts/build-hero-base.py`: gerador da Fortaleza dos Heróis.
- `scripts/buildings/`: engine, plan, validator, authorization, foundation, foundation_commands, preview, executor, bedrock_sender, bedrock_verifier, construction_runner, location_registry e site_locator.
- `scripts/terrain/`: terrain_reader, analyzer, materials, volume_analyzer, building_validation e inicializador.
- `tests/`: testes unittest para backup, terreno, planos, fundação, autorização, transporte, verificação e execução.
- `packs/blocktopia-structures/`: LICENSE, manifest e `structures/blocktopia/{casa_inicial,house1}.mcstructure`.
- `mundos/`: orientação e marcador; sem save na árvore auditada.
- `docs/`: acompanhamento e documentação desta entrega.

Não existe `scripts/scripts/hero-base.commands.txt` na base auditada. O gerador produz arquivo em execução; não confundir saída gerada com arquivo versionado.

## Docker e configuração

O Compose declara reinício `unless-stopped`, 4 GB de memória, 2 CPUs, stdin aberto e TTY. Monta `MINECRAFT_DATA_DIR:/data`. Usa NetherNet, TCP 19132 e UDP 19140–19155. O histórico de acesso PS4 usa DNS/BedrockConnect; não diagnosticar essa configuração somente por UDP 19132.

Padrões: Survival, FORCE_GAMEMODE=true, Easy, 10 jogadores, visão 16, simulação 4, cheats=false. Autenticação online e allowlist são fixadas em true; permissão padrão member, OPS vazio por padrão. O ambiente privado pode alterar parâmetros interpolados; isso não foi verificado.

Cuidados com `.env.example`:

- Configurar localmente SERVER_UDP_PORTS e MINECRAFT_DATA_DIR; o caminho do exemplo é ilustrativo.
- Preencher jogadores e identificadores no formato aceito pela versão da imagem; UUID é placeholder.
- O exemplo ativa ALLOW_CHEATS=true temporariamente. Revisar para a operação normal.
- MINECRAFT_PORT não é consumido pelo Compose; portas estão fixas.
- ONLINE_MODE e ALLOW_LIST no exemplo não alteram os valores fixos do Compose.
- LEVEL_SEED orienta geração; mudar a variável não reseta um mundo existente.

## Console e comandos

O histórico relata falha de permissão em `docker exec blocktopia send-command`. Alternativa utilizada:

```bash
docker attach blocktopia
```

Enviar comandos Bedrock sem barra inicial. Desconectar com **Ctrl+P, depois Ctrl+Q**. **Não usar Ctrl+C** no console anexado.

O wrapper e os módulos Python procuram exatamente um processo `/data/bedrock_server-*` e escrevem no stdin usando usuário `1001:1001`. Confirmar permissões e formato do processo no ambiente real; não tratar essa implementação como API universal.

```bash
bash scripts/admin/bedrock-command.sh list
bash scripts/admin/bedrock-command.sh tickingarea-list
```

O wrapper também contém ações específicas add/remove de tickingarea (`test`, `east`, `se`) com coordenadas fixas. Elas alteram o mundo e não devem ser usadas como diagnóstico genérico. A mensagem de envio confirma transporte; verificar resposta do servidor separadamente.

## Backup e recuperação

`backup-world.py` é Linux: usa fcntl, Docker, caminhos fixos e usuário 1001:1001. Confere container ativo e montagem /data esperada. Compartilha lock `/tmp/blocktopia-save-cycle.lock` com o probe.

Fluxo implementado:

1. Envia `save hold`, consulta `save query` e espera a mensagem de arquivos prontos.
2. Valida a lista de caminhos/tamanhos do mundo Blocktopia.
3. Copia os bytes informados para diretório `.online-*.partial/worlds/Blocktopia`, com verificações de caminho, tipo, tamanho e fsync.
4. Tenta `save resume` em finally, inclusive após erro/interrupção tratável, e exige mensagem de retomada.
5. Só renomeia para `online-AAAAMMDD-HHMMSS` e anuncia conclusão se cópia e retomada forem confirmadas.

```bash
# Na VPS, somente após revisão do ambiente e autorização operacional:
python3 scripts/backup/backup-world.py
```

O probe testa hold/query/resume, sem produzir backup. Falha de resume requer conferir imediatamente o console; encerramento forçado do processo/host pode impedir a recuperação automática. Não considerar diretório parcial como backup concluído.

O script copia o mundo listado, não todo /data: pack instalado, lista de ativação, configurações e permissões exigem cópia privada separada para recuperação completa. Verificação estrutural/tamanho não equivale a restauração testada. Não há evidência nesta revisão de retenção automática, cópia externa ou teste de restauração.

Para recuperação futura: selecionar backup concluído, preservar estado anterior, testar cópia em ambiente isolado com versão compatível e, em janela acordada, parar apenas minecraft antes de substituir dados. Confirmar caminhos absolutos e preservar packs/configurações correspondentes. Reiniciar somente minecraft e validar logs, login e construção. Não fornecer restauração automática destrutiva sem confirmar backup e destino.

## Terreno e planejamento

`TerrainReader` abre LevelDB e lê NBT via `amulet_nbt` e `leveldb`. Usar apenas cópia consistente e privada, nunca o banco ativo. Abertura por biblioteca LevelDB não deve ser presumida inofensiva ao banco de produção.

Suporte experimental: subchunk versão 9 com uma camada, paleta persistente e bits suportados; chave usada sem identificador adicional de dimensão. Altura Data3D convertida por `raw_height - 65`, descrita no código como validada em amostras. Isso não comprova compatibilidade geral. Ausência retorna None; formato inválido interrompe. Dados desconhecidos não equivalem a ar.

`TerrainAnalyzer` compara alturas, materiais e obstáculos acima da superfície (até 10.000 posições de área). `volume_analyzer` analisa volume e `building_validation` estima escavação/fundação, mantendo avaliação preliminar pendente. `SiteLocator` ordena candidatos por desnível/distância, descarta alturas incompletas e não autoriza execução.

## Construção e limites

- `BuildingEngine` gera setblock/fill, limites, dimensões e footprint; valida volume fill até 32.768.
- Planos, validador, fundação, comandos de fundação e prévia organizam análise e comandos revisáveis.
- `authorize_building` distingue DRY_RUN, STRICT e FORCE; FORCE requer confirmação administrativa.
- `BuildingExecutor` valida sintaxe restrita setblock/fill, alturas -64 a 319, materiais simples e simula até 1.000 comandos. Validação sintática não comprova que todo material existe na versão instalada.
- `ConstructionRunner.execute()` aceita apenas DRY_RUN ou FORCE e **um comando por chamada**. Exige confirmação em FORCE, backup concluído/retomado e arquivos essenciais antes de enviar. Limita fill a **64 blocos**, inclusive em simulação.
- `BedrockCommandSender` confirma envio, não colocação. Não chamar diretamente para contornar backup.
- `BedrockVerifier` consulta testforblock e interpreta logs recentes como CONFIRMADO, DIVERGENTE ou INDETERMINADO. Verifica fill posição a posição até 64 blocos.
- Falha de verificação não reenvia construção. Timeout pode deixar resultado desconhecido; inspecionar antes de tentar novamente.

O limite de geração (32.768) não é o limite de execução verificada (64). A política STRICT do módulo de autorização não significa que o runner ofereça esse modo. O runner não importa .mcstructure; essa importação usa o pack e o console.

Exemplo de simulação local, sem Docker ou alteração no mundo:

```bash
python3 -c 'from scripts.buildings.construction_runner import ConstructionRunner; print(ConstructionRunner().execute("setblock 100 100 100 minecraft:stone"))'
```

Gerador histórico, somente para produzir comandos revisáveis:

```bash
python3 scripts/build-hero-base.py --x 100 --y 70 --z 100
```

Coordenadas ilustrativas; revisar destino/saída antes de usar. Não há confirmação de Fortaleza implantada.

## Behavior Pack e casa importada

Manifest: format_version 2, módulo data, versão 1.0.0 e min_engine_version 1.21.0. Essa versão mínima declarada não é teste de compatibilidade. UUID do header: `0b827b5b-10d6-4ee0-b139-32d38f1a8ae5`; UUID de módulo é diferente.

As estruturas usam namespace de caminho `blocktopia`. A licença acompanha o pack; conferir procedência e termos antes de redistribuir novos assets. Não há instalador de packs na base auditada.

Procedimento para futura implantação revisada:

1. Confirmar versão, mundo, origem e dimensões do asset; fazer backup do mundo e cópia privada dos packs/listas de ativação.
2. Copiar o diretório do pack para a área behavior_packs dos dados do servidor, preservando manifest e caminho structures.
3. Mesclar a ativação em `worlds/Blocktopia/world_behavior_packs.json` usando UUID do **header** e versão [1,0,0]; preservar outros packs e validar JSON. Não substituir a lista inteira por um único pack.
4. Programar reinício somente do serviço minecraft se necessário para carregar a alteração, conferir logs de packs e compatibilidade.
5. Revisar origem, orientação e volume afetado antes do comando de carga. Exemplo de sintaxe a validar na versão instalada: `structure load blocktopia:casa_inicial 137 120 176`. Este exemplo não comprova qual asset foi usado historicamente e **não deve ser repetido para validar a casa existente**.
6. Conferir console, inspeção visual e cadastro conforme STATUS.

O administrador confirmou “Loaded a structure” em 137 120 176. Inspeção visual e registro continuam pendentes. Remover/desativar o pack não remove blocos já colocados. Para desfazer carga, usar recuperação revisada de backup anterior; não limpar a área com fill air indiscriminadamente.

## Testes unittest e dependências

Da raiz, em Linux com ambiente preparado:

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

A suíte usa unittest/mock; a tentativa histórica com pytest falhou porque ele não estava instalado. Não instalar pytest só para substituir esse comando. O leitor importa `amulet_nbt` e `leveldb`; o backup importa fcntl, indisponível no Python Windows padrão. A base auditada não contém arquivo de dependências Python fixadas. Registrar versões compatíveis em ambiente isolado antes de declarar a suíte reproduzível.

Há testes de parsing/cópia de backup, terreno, validação, autorização, engine, planos/prévias, fundação, catálogo/busca, transporte, divergência/verificação e runner setblock/fill. Mocks não validam conexão Docker ou mundo real. Nesta entrega houve revisão documental; não se executou a suíte nem integração na VPS.

## Implantação futura, validação e Git

Em novo checkout:

```bash
git clone https://github.com/alexcarlos06/blocktopia-minecraft.git
cd blocktopia-minecraft
cp .env.example .env
# Preencher .env localmente; aceitar EULA somente após revisão dos termos.
docker compose config --quiet
```

Na VPS existente, verificar checkout limpo, commit aprovado, volume, ambiente e backup antes de atualizar. Documentação sozinha não exige reinício. Não executar pull de imagem apenas para atualizar documentos.

Após revisão e backup, somente quando houver alteração operacional aprovada:

```bash
docker compose up -d minecraft
docker compose ps minecraft
docker compose logs --tail=100 minecraft
```

up pode recriar container e interromper partidas. Confirmar versão, montagem, login autorizado, pack e resultado pretendido. Não publicar logs completos ou saída interpolada de compose config; podem conter dados privados.

Versionar somente arquivos revisados e usar commit descritivo; registrar SHA e evidência em STATUS. Reverter documentação/código com `git revert SHA_DO_COMMIT` e revisão do diff. Git revert não restaura mundo, configuração privada nem migração de versão. A reversão desta entrega é documental e não requer ação na VPS.

## Segurança e serviços compartilhados

Não publicar .env, senhas, tokens, chaves, IPs privados, XUIDs, saves, bancos LevelDB ou backups. .gitignore não remove itens já rastreados. A pasta mundos não é montada pelo Compose; esta entrega mantém apenas sua documentação, sem importar dados. O README histórico dessa pasta descreve cópia autorizada, mas a orientação atual é manter saves privados.

Preservar autenticação/allowlist e não conceder OP às crianças por padrão. Revisar cheats e permissões conforme a atividade administrativa. Backup antes de resets, atualizações, packs ou alterações extensas; testar uma alteração por vez. Usar comandos sempre restritos a minecraft/blocktopia. Não usar docker system prune, parada global ou alterações nos outros serviços da VPS.

## Referências técnicas

- [Imagem itzg para Bedrock](https://github.com/itzg/docker-minecraft-bedrock-server)
- [Docker Compose](https://docs.docker.com/compose/)
- [Conteúdo e caminhos de packs — Microsoft](https://learn.microsoft.com/en-us/minecraft/creator/documents/comprehensivepackcontents?view=minecraft-bedrock-stable)
- [Exemplo oficial de estruturas em Behavior Pack](https://learn.microsoft.com/en-us/samples/microsoft/minecraft-samples/structure-blocks-sample-behavior-pack/)
- [Sintaxe de structure — MicrosoftDocs](https://github.com/MicrosoftDocs/minecraft-creator/blob/main/creator/Commands/commands/structure.md)

Referências explicam o procedimento; não são evidência de implantação do Blocktopia.
