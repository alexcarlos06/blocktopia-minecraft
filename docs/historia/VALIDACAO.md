# Validação do Capítulo 1

## Revisão documental, sem ambiente de jogo

Aplicável a este PR e a futuras alterações apenas de texto:

- Conferir caminhos e links relativos contra a árvore real do repositório.
- Revisar o diff com `git diff --check` e confirmar que o escopo contém somente arquivos previstos.
- Conferir coerência entre [capítulo](CAPITULO-01.md), [missão](MISSAO-001-UM-LAR.md) e [requisitos](REQUISITOS-DE-CONSTRUCAO.md).
- Manter explícitos Survival Easy, Bedrock/PS4, participação cooperativa e progressão natural.
- Distinguir proposta narrativa, código existente, execução relatada e validação pendente; não criar coordenadas, evidências ou marcos de implantação.
- Confirmar que não foram incluídos segredos, identificadores privados, saves ou backups.

Revisão documental não exige executar scripts administrativos, suíte de integração, Docker ou acessar VPS/mundos. Registrar no PR os checks realmente realizados e os não executados.

## Validação futura de implementação

**Procedimentos planejados, não executados nesta organização documental.** O ensaio no jogo depende de autorização operacional específica e dos pré-requisitos do [plano](../PLANO-CAPITULO-01.md); não deve ser iniciado para validar este PR.

### Código

Após preparar dependências em Linux isolado, executar da raiz:

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

Revisar especialmente test_site_locator.py, test_location_registry.py, test_terrain_reader.py, test_foundation.py, test_foundation_commands.py, test_backup_world.py e testes construction/bedrock de envio, divergência e verificação. Existem 24 arquivos de testes na base. A suíte usa unittest/mock; pytest não é pré-requisito.

Dependências do leitor: amulet_nbt e leveldb; backup usa fcntl (Linux). A main não fixa dependências Python. Registrar versões e falhas de importação; não omitir falhas para declarar aprovação. A revisão anterior do plano registra inspeção dos testes, sem execução. Nesta organização documental, a suíte também **não foi executada**; não houve teste de integração ou VPS.

### Ensaio do capítulo

- [ ] Confirmar backup recuperável e cenários aprovados.
- [ ] Entrar por cliente Bedrock/PS4 autorizado com permissão member.
- [ ] Percorrer acampamento → trilha → ponte → vila e retorno, sem OP/voo/teleporte.
- [ ] Conferir placas no PS4, pontos de confusão, iluminação e riscos de dia/noite; não exigir que crianças passem noite em perigo.
- [ ] Simular aceite e recusa da missão com adulto: lar incompleto recebe dica, sem recompensa; completo recebe reconhecimento e recompensa uma vez.
- [ ] Simular chegada posterior de outro participante e impedir recompensa duplicada sem bloquear sua participação.
- [ ] Confirmar que crianças podem construir o próprio lar sem ocupar espaços públicos.
- [ ] Registrar ajustes; repetir apenas cenários afetados.
- [ ] Autorizar início da sessão familiar após todos os bloqueios resolvidos.

Registro técnico por etapa: data real, SHA, mundo/versão, cenário, coordenadas/footprint/orientação, backup privado, comando se houve, trecho de resposta sanitizado, inspeção, resultado, pendências e responsável. Git guarda documentação e referências sanitizadas, nunca save, backup, .env, tokens, chaves, IPs privados ou identificadores pessoais.

### Resultado e acompanhamento

Registrar cada verificação como aprovado, reprovado ou não executado, com evidência sanitizada e pendência. Atualizar [STATUS](../STATUS.md) somente com resultados reais. Uma falha no ensaio retorna à etapa afetada; publicação de Markdown e testes com mocks não comprovam compatibilidade ou jogabilidade no PS4.
