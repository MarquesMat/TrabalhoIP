#!/etc/bin/bash

# Data: 31/05/2023
# Autor: Matheus Marques
# Esse script verifica quais ips estão livres para utilizar em novos dispositivos
# Parâmetros: Veja o aquivo README.txt para mais detalhes
# Caminho: /home/monitora/Documents/Projeto Monitora/Códigos/iplivres

from __future__ import print_function
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import subprocess

SCOPES = ['https://www.googleapis.com/auth/spreadsheets'] # Link da API
SAMPLE_SPREADSHEET_ID = '12QHt0lVhsdlLFUOXwfpuazXFw5TpGyB6JBXMSiM10wA' # ID da planilha
#SAMPLE_RANGE_NAME = 'GRAGOATÁ!G:G' # Exemplo de range

def get_list_sheet(pagina, letra):
    sample_range_name = pagina+"!"+letra+"3:"+letra # Coluna com IPs
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range=sample_range_name).execute()
    except HttpError as err:
        print(err)
    
    values = result.get('values', [])
    non_empty_cells = [cell[0] for cell in values if cell]  # Filtra as células não vazias
    print(pagina) # Indica qual página já foi acessada
    return non_empty_cells

def get_ips(nome_arq): # Retorna uma lista com os IPs do arquivo passado como parâmetro
    with open(nome_arq, 'r') as arquivo:
        linhas = arquivo.readlines()
    return [linha.strip() for linha in linhas]

def check_ip(ip, list1, list2, list3): # Retorna True se estiver em alguma lista
    if (ip in list1):
        return True
    elif (ip in list2):
        return True
    elif (ip in list3):
        return True
    return False


def escrever_ips(list, nome_arq):
    with open(nome_arq, 'w') as arquivo:
        for ip in list:
            arquivo.write(ip + '\n')

def pingar_ips(list, nome_arq):
    ip_sem_resposta = []
    for ip in list:
        comando = ['ping', '-c', '1', ip]  # Adicionamos '-c 1' para enviar apenas um pacote de ping
        resultado = subprocess.run(comando, capture_output=True, text=True)
        res = resultado.stdout.split()
        if res[7] == "From": # Ping não teve resposta
            ip_sem_resposta.append(ip)
    escrever_ips(ip_sem_resposta, nome_arq)


def verificar_saida(list):
    for ip in list:
        comando = ['ping', '-c', '1', ip]  # Adicionamos '-c 1' para enviar apenas um pacote de ping
        resultado = subprocess.run(comando, capture_output=True, text=True)
        res = resultado.stdout.split()
        print(ip+" "+res[7]+"\n")

ip_test = get_ips("ips_teste.txt")

ips_grg = get_list_sheet("GRAGOATÁ", "G")
ips_prv = get_list_sheet("PRAIA VERMELHA", "G")
ips_val = get_list_sheet("VALONGUINHO", "G")
ips_ret = get_list_sheet("REITORIA", "G")
ips_bio = get_list_sheet("BIOMÉDICO", "G")
ips_far = get_list_sheet("FARMÁCIA", "G")
ips_enf = get_list_sheet("ENFERMAGEM", "G")
ips_vet = get_list_sheet("VETERINÁRIA", "G")
ips_meq = get_list_sheet("MEQUINHO", "G")


ip_livre =[]

for ip in ip_test:
    if check_ip(ip, ips_grg, ips_prv, ips_far):
        continue
    elif check_ip(ip, ips_enf, ips_bio, ips_ret):
        continue
    elif check_ip(ip, ips_meq, ips_val, ips_vet):
        continue
    ip_livre.append(ip)


#verificar_saida(ip_livre)
pingar_ips(ip_livre, "ips_livres.txt")

'''
Criar arquivos com os IPs de cada campus

escrever_ips(ips_grg, "ips_grg.txt")
escrever_ips(ips_prv, "ips_prv.txt")
escrever_ips(ips_val, "ips_val.txt")
escrever_ips(ips_ret, "ips_ret.txt")
escrever_ips(ips_bio, "ips_bio.txt")
escrever_ips(ips_far, "ips_far.txt")
escrever_ips(ips_enf, "ips_enf.txt")
escrever_ips(ips_vet, "ips_vet.txt")
escrever_ips(ips_meq, "ips_meq.txt")
'''