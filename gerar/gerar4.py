import os,json,datetime,subprocess
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
R=os.getcwd()
src=open(R+"/gerar/gerar.py").read().split('T="/tmp/sgb"')[0].replace("#FFC53D","#9ADBBB").replace("#FF8A00","#0F7A55")
g={"__name__":"g4","__file__":R+"/gerar/gerar.py"}
os.environ.setdefault("FONTDIR","/usr/share/fonts/opentype/inter")
exec(src,g)
g["BAG"]='<svg viewBox="0 0 200 200" width="120" height="120"><rect width="200" height="200" rx="46" fill="#F6F5F2"/><path d="M72 80 C72 44 132 44 132 80" stroke="#E5452D" stroke-width="13" stroke-linecap="round" fill="none"/><path d="M52 76 H152 L160 148 Q161 160 149 160 H55 Q43 160 44 148 Z" fill="#0F7A55"/><path d="M84 118 H122 M106 100 L124 118 L106 136" stroke="#fff" stroke-width="11" stroke-linecap="round" stroke-linejoin="round" fill="none"/><path d="M22 112 H38 M16 130 H34" stroke="#0F7A55" stroke-width="8" stroke-linecap="round" opacity=".5"/></svg>'
page=g["page"]; BASE=g["BASE"]
X=[
("sinais-perdendo","foto1",["3 sinais de que seu mercado está **perdendo dinheiro** e você nem vê. 💸","Sinal 1: o cliente pede por áudio e metade do pedido se perde. 🎙️","Sinal 2: o produto acaba e a vitrine continua mostrando. 📦","Sinal 3: o app leva uma parte de cada venda, todo mês. 🧾","Dá pra resolver os 3 no mesmo lugar: pedido organizado, vitrine certa, sem comissão. ✅","Quer parar de perder? **Teste grátis**. Link na bio. 👇"],"3 sinais clássicos de dinheiro escapando do mercado.\n\nSalve e confira o seu. Teste o SeparaGo grátis, link na bio.","#separago #mercado #supermercado #comerciolocal"),
("cardapio-lanchonete","foto2",["Seu cardápio é uma **foto torta no WhatsApp**? 😬","Cliente não acha o preço e desiste de pedir. 📉","Cardápio em link, com foto e preço, vende sozinho. 📲","O pedido chega pronto, sem você digitar nada. ✅","Lanchonete organizada vende mais na hora do pico. 🍔","Quer um cardápio que vende? **Teste grátis**. Link na bio. 👇"],"Cardápio em link com preço claro vende mais que foto torta no WhatsApp.\n\nSalve e teste o SeparaGo grátis, link na bio.","#separago #lanchonete #pizzaria #delivery"),
("whatsapp-lotado",None,["Seu WhatsApp tem **200 mensagens não lidas**? 📱","Dentro delas tem pedido que você nem viu. 😰","Cada pedido perdido é dinheiro que foi pro concorrente. 💸","Com loja online, o pedido cai numa fila, não numa conversa. 📋","Você atende o que importa e a equipe separa o resto. 👥","Quer o WhatsApp livre? **Teste grátis**. Link na bio. 👇"],"WhatsApp lotado esconde pedido. Fila de pedidos não esconde.\n\nSalve e teste o SeparaGo grátis, link na bio.","#separago #varejo #donodemercado #gestao"),
("erros-delivery","foto4",["5 erros que **fazem o cliente nunca mais pedir** no seu delivery. 🛵","1. Prometer 30 minutos e entregar em 60. ⏰","2. Mandar item errado e não avisar. 📦","3. Não confirmar o pedido com o cliente. ❓","4. Deixar o cliente sem saber onde está o pedido. 📍","Quer organizar o delivery? **Teste grátis**. Link na bio. 👇"],"Delivery bom é o que cumpre o que promete e avisa quando atrasa.\n\nSalve a lista. Teste o SeparaGo grátis, link na bio.","#separago #lanchonete #pizzaria #delivery"),
("cliente-sumiu",None,["Aquele cliente que **comprava toda semana e sumiu**. 🫥","Você nem notou, porque não tem como ver. 👀","No SeparaGo você vê quem pediu e quem parou de pedir. 📊","Uma mensagem simples no dia certo traz ele de volta. 💬","Cliente que volta custa bem menos que cliente novo. 🔁","Quer ver quem sumiu? **Teste grátis**. Link na bio. 👇"],"Reconquistar cliente custa menos que conquistar um novo.\n\nSalve e teste o SeparaGo grátis, link na bio.","#separago #mercadinho #empreendedorismo #vendas"),
("fim-de-semana","foto3",["Sábado de mercado cheio: **a equipe corre e o erro aparece**. 🏃","Pedido acumula e ninguém sabe qual é o próximo. 🌀","Fila de separação deixa cada um no seu pedido. 📋","Balança blindada confere o peso de cada item. ⚖️","Sábado vira o dia mais lucrativo, não o mais caótico. 💚","Quer sábado sem caos? **Teste grátis**. Link na bio. 👇"],"Fim de semana cheio pede fila de separação e conferência por item.\n\nSalve e teste o SeparaGo grátis, link na bio.","#separago #mercado #supermercado #comerciolocal"),
("app-nao-e-seu","foto1",["O cliente do app **não é seu cliente**. 📵","Você não tem telefone, nem nome, nem histórico dele. 🕳️","Se o app cobrar mais ou sumir, você perde tudo. 😨","Na loja própria o cliente fica no seu cadastro. 📒","A marca é sua, o contato é seu, o cliente é seu. 💚","Quer o cliente na sua mão? **Teste grátis**. Link na bio. 👇"],"Quem depende só de aplicativo não é dono do próprio cliente.\n\nSalve e teste o SeparaGo grátis, link na bio.","#separago #varejo #donodemercado #gestao"),
("cliente-vale",None,["Quanto vale **um cliente fiel** pro seu mercado em um ano? 🧮","Se ele gasta R$ 200 por mês, são R$ 2.400 por ano. 💰","Perder 1 cliente assim dói mais do que parece. 😬","Atendimento rápido e pedido certo é o que prende. ✅","Cuide de quem já compra antes de caçar quem nunca comprou. 🤝","Quer cuidar melhor? **Teste grátis**. Link na bio. 👇"],"Um cliente fiel vale milhares por ano. Perder um é caro.\n\nSalve a conta. Teste o SeparaGo grátis, link na bio.","#separago #mercadinho #empreendedorismo #vendas"),
("horario-nobre","foto2",["Das 18h às 20h seu delivery **vende metade do dia**. 🌆","É também a hora que mais dá erro. 🔥","Dica 1: separe os pedidos em fila, não no grito. 📋","Dica 2: avise o prazo na hora do pedido. ⏱️","Dica 3: ponha mais gente na separação nesse horário. 👥","Quer atravessar o pico? **Teste grátis**. Link na bio. 👇"],"Horário nobre pede fila organizada e equipe no lugar certo.\n\nSalve as dicas. Teste o SeparaGo grátis, link na bio.","#separago #lanchonete #pizzaria #delivery"),
("sete-dias",None,["O que dá pra fazer em **7 dias grátis** no SeparaGo? 🗓️","Dia 1: cadastrar seus produtos e preços. 🏷️","Dia 2: ver sua loja online com seu nome e cores. 🏪","Dias 3 a 5: receber pedidos de teste com sua equipe. 👥","Dias 6 e 7: ver os relatórios e decidir. 📊","Quer testar sem risco? **Teste grátis**. Link na bio. 👇"],"7 dias grátis em todos os planos para testar com sua equipe.\n\nSalve e comece o seu teste, link na bio.","#separago #mercado #lanchonete #comerciolocal"),
]
T="/tmp/sgx"; os.makedirs(T,exist_ok=True); jobs=[]
for i,(slug,bg,sl,leg,tg) in enumerate(X,1):
    out=f"{R}/midia/x{i:02d}"; os.makedirs(out,exist_ok=True)
    for si,tx in enumerate(sl,1):
        h=f"{T}/x{i:02d}_{si}.html"; p=f"{T}/x{i:02d}_{si}.png"
        open(h,"w").write(page(tx,si,len(sl),bg if si==1 else None,si==len(sl))); jobs.append((h,p,f"x{i}{si}"))
