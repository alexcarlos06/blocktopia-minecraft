# Scripts planejados para a história

**Planejamento, sem novos executáveis ou implantação.** O MVP usa condução manual: o adulto apresenta a história, acompanha a missão, confere o lar e controla a entrega da recompensa. As falas estão nos documentos narrativos; este arquivo trata apenas de possíveis automações.

## Possíveis evoluções após o ensaio manual

| Necessidade | Comportamento proposto | Condição antes de implementar |
| --- | --- | --- |
| Apresentar capítulo e missão | Exibir texto breve quando o adulto iniciar a atividade | Conferir legibilidade e compatibilidade na versão Bedrock usada e no PS4; manter alternativa de leitura manual |
| Acompanhar Missão 001 | Registrar aceite, pendência e conclusão aprovada pelo adulto | Definir persistência privada e participação cooperativa; não concluir apenas por detectar blocos |
| Entregar recompensa | Entregar somente após validação e impedir duplicação por participante | Aprovar conteúdo, quantidade e controle de entrega; prever retomada sem repetir recompensa |
| Liberar pista seguinte | Apresentar pista após capítulo concluído e destino validado | Atividade seguinte pronta; não gerar coordenadas nem desbloquear destinos inexistentes |

Nenhum nome de arquivo executável, API, comando ou tecnologia está fechado. Escolher mecanismo apenas após observar uma necessidade real no ensaio; não pressupor plugins de Java Edition, mods no PS4, cheats ou OP para as crianças.

## Relação com o código existente

O [inventário do plano](../PLANO-CAPITULO-01.md#reaproveitamento-da-infraestrutura-existente) descreve os módulos de terreno, construção, backup e catálogo disponíveis. Eles não constituem um sistema de capítulos, missões ou recompensas. O pack versionado contém estruturas de casa, não uma vila ou aventura completa.

Uma futura implementação deve respeitar os limites documentados em [IMPLEMENTACAO](../IMPLEMENTACAO.md#construção-e-limites), prever simulação e falhas, e receber testes locais antes de qualquer operação autorizada. Não contornar o runner ou usar scripts administrativos para colocar cenários durante uma tarefa documental.

Critérios futuros: conclusão incompleta recebe orientação; entrega não se repete após retomada; participante que chega depois pode contribuir; nenhuma automação impede continuar jogando manualmente. O [ensaio](VALIDACAO.md) continua necessário, mesmo que testes locais passem.
