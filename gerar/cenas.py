# Cena (biblioteca Pexels) para cada frase de cada video. 8 beats + 1 cena para o final (CTA).
# Chaves = arquivos lib-<chave>.mp4 em /home/claude/lib. Escolhidas lendo o roteiro de cada video.
CENAS = {
 "m04-audio-lista": ["voice_msg", "writing_list", "angry_customer", "owner_thinking", "writing_list", "receipt_calc", "empty_shelf", "happy_groceries", "packing_order"],
 "m05-item-falta": ["empty_shelf", "picking_shelf", "queue_checkout", "owner_thinking", "inventory_check", "showing_product", "customer_ok", "happy_groceries", "packing_order"],
 "m06-sexta-18h": ["queue_checkout", "phone_notif", "busy_cashier", "owner_thinking", "pickup_counter", "packing_order", "typing_phone", "happy_groceries", "packing_order"],
 "m07-preco-zap": ["phone_chat", "typing_phone", "clock_time", "owner_thinking", "price_tags", "photo_product", "price_tags", "customer_phone", "happy_groceries"],
 "c04-sinal": ["brigadeiro", "sweets_tray", "phone_chat", "owner_thinking", "pix_pay", "clock_time", "writing_list", "pickup_counter", "box_packing"],
 "c05-preco-bolo": ["cake_display", "calc_confused", "cake_decorating", "owner_thinking", "ingredients", "clock_time", "sweets_tray", "baker_smile", "cake_display"],
 "c06-meio-a-meio": ["snacks_tray", "phone_chat", "angry_customer", "owner_thinking", "writing_list", "customer_ok", "box_packing", "baker_smile", "snacks_tray"],
 "c07-limite-dia": ["oven_trays", "night_baking", "tired_worker", "owner_thinking", "clock_time", "writing_list", "clock_time", "baker_smile", "oven_trays"],
 "l04-adicional": ["bacon", "receipt_calc", "burger_serve", "owner_thinking", "order_ticket", "pix_pay", "kitchen_ticket", "money_count", "burger_serve"],
 "l05-taxa-entrega": ["delivery_bike", "phone_chat", "angry_customer", "owner_thinking", "map_nav", "customer_phone", "receipt_calc", "delivery_handoff", "delivery_bike"],
 "l06-endereco": ["delivery_bike", "phone_ringing", "burger_cook", "owner_thinking", "order_ticket", "phone_chat", "phone_ringing", "delivery_handoff", "delivery_bike"],
 "l07-cardapio-zap": ["photo_product", "phone_chat", "typing_phone", "owner_thinking", "combo", "customer_phone", "photo_product", "burger_serve", "combo"],
 "v02-encomenda": ["snacks_tray", "phone_chat", "phone_notif", "owner_thinking", "snacks_tray", "clock_time", "pix_pay", "writing_list", "box_packing"],
 "v03-correria": ["phone_notif", "onion", "angry_customer", "owner_thinking", "order_ticket", "kitchen_ticket", "burger_pack", "burger_serve"],
}

# finais contextualizados (texto na tela; a voz diz o mesmo + "Link na bio."). So entram quando a nova voz existe.
CTAS = {
 "m05-item-falta": "Cansado de descobrir o item em falta só na hora de separar? No SeparaGo o cliente já pede sabendo o que tem.",
 "m06-sexta-18h": "Quer atender a sexta sem perder pedido? No SeparaGo os pedidos chegam num lugar só.",
 "m07-preco-zap": "Cansou de responder preço o dia inteiro? No SeparaGo o cliente vê tudo e pede sozinho.",
 "c04-sinal": "Quer parar de perder encomenda sem sinal? No SeparaGo o pedido chega organizado, com tudo no mesmo lugar.",
 "c05-preco-bolo": "Quer fechar o preço e vender sem negociar no zap? No SeparaGo o cliente já vê o valor e pede.",
 "c06-meio-a-meio": "Quer acabar com a confusão de sabor e quantidade? No SeparaGo o cliente escolhe sozinho e a lista já vem pronta.",
 "c07-limite-dia": "Quer ver o dia fechar antes de aceitar mais encomenda? No SeparaGo o pedido chega organizado.",
 "l04-adicional": "Quer parar de dar adicional de graça? No SeparaGo o adicional vai junto do lanche até a cozinha.",
 "l05-taxa-entrega": "Cansou de explicar a taxa de entrega no zap? No SeparaGo o cliente já vê o total com a entrega.",
 "l06-endereco": "Quer que o endereço chegue certo na primeira vez? No SeparaGo ele vai junto do pedido.",
 "l07-cardapio-zap": "Quer parar de responder o cardápio o dia todo? No SeparaGo o cliente vê o cardápio e pede sozinho.",
 "v02-encomenda": "Cansou de encomenda espalhada em mil mensagens? No SeparaGo o cliente escolhe sabor e quantidade e o pedido chega organizado.",
 "v03-correria": "Quer que o sem cebola chegue na cozinha? No SeparaGo ele vai junto do lanche, e a comanda sai impressa.",
}
