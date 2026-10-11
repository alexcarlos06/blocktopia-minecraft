# Cópias de mundos Bedrock

Esta pasta foi preparada para versionamento. **O mundo ativo não foi copiado nem enviado.** Não há integração automática com o volume /data do container.

Não existia convenção mundos/ ou worlds/ na árvore consultada; adotou-se mundos/ para as cópias no Git. Isso não renomeia a pasta worlds/ interna do Bedrock.

## Obter uma cópia consistente

1. Confirmar no ambiente real MINECRAFT_DATA_DIR, LEVEL_NAME, versão do servidor e caminho do mundo. Normalmente o mundo está em MINECRAFT_DATA_DIR/worlds/LEVEL_NAME; verificar, sem presumir.
2. Usar uma cópia feita após encerramento limpo do servidor, ou um snapshot/backup consistente produzido por procedimento suportado e validado para a versão instalada. Copiar arquivos LevelDB enquanto o mundo recebe gravações pode gerar corrupção; snapshot de disco isolado não garante consistência da aplicação.
3. Se não existe cópia consistente, programar uma janela de manutenção e backup com o administrador. Este documento não executa nem autoriza uma parada da VPS.
4. Transferir somente a pasta do mundo a partir dessa cópia imutável para uma área local privada, fora do repositório. Não copiar /data inteiro: ele pode conter configurações, listas de jogadores e outros dados privados.
5. Testar a cópia em ambiente isolado com versão compatível, preservando a origem, sem abrir portas públicas e sem usar o volume de produção.
6. Revisar privacidade e tamanho antes de publicar. O repositório é público: o próprio banco do mundo pode conter dados de jogadores. Não basta excluir allowlist.json; se não houver segurança sobre a privacidade, manter o save em backup privado e versionar somente documentação.

## Importar uma cópia local já revisada

Exemplo Bash/Linux, na raiz de um checkout separado do volume ativo. Substitua o caminho por uma cópia local consistente e previamente revisada; não aponte para o mundo em execução.

```bash
origem="/caminho/privado/copia-consistente/Blocktopia"
test -f "$origem/level.dat" && test -d "$origem/db" || exit 1
test ! -e mundos/Blocktopia || exit 1
mkdir -p mundos/Blocktopia
cp -a "$origem/." mundos/Blocktopia/
du -sh mundos/Blocktopia
find mundos/Blocktopia -type f -size +50M -print
git status --short --untracked-files=all -- mundos/
git add --dry-run -- mundos/Blocktopia
```

A verificação de level.dat e db é apenas estrutural, não comprova integridade. Registre em documentação a data da cópia, versão exata do Bedrock, método de snapshot e resultado do teste, sem nomes ou identificadores privados.

Mundos binários mudam frequentemente e podem aumentar muito o histórico do Git. Verifique os limites atuais do GitHub antes do envio; para saves grandes, prefira armazenamento privado de backups ou avalie Git LFS com acesso e custos apropriados. LFS não torna dados de um repositório público privados.

Só após revisão e teste:

```bash
git add -- mundos/Blocktopia
git diff --cached --stat
git diff --cached --name-only
git commit -m "chore: adiciona copia revisada e consistente do mundo"
git push
```

Não usar git add -f para contornar proteções. Arquivos .env, chaves, allowlist.json, permissions.json e arquivos de backup permanecem ignorados. O .gitignore não remove arquivos já rastreados nem protege dados embutidos no banco binário. Revise também os arquivos ignorados para garantir que a cópia continua completa e funcional.

## Reversão

Antes de commitar, se a cópia foi adicionada ao índice: git restore --staged -- mundos/Blocktopia. Remova depois somente a cópia local que você criou, conferindo o caminho; nunca remova o volume ativo.

Depois do commit, git revert SHA_DO_COMMIT desfaz a inclusão na versão corrente, mas não elimina dados do histórico. Se algum dado privado for publicado, tratar como exposição e revisar a remoção do histórico e eventuais credenciais. Este fluxo não implanta nem restaura o mundo na VPS.
