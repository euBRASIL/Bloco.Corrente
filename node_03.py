import datetime # lida com as datas
import hashlib  # cria as hashes
import json # cria os arquivos json
from flask import Flask, request, jsonify  # envia/recebe as requisições
import requests  # gerencia os nós da rede
from uuid import uuid4  # gera identficadores únicos aleatóriamente
from urllib.parse import urlparse  # trabalha com as URLs

# Parte 1 - Cria a moeda Apuscoin (transações)

class Blockchain:
    # função de inicialização
    def __init__(self):  # "self" usa as variáveis do objeto
        self.chain = []  # lista Python como o bloco
        # cria uma lista para as transações: as transações são adicionadas ao bloco através da mineração
        self.transactions = []
        # cria o bloco gênesis
        self.create_block(proof = 1, previous_hash = '0')  
        # adiciona os nós participantes da rede através de um set (mais otimizado q o list)
        self.nodes = set()

    # função que cria um bloco com suporte a transações e adiciona ao blockchain (encadear)
    def create_block(self, proof, previous_hash):  # faz o link com o bloco anterior
        # cria o dicionário com as 5 chaves do bloco: índice, timestamp, proof (nounce), previous_hash, transações
        # importante: o bloco é criado depois ser de minerado (proof-of-work)
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previous_hash': previous_hash,
            # adiciona uma chave para as transações na criação do bloco
            'transactions': self.transactions
        }
        # quando o bloco é criado, zera a lista de transações
        self.transactions = []
        # inclui o bloco (lista) à blockchain (lista)
        self.chain.append(block)

        return block  # retorna o bloco criado

    # função que retorna o bloco anterior
    def get_previous_block(self):  # recebe o próprio objeto (lista inicializada)
        return self.chain[-1]  # retorna o bloco anterior

    # função que faz o proof-of-work (deve ser difícil de resolver e fácil de recuperar)
    def proof_of_work(self, previous_proof): # recebe: o próprio objeto e a prova anterior
        new_proof = 1  # inicializa o proof (prova)
        check_proof = False  # verifica se o proof está correto
        # resolve o hash (quanto mais zeros à esquerda, mais difícil o problema)
        while check_proof is False:
            # cria uma hash em hexadecimal
            hash_operation = hashlib.sha256(
                str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            # verifica se resolveu o problema/puzzle
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1  # incrementa o proof antes de testar novamente

        return new_proof  # retorna o proof

    # função que verifica se o bloco gerado é válido
    # 1. 
    # 2. A cadeia do bloco anterior está correta?

    # cria uma função de hash própria
    def hash(self, block):  # recebe o próprio objeto e o próprio bloco (lista)
        # gera o json codificado do bloco
        # ordena pela chave e codifica como string
        encoded_block = json.dumps(block, sort_keys=True).encode()
        # retorna o hash SHA256 do json
        return hashlib.sha256(encoded_block).hexdigest()

    # cria uma função que valida o proof-of-work e o hash anterior
    def is_chain_valid(self, chain): # recebe o próprio objeto (cadeia de blocos) e a lista com todos os blocos
        previous_block = chain[0]  # inicializa o bloco anterior
        block_index = 1  # inicializa o índice do bloco atual
        while block_index < len(chain):  # percorre todos os blocos do blockchain
            block = chain[block_index]  # pega o block atual pelo índice
            # verifica se o hash do bloco atual (dicionário) é igual ao hash do bloco anterior
            if block['previous_hash'] != self.hash(previous_block):
                return False  # hash anterior inválida (blockchain inválido)
            # recebe o valor do proof-of-work prévio
            previous_proof = previous_block['proof']
            # recebe o valor do proof-of-work atual
            proof = block['proof']  
            # gera o novo hash
            hash_operation = hashlib.sha256(
                str(proof**2 - previous_proof**2).encode()).hexdigest()
            # verifica se o proof está correto, inciciando com 0000
            if hash_operation[:4] != '0000':
                # hash do proof-of-work é inválido (blockchain inválido)
                return False
            # atualiza a variável do bloco anterior com o bloco atual
            previous_block = block
            # incrementa o índice do bloco
            block_index += 1
        # se deu tudo certo com as 2 validações (proof-of-work e o hash anterior), retorna True
        return True  

    # função que define o formato da transação
    def add_transaction(self, sender, receiver, amount): # recebe a si própria, o desto, o receptor e o valor
        # define o formato da transação no dicionário Python
        self.transactions.append({
            'sender': sender,
            'receiver': receiver,
            'amount': amount
        })
        # verifica em qual bloco a transação foi adicionada
        previous_block = self.get_previous_block()
        # retorna o bloco atual
        return previous_block['index'] + 1  

    # função que adiciona um nó na lista de nós
    def add_node(self, address):  # recebe a si mesmo e o endereço do nó
        # extrai a parte do endereço que interessa (ip + porta)
        parsed_url = urlparse(address)
        # adiciona o endereço ao conjunto de nós
        self.nodes.add(parsed_url.netloc)

    # função do protocolo de consenso (substitui o blockchain se encontrar um bloco maior)
    def replace_chain(self):
        network = self.nodes  # recebe todos os nós (conjunto)
        longest_chain = None  # encontra a cadeia mais longa
        max_length = len(self.chain)  # verifica o tamanho da cadeia
        # percorre todos os nós da rede (busca o blockchain mais longo)
        for node in network:
            # pega o comprimento da rede
            response = requests.get(f'http://{node}/get_chain')
            # verifica se a resposta está correta
            if response.status_code == 200:
                # pega o comprimento do blockchain
                length = response.json()['length']
                # pega o blockchain em si
                chain = response.json()['chain']
                # verifica se o comprimento atual é maior que o tamanho máximo
                if length > max_length and self.is_chain_valid(chain):
                    # atualiza o maior valor com o blockchain atual
                    max_length = length
                    longest_chain = chain
        # verifica se foi econtrado um bloco maior
        if longest_chain:
            self.chain = longest_chain
            return True  # o blockchain foi substituído
        else:
            return False  # não houve substituição no blockchain

# Parte 2 - Mineração do Bitcoin

# cria a aplicação web
app = Flask(__name__)

# cria o endereço para o nó na porta 5000 (nó minerador para recompensa)
node_address = str(uuid4()).replace('-', '')  # retira os "-" da hash gerada

# cria uma instância da classe Blockchain (objeto em memória)
blockchain = Blockchain()

# cria a rota de mineração
@app.route('/mine_block', methods = ['GET'])
# função que vai minerar o bloco a partir da instância criada
def mine_block():
    previous_block = blockchain.get_previous_block() # pega o bloco anterior
    previous_proof = previous_block['proof']  # pega o proof-of-work do bloco
    # adiciona uma transação de recompensa
    blockchain.add_transaction(sender = node_address, receiver = 'miner', amount = 0.5)
    # pega o proof-of-work do bloco anterior
    proof = blockchain.proof_of_work(previous_proof)
    # pega o hash anterior
    previous_hash = blockchain.hash(previous_block)  
    # cria o bloco
    block = blockchain.create_block(proof, previous_hash)  
    # exibe o resultado da mineração na página
    response = {
        'message': 'Parabéns! Você minerou um bloco.',
        'index': block['index'],
        'timestamp': block['timestamp'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
        # inclui as transações do bloco
        'transaction': block['transactions']
    }
    # retorna no formato json e o status de resposta http (OK)
    return jsonify(response), 200

# cria a rota que retorna a versão atual do blockchain
@app.route('/get_chain', methods = ['GET'])
# cria uma função que retorna todo o blockchain e o seu tamanho
def get_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    # retorna no formato json e o status de resposta http (OK)
    return jsonify(response), 200

# cria a rota que adiciona uma transação ao bloco
@app.route('/add_transaction', methods = ['POST'])
# cria a funçao que adiciona uma transação ao bloco
def add_transaction():  # cria a transação
    json = request.get_json()  # pega o arquivo json enviado
    # verifica se o json é válido, ou seja, se as chaves existem
    transaction_keys = ['sender', 'receiver', 'amount']
    # se não há chaves no arquivo
    if not all(key in json for key in transaction_keys):
        # retorna um aviso e o status de resposta http (Bad request)
        return 'Alguns elementos estão faltando', 400
    else:
        # se a transação está ok, adiciona as transações ao próximo bloco
        index = blockchain.add_transaction(
            json['sender'], json['receiver'], json['amount'])
        # cria a mensagem de output
        response = {
            'message': f'Esta transação será adicionada ao Bloco {index}.'}
        # retorna a mensagem no formato json e o status de resposta http (Created)
        return jsonify(response), 201

# rota que conecta qualquer nó na rede descentralizada (registra na rede)
@app.route('/connect_node', methods = ['POST'])
# inclui o nó no json com os nós existentes
def connect_node():  # não recebe nada, pois os parâmetros já fazem parte do blockchain
    json = request.get_json()  # recebe o json com os nós
    # conecta o novo nó aos demais da rede pela chave
    nodes = json.get('nodes')  # armazena a chave "nodes" (todos os nós)
    # verifica se os nós existem
    if nodes is None:
        return "Sem nós no arquivo.", 400  # Bad Request
    # adiciona cada um dos nós ao blockchain
    for node in nodes:
        blockchain.add_node(node)  # adiciona um nó na rede
        # retorna uma mensagem e todos os nós do blockchain
    response = {
        'message': 'Todos nós conectados. O Blockchain contém os seguintes nós:',
        'total_nodes': list(blockchain.nodes)
    }
    # retorna a mensagem no formato json e o status de resposta http (Created)
    return jsonify(response), 201

# rota que substitui a versão do blockchain em um nó (se necessário)
@app.route('/replace_chain', methods = ['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()  # recebe a execução do blockchain
    # testa o blockchain (versão nova e versão do nó)
    if is_chain_replaced:
        response = {
            'message': 'Os nós tinham cadeias diferentes, então foi substituída.',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Tudo certo, não houve substituição.',
            'actual_chain': blockchain.chain
        }
    # retorna no formato json e o status de resposta http (Created)
    return jsonify(response), 201

# executa a aplicação
app.run(host = '0.0.0.0', port = 5003)
