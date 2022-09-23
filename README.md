# tchelinux-2022
Repositório da palestra "APUSCOIN: Criando uma criptomoeda do zero com Python e Linux". Tchelinux Live 2022. 

## Sequência de testes via POSTMAN:   

1. POST /connect_node - Conecta o nó atual aos nós na rede   
Body >> raw >> JSON >> nodes.json    
http://127.0.0.1:5001/connect_node   
http://127.0.0.1:5002/connect_node   
http://127.0.0.1:5003/connect_node   

2. GET /get_chain - Retorna o blockchain atual   
http://127.0.0.1:5001/get_chain   
http://127.0.0.1:5002/get_chain   
http://127.0.0.1:5003/get_chain   

3. POST /add_transaction - Envia uma transação através via Node 01   
Body >> raw >> JSON >> transactions.json    
http://127.0.0.1:5001/add_transaction   

4. GET /mine_block - Minera um bloco   
http://127.0.0.1:5001/mine_block   

5. GET /replace_chain - Aplica o protocolo de consenso   
http://127.0.0.1:5002/replace_chain   
http://127.0.0.1:5003/replace_chain   




