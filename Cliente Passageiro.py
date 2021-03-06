from __future__ import print_function
import sys
from dataclasses import dataclass
import json
import Pyro4
import Pyro4.util
import rsa
import Crypto
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Signature import pss
import binascii
sys.excepthook = Pyro4.util.excepthook

nameserver = Pyro4.locateNS()
uri = nameserver.lookup("servidor.carona")
servidor = Pyro4.Proxy(uri)

key = RSA.generate(2048)
privatekey = key.export_key()
file_out = open("privatePassageiro.pem", "wb")
file_out.write(privatekey)
file_out.close()

publickey = key.publickey().export_key()
file_out = open("publicPassageiro.pem", "wb")
file_out.write(publickey)
file_out.close()

def consulta(idUser):
    if(not(idUser)):
        print("Antes de agendar a viagem, precisamos de um cadastro!\n")
        idUser = cadastro()
    destino = input("Para onde deseja ir? ").strip()
    origem = input("Aonde está? ").strip()
    data = input("Quando deseja ir? ").strip()
    qtdePessoas = input("Em quantas pessoas? ").strip()
    if origem and destino and data:
        respConsulta = servidor.consultaViagens(origem, destino, data, 0)
        idCorrida = interesse(data, origem, idUser, destino, qtdePessoas)
        if(not(respConsulta)):
            adicionarALista = input(
                "Não encontrei nada deseja adicionar a sua lista de interesse? 1 - SIM/ 0 - NÃO\n").strip()
            if adicionarALista == '0':
                print('Tudo bem! Nos vemos na próxima\n')
                servidor.cancelarInteresseEmCarona(idCorrida)
        else:
            servidor.cancelarInteresseEmCarona(idCorrida)
            print(respConsulta)
    # Registro de interesse em eventos (1,1)
def interesse(data, origem, idUser, destino, qtdePessoas):
    encoded = str(idUser)
    idUserEncoded = SHA256.new(encoded.encode('utf-8'))
    private = RSA.import_key(open('privatePassageiro.pem').read())
    signature = pss.new(private).sign(idUserEncoded)
    id = servidor.interesseEmCarona(idUser, origem, destino, data, qtdePessoas, signature)
    return id
def cadastro ():
    print("Novo por aqui? Cadastre-se\n")
    nome = input("Qual seu nome? ").strip()
    telefone = input("Certo! \n Qual seu telefone?").strip()
    if nome and telefone:
        idUser = servidor.cadastroUsuario(nome, telefone, publickey, 0) #O ultimo campo - se 1 motorista, se 0 passageiro
        print(idUser)
    return idUser
def removeInteresse(idUser):
    remover = input("Digite o número da viagem que deseja remover").strip()
    servidor.cancelarInteresseEmCarona(remover)
    print("Feito! Nos vemos na próxima!\n")
#TODO

#Cada cliente tem um método para o recebimento de notificações de eventos do servidor (0,4)


def main():

    escolha = ''
    idUser = ''
    while escolha != '0':
        escolha = input("\nOlá, o que precisa hoje? \n "
                        "1 - Cadastro \n"
                        " 2 - Buscar viagem \n"
                        " 3 - Remover Viagem \n"
                        " 0 - Sair\n").strip()
        if escolha != '0':
            if escolha == '1':
                idUser = cadastro()
            elif escolha == '2':
                consulta(idUser)
            else:
                removeInteresse(idUser)
    print("Até a próxima!")


if __name__ == "__main__":
    main()