def shot(a):
    h,p,n=a
    subprocess.run(["google-chrome","--headless=new","--no-sandbox","--disable-gpu","--allow-file-access-from-files","--hide-scrollbars","--window-size=1080,1350","--user-data-dir=/tmp/cx_%s"%n,"--screenshot="+p,"file://"+h],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=180)
with ThreadPoolExecutor(4) as ex: list(ex.map(shot,jobs))
FP=R+"/fila/fila.json"; fila=json.load(open(FP)); have={x["id"] for x in fila}
hoje=(datetime.datetime.now(datetime.timezone.utc)-datetime.timedelta(hours=3)).strftime("%Y-%m-%d")
for i,(slug,bg,sl,leg,tg) in enumerate(X,1):
    for si in range(1,7): Image.open(f"{T}/x{i:02d}_{si}.png").convert("RGB").save(f"{R}/midia/x{i:02d}/{si}.jpg",quality=90)
    iid=f"x{i:02d}-{slug}"
    if iid not in have: fila.append({"id":iid,"data":hoje,"hora":"extra","tipo":"carrossel","legenda":leg+"\n\n"+tg,"imagens":[f"{BASE}/x{i:02d}/{s}.jpg" for s in range(1,7)],"status":"pendente"})
json.dump(fila,open(FP,"w"),ensure_ascii=False,indent=1); print("ok",len(fila))
