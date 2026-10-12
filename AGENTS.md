# Instruções para o Codex

## Antes de alterar

- Trabalhe no checkout `minecraft-bedrock-server`. Não crie checkouts, worktrees ou pastas de trabalho paralelas sem pedido explícito; documentos novos pertencem à estrutura deste repositório.
- Leia este arquivo, `README.md`, `docs/STATUS.md` e `BLOCKTOPIA-CONTEXTO.md`, quando disponível. Para história, consulte [o índice](docs/historia/README.md) e [o plano](docs/PLANO-CAPITULO-01.md). Se uma fonte estiver ausente, registre a limitação; não invente seu conteúdo nem procure em dados privados.
- Confira a árvore real, a branch e o diff antes de editar. Preserve alterações existentes do usuário e use uma branch com PR para revisão.

## Escopo e segurança

- Tarefas documentais ficam restritas ao Git. Não acessar VPS, containers, mundos salvos, backups ou segredos; não executar deploy nem scripts operacionais para validar Markdown.
- `minecraft-data` contém dados persistentes do container. A pasta de backup indicada pelo administrador (`minecraft-backup`; a documentação histórica também menciona `minecraft-backups`) é privada. Não inspecionar essas pastas nem presumir caminhos a partir dos nomes.
- Não versionar `.env`, credenciais, identificadores privados, saves, bancos LevelDB ou backups. Publicação de código não autoriza operação no servidor.
- Qualquer tarefa operacional futura exige escopo explicitamente autorizado e os cuidados de [IMPLEMENTACAO](docs/IMPLEMENTACAO.md); este arquivo não é autorização para executá-la.

## Conteúdo e continuidade

- Preserve Survival Easy, compatibilidade Minecraft Bedrock/PS4 e progressão natural. Não exigir OP, recursos exclusivos de Java Edition, mods no cliente ou recompensas que pulem etapas para participar da história.
- Separe narrativa, requisitos de construção, scripts planejados e validação conforme o índice de história. Atualize a fonte responsável e use links em vez de copiar seções entre documentos.
- Não invente coordenadas, versões instaladas, testes aprovados ou estado de implantação. Diferencie proposta, código versionado, execução relatada e validação pendente conforme `docs/STATUS.md`.
- Não transforme a casa importada em lar concluído dos jogadores nem marque locais como confirmados sem evidência e aprovação. Preserve as escolhas criativas e a condução manual da aventura.
- Mantenha este arquivo curto: instruções de trabalho aqui; história, critérios e procedimentos nos documentos próprios.

## Validação e entrega

- Para documentação, revise links, coerência e `git diff --check` conforme [VALIDACAO](docs/historia/VALIDACAO.md). Não execute a suíte ou comandos administrativos apenas por ter alterado texto.
- Para mudanças de código autorizadas, revise os testes antes de executar e selecione verificações locais adequadas; dependências e limites estão em [IMPLEMENTACAO](docs/IMPLEMENTACAO.md#testes-unittest-e-dependências).
- No PR, descreva o resultado, as verificações realmente executadas e as pendências. Não faça merge ou deploy como consequência de abrir o PR.
