# SOCORRO: robô do Instagram do SeparaGo sem o Claude

Tudo aqui roda no GitHub, mesmo com o limite do Claude acabado.
Repositório: https://github.com/gustavobaronidog-ctrl/separago-marketing

## Como apertar um botão
1. Abra o repositório e clique na aba **Actions**.
2. Clique em **Maestro dos posts (SeparaGo)** (menu da esquerda) ou em **Vigia**.
3. Clique em **Run workflow** e depois no botão verde **Run workflow**. Clique só 1 vez: o Maestro publica só o que estiver atrasado.

## Como o robô trabalha
O **Maestro** roda a cada 10 minutos (minutos 7, 17, 27, 37, 47, 57, que o GitHub atrasa menos). Ele olha o Instagram, vê quantos carrosséis e Reels já saíram hoje, compara com os horários da fila (carrosséis 08:30/12:30/18:30, Reels 10:30/15:00/20:30) e publica só o que faltar, no máximo 1 carrossel e 1 Reel por rodada, até 22h. Se o GitHub atrasar ou pular rodadas, a próxima corrige sozinha. Se não conseguir contar os posts, não publica (melhor atrasar que duplicar). Pausa 6 h se o Instagram bloquear. O workflow antigo "Postar" ficou só como botão manual de reserva.

**Feed organizado:** cada dia tem 3 carrosséis + os 3 Reels deles, todos do mesmo estilo (foto de fundo ou branco), alternando dia a dia. Para reorganizar de novo depois de criar conteúdo: Actions não tem botão para isso, peça ao Claude ("reorganizar a fila do SeparaGo").

## Chegou e-mail "Run failed". O que fazer
O e-mail já traz o problema e a solução em duas linhas: **SEM O CLAUDE** e **COM O CLAUDE**. Resumo:

| Problema no e-mail | Sem o Claude | Com o Claude |
|---|---|---|
| post atrasado | Actions > Maestro > Run workflow (1 vez) | "o robô do SeparaGo atrasou, destrave" |
| item falhou | Actions > última execução vermelha > ler o erro. Em fila/fila.json trocar "falhou" por "pendente" e "tentativas" por 0, Commit changes | "o robô do SeparaGo falhou, leia o erro e corrija" |
| bloqueio do Instagram (pausa) | esperar 6 horas, o robô volta sozinho | nada a fazer |
| arquivo não abre | em fila/fila.json trocar "pendente" por "pulado" no item (o robô ignora e segue) | "uma imagem não abre, restaure" |
| estoque acabando | o robô não cria conteúdo; a conta só fica sem post novo, sem risco. Poste 1 story ou Reel pelo celular se quiser | "criar mais carrosséis e Reels para o SeparaGo" |
| site fora do ar | Vercel > projeto separago > Deployments > último "Ready" > 3 pontinhos > Promote to Production | "o site do SeparaGo caiu, corrija" |
| token do Instagram venceu | gerar outro no painel da Meta e trocar em Settings > Secrets and variables > Actions | "o token venceu, troque" |

## Para onde vão os avisos
Os avisos chegam em gustavobaronidog@gmail.com e um filtro do Gmail encaminha para separago.contato@gmail.com.

## Só o Claude resolve
Código novo, criar conteúdo novo e gerar token novo.
