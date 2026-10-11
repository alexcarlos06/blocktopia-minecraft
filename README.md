# Blocktopia — Minecraft Bedrock

Servidor privado para aventuras cooperativas, exploração e construções em família, com foco em Henry e Nicolas. Este repositório organiza a infraestrutura e os scripts; o mundo ativo permanece na VPS.

## Estrutura

- `compose.yaml`: serviço Minecraft.
- `.env.example`: modelo de configuração; copiar para `.env` e preencher localmente.
- `scripts/build-hero-base.py`: gerador de comandos da Fortaleza dos Heróis.
- `scripts/scripts/hero-base.commands.txt`: arquivo de comandos já existente no repositório.
- `mundos/`: pasta preparada para uma cópia consistente, revisada e autorizada do mundo. Veja [o procedimento](mundos/README.md).

## Configuração versionada e estado real

O Compose declara o serviço `minecraft`, container `blocktopia`, imagem `itzg/minecraft-bedrock-server:latest`, volume `MINECRAFT_DATA_DIR:/data`, limite de memória de 4 GB e 2 CPUs, reinício `unless-stopped` e console interativo.

Configura NetherNet, TCP 19132 e UDP 19140–19155. Não assumir UDP 19132 como diagnóstico dessa configuração. Survival, dificuldade Easy, até 10 jogadores, visão 16 e simulação 4 são os padrões do Compose. Autenticação online e allowlist estão fixadas em true; a permissão padrão é member e OPS fica vazio por padrão.

Esses arquivos descrevem a configuração versionada, não comprovam a versão ou o estado implantado na VPS. A tag latest não fixa a versão do Bedrock. Confirme nos logs antes de usar comandos ou add-ons dependentes de versão.

### Atenção ao .env.example

- Substituir `<IP_Publico>` em SERVER_UDP_PORTS e confirmar o caminho MINECRAFT_DATA_DIR; o caminho do exemplo é ilustrativo.
- Preencher ALLOW_LIST_USERS e MEMBERS com os identificadores aceitos pela imagem, verificados para a versão em uso; `UUID` é um placeholder, não um cadastro válido.
- O exemplo define ALLOW_CHEATS=true para configuração temporária; para a experiência normal, revisar e preferir false.
- MINECRAFT_PORT não é usado pelo Compose atual: as portas estão fixas em compose.yaml.
- ONLINE_MODE e ALLOW_LIST do exemplo não controlam o Compose atual, que fixa ambas em true.
- Não conceder OPS às crianças por padrão.
- LEVEL_SEED serve à geração de mundo; não é procedimento de reset de um mundo existente.

## Preparação e implantação

Requer Git, Docker e Docker Compose no host. Aceitar a EULA implica concordância com os termos do Minecraft.

Em um novo checkout:

```bash
git clone https://github.com/alexcarlos06/blocktopia-minecraft.git
cd blocktopia-minecraft
cp .env.example .env
# Editar .env localmente antes de continuar
docker compose config --quiet
```

O .env nunca deve ser publicado. Evite compartilhar a saída completa de docker compose config, pois pode revelar valores interpolados.

Na VPS existente, conferir o checkout e o volume antes de executar qualquer implantação. Caminhos de referência do projeto:

- Projeto: /home/alexcsousa/projects/minecraft-bedrock-server
- Dados: /home/alexcsousa/projects/minecraft-data
- Backups: /home/alexcsousa/projects/minecraft-backups

Após configuração revisada e backup consistente, a implantação manual afeta somente o serviço Minecraft:

```bash
docker compose up -d minecraft
docker compose ps minecraft
docker compose logs --tail=100 minecraft
```

O comando up pode criar ou recriar o container e causar indisponibilidade. Não executar pull/atualizações sem backup e revisão de compatibilidade. Não usar comandos globais de limpeza ou parar outros serviços da VPS. Nenhum desses comandos foi executado como parte da documentação.

## Console e construções

O histórico registra problemas de permissão com send-command; a alternativa utilizada foi:

```bash
docker attach blocktopia
```

Enviar comandos Bedrock sem / inicial. Desconectar com Ctrl+P, depois Ctrl+Q. **Não usar Ctrl+C**, que pode interromper o servidor.

Para gerar comandos, executar da raiz do repositório, com coordenadas revisadas:

```bash
python3 scripts/build-hero-base.py --x 100 --y 70 --z 100
```

Isso apenas gera scripts/hero-base.commands.txt; não modifica o servidor. As coordenadas são ilustrativas. Revisar a área afetada e os comandos para a versão instalada, fazer backup e aplicar de maneira controlada: fill e setblock podem sobrescrever construções.

## Mundos, privacidade e reversão

O repositório é público. Nenhum save da VPS acompanha esta preparação. A pasta mundos/ não é montada pelo Compose; importar nela uma cópia não muda o mundo ativo. Saves podem expor inventários, nomes, identificadores e construções privadas. Git não substitui backup e mundos grandes ou com alterações frequentes podem ser inadequados para ele. Consulte [mundos/README.md](mundos/README.md) antes de adicionar dados.

Para reverter somente uma alteração de documentação/ignore, usar git revert com o SHA do commit correspondente e revisar o resultado antes de enviar. Isso não restaura nem altera a VPS. Voltar o código não restaura mundos nem desfaz uma migração de versão; restauração operacional exige backup validado e procedimento específico.

Referências: [imagem do servidor](https://github.com/itzg/docker-minecraft-bedrock-server) e [Docker Compose](https://docs.docker.com/compose/).
