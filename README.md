# Blocktopia — Minecraft Bedrock

Servidor privado para aventuras cooperativas, exploração e construções em família, com foco em Henry e Nicolas. Este repositório organiza infraestrutura, automações e estruturas; o mundo ativo permanece privado na VPS.

## Estado do projeto

Leia [docs/STATUS.md](docs/STATUS.md) para o checklist de última feature, feature atual e próximas prioridades, com distinção entre código versionado, execução confirmada por relato, histórico e propostas.

A última feature confirmada pelo administrador é a importação da casa .mcstructure por Behavior Pack, com “Loaded a structure” em **137 120 176**. A **inspeção visual, validação pós-implantação e registro da construção continuam pendentes**. O catálogo de locais da base auditada está vazio.

A documentação foi conferida contra a main em `3e52f72a8cc99a570945ba8ca1a69a1602790b75`. Publicação de código/documentação não comprova implantação. Não houve acesso à VPS nesta atualização.

## Documentação

- [Status e checklist](docs/STATUS.md): evidências, pendências e prioridades.
- [Implementação e operação](docs/IMPLEMENTACAO.md): Docker, backups, terreno, construção, testes, packs, implantação e reversão.
- [Orientações históricas sobre cópias de mundos](mundos/README.md): consistência e privacidade. Manter saves e backups privados; esta entrega não inclui dados do mundo.

## Estrutura atual

```text
compose.yaml
.env.example
.gitignore
config/adventure-locations.json
docs/
  STATUS.md
  IMPLEMENTACAO.md
scripts/
  admin/bedrock-command.sh
  backup/backup-world.py
  backup/probe-save-cycle.sh
  build-hero-base.py
  buildings/                  # planejamento, execução restrita e verificação
  terrain/                    # leitura experimental e análise de cópia do mundo
tests/                        # unittest
packs/blocktopia-structures/
  LICENSE
  manifest.json
  structures/blocktopia/
    casa_inicial.mcstructure
    house1.mcstructure
mundos/                       # documentação e .gitkeep; sem save
```

O gerador produz comandos durante a execução; nenhum arquivo `scripts/scripts/hero-base.commands.txt` está presente na base auditada.

## Infraestrutura e configuração

Compose: serviço `minecraft`, container `blocktopia`, imagem `itzg/minecraft-bedrock-server:latest`, volume `MINECRAFT_DATA_DIR:/data`, 4 GB e 2 CPUs, reinício `unless-stopped`, stdin/TTY. NetherNet: TCP 19132 e UDP 19140–19155; não assumir UDP 19132 como diagnóstico.

Padrões versionados: Survival, Easy, 10 jogadores, visão 16, simulação 4 e cheats=false. Autenticação online/allowlist são fixadas em true, permissão padrão member e OPS vazio por padrão. O exemplo de ambiente habilita cheats temporariamente; revisar para operação normal. Não conceder OP às crianças por padrão.

A tag latest não fixa a versão Bedrock. 1.26.52 é referência histórica: confirmar a versão instalada antes de comandos/add-ons. Variáveis e caminhos privados não foram lidos.

No `.env.example`, preencher SERVER_UDP_PORTS, MINECRAFT_DATA_DIR e jogadores localmente. UUID é placeholder. MINECRAFT_PORT não é usado pelo Compose atual; ONLINE_MODE e ALLOW_LIST do exemplo não controlam os valores fixos. LEVEL_SEED não é mecanismo de reset.

## Preparação

Requer Git, Docker e Docker Compose. Revisar e aceitar os termos da EULA antes de operar.

```bash
git clone https://github.com/alexcarlos06/blocktopia-minecraft.git
cd blocktopia-minecraft
cp .env.example .env
# Editar .env localmente antes de continuar.
docker compose config --quiet
```

Não publicar .env nem saída interpolada completa de compose config. Na VPS existente, conferir checkout, volume e backup antes de atualização. A [documentação operacional](docs/IMPLEMENTACAO.md) descreve implantação/reversão; atualizar somente documentação não exige reinício.

## Console, construções e testes

O histórico registra problemas de permissão com send-command. Alternativa utilizada:

```bash
docker attach blocktopia
```

Comandos Bedrock sem / inicial. Sair com **Ctrl+P, depois Ctrl+Q**. **Não usar Ctrl+C** no console anexado.

As automações distinguem simulação, envio e confirmação. O runner exige backup antes da execução real, trabalha com um comando por chamada e limita fill verificado a 64 blocos. A importação por pack é um fluxo separado. Consulte os limites antes de executar: fill, setblock e structure load podem sobrescrever construções.

Testes previstos, da raiz em Linux com dependências preparadas:

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

Não é necessário introduzir pytest. A tentativa histórica com pytest falhou por módulo ausente. Esta atualização não executou a suíte nem testes na VPS. O leitor depende de amulet_nbt/leveldb e o backup usa fcntl; veja [dependências e limites](docs/IMPLEMENTACAO.md#testes-unittest-e-dependências).

## Segurança e continuidade

Backups e saves ficam fora do Git; não publicar credenciais, chaves, identificadores de jogadores, IPs privados ou dados do mundo. .gitignore não protege dados já rastreados. Fazer backup antes de alterações extensas, resets, atualização ou implantação de packs e validar restauração isoladamente.

A VPS contém outros serviços de produção. Restringir operações ao serviço minecraft/container blocktopia; não parar serviços globais nem executar limpezas Docker indiscriminadas. Git revert desfaz código/documentação, não restaura mundos ou versões migradas.

Referências: [imagem do servidor](https://github.com/itzg/docker-minecraft-bedrock-server), [Docker Compose](https://docs.docker.com/compose/) e [estruturas em Behavior Packs](https://learn.microsoft.com/en-us/samples/microsoft/minecraft-samples/structure-blocks-sample-behavior-pack/).
