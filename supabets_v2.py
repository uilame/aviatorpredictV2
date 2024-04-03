# Importando as bibliotecas necessárias do Selenium
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from time import sleep
import datetime
import pytz
import psutil
import httpx
from supabase import create_client, Client

# Substitua os valores abaixo pelos seus próprios
supabase_url: str = "https://butzalvizvitiezqdfma.supabase.co"
supabase_key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ1dHphbHZpenZpdGllenFkZm1hIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDkwNDE5MTMsImV4cCI6MjAyNDYxNzkxM30.ic7LeZWFzjXJCAaw2v9EGGD6y44BdzaXsAg3vLq3n4w"

# Crie o cliente Supabase
supabase: Client = create_client(supabase_url, supabase_key)

def read_cfg(numero_linha):
    try:
        with open('cfg.txt', 'r') as arquivo:
            linhas = arquivo.readlines()
            if 1 <= numero_linha <= len(linhas):
                linha_selecionada = linhas[numero_linha - 1].strip()
                return linha_selecionada
            else:
                return f"O arquivo tem {len(linhas)} linhas. Por favor, forneça um número de linha válido."
    except FileNotFoundError:
        return "O arquivo não foi encontrado."
    except Exception as e:
        return f"Ocorreu um erro: {str(e)}"


def send_webhook(resultados_str):
    print("STR:", resultados_str)
    padrao = ''
    data = datetime.datetime.now().strftime("%Y-%m-%d")
    fuso_horario = pytz.timezone('America/Sao_Paulo')
    hora_atual = datetime.datetime.now(tz=fuso_horario).strftime("%H:%M:%S")
    if float(resultados_str) >= 5:
        hora_tres_min = (datetime.datetime.now(tz=fuso_horario) + datetime.timedelta(minutes=3)).strftime(
            "%H:%M:%S")
        hora_cinco_min = (datetime.datetime.now(tz=fuso_horario) + datetime.timedelta(minutes=5)).strftime(
            "%H:%M:%S")
        hora_dez_min = (datetime.datetime.now(tz=fuso_horario) + datetime.timedelta(minutes=10)).strftime(
            "%H:%M:%S")

        minuto_tres = "#" + data + ":" + hora_tres_min.split(":")[0] + ":" + hora_tres_min.split(":")[1]
        minuto_cinco = "#" + data + ":" + hora_cinco_min.split(":")[0] + ":" + hora_cinco_min.split(":")[1]
        minuto_dez = "#" + data + ":" + hora_dez_min.split(":")[0] + ":" + hora_dez_min.split(":")[1]

        print("Data:", data)
        print("Hora Atual:", hora_atual)
        print("Hora 3 minutos:", minuto_tres)
        print("Hora 5 minutos:", minuto_cinco)
        print("Hora 10 minutos:", minuto_dez)

        # Abra o arquivo "horarios.txt" em modo anexação ("a")
        with open("horarios.txt", "a") as arquivo:
            # Escreva o valor no arquivo, incluindo um caractere de quebra de linha
            arquivo.write("*3*" + minuto_tres + "\n")
            arquivo.write("*5*" + minuto_cinco + "\n")
            arquivo.write("*10*" + minuto_dez + "\n")
        # Abra o arquivo "horarios.txt" em modo leitura
        with open("horarios.txt", "r") as arquivo:
            linhas = arquivo.readlines()
            for linha in linhas:
                if data + ":" + hora_atual.split(":")[0] + ":" + hora_atual.split(":")[1] in linha.split("#")[1]:
                    padrao = linha.split("#")[0]
    else:
        hora_tres_min = ''
        hora_cinco_min = ''
        hora_dez_min = ''

    sheet_name = read_cfg(1)
    sleep(2)
    try:
        data, count = supabase.table('bets').insert({
            "id_cliente": 1,
            "casa": sheet_name,
            "vela": f"'{str(resultados_str).replace('.', ',')}'",
            "data": f"'{data}'",
            "hora": f"'{hora_atual}'",
            "padrao": f"'{padrao}'",
            "hora_tres_min": f"'{hora_tres_min}'",
            "hora_cinco_min": f"'{hora_cinco_min}'",
            "hora_dez_min": f"'{hora_dez_min}'"
        }).execute()
    except NoSuchElementException:
        # Lidar com a exceção, por exemplo, imprimir uma mensagem ou pausar o código
        print("Erro no envio do webhook...")

def is_chromedriver_running():
    for process in psutil.process_iter(['pid', 'name']):
        if 'chromedriver' in process.info['name'].lower():
            return True
    return False


# Especifique o diretório para armazenar os dados do usuário
user_data_dir = read_cfg(6)

if not is_chromedriver_running():
    # Configurando e iniciando o serviço do WebDriver para o Chrome
    webdriver_service = webdriver.chrome.service.Service(ChromeDriverManager().install())
    webdriver_service.start()

    # Configurando as opções do Chrome
    options = webdriver.ChromeOptions()
    # Descomente a linha abaixo se quiser executar o navegador em modo headless (sem interface gráfica)
    # options.add_argument('--headless')
    options.add_argument('--disable-logging')
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-popup-blocking')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument(f"--user-data-dir={user_data_dir}")
    options.add_experimental_option('w3c', True)

    # Iniciando o driver remoto do Chrome com as opções configuradas
    driver = webdriver.Remote(webdriver_service.service_url, options=options)

    # Maximizando a janela do navegador
    driver.maximize_window()

def start_aposta1():
    driver.get('https://www.aposta1.com/games/jogar/aviator')
    sleep(30)
    try:
        # Utilizando WebDriverWait para aguardar a presença do iframe
        wait = WebDriverWait(driver, 60)  # Você pode ajustar o tempo limite conforme necessário
        try:
            iframe = driver.find_element(By.CLASS_NAME, 'play-frame')
        except NoSuchElementException:
            # Lidar com a exceção, por exemplo, imprimir uma mensagem ou pausar o código
            print("Elemento Frame Não Encontrado. Aguardando...")
            start_aposta1()
        except NoSuchElementException:
            # Lidar com a exceção NoSuchElementException, por exemplo, imprimir uma mensagem ou pausar o código
            print("Elemento Frame Não Encontrado. Aguardando...")
            start_aposta1()
        except WebDriverException as e:
            # Lidar com outras exceções do WebDriver, por exemplo, imprimir uma mensagem de erro
            print("Ocorreu uma exceção não prevista:", e)
            start_aposta1()
            # Possivelmente adicionar mais ações para lidar com a exceção, como fechar o navegador ou registrar o erro em um arquivo de log

        driver.switch_to.frame(iframe)

        # Aguardando por 60 segundos (tempo definido por sleep)
        sleep(40)

        # Loop principal
        while True:
            # Obtendo resultados do elemento e convertendo para uma lista de números
            try:
                ec = driver.find_elements(By.CLASS_NAME, 'payout.ng-star-inserted')
                resultados = []
                for n in ec[:5]:
                    valueVela = n.text.replace('x', '')
                    if valueVela:
                        try:
                            resultados.append(float(valueVela))
                        except NoSuchElementException:
                            print("VALUE NOT FOUND...")
                resultados_str = resultados[0]
                print(f'Resultados: {resultados}')
                try:
                    send_webhook(resultados_str)
                except httpx.ConnectTimeout:
                    # Lidar com a exceção, por exemplo, imprimir uma mensagem ou pausar o código
                    print("Erro no envio do webhook...")
                    sleep(6)
            except NoSuchElementException:
                # Lidar com a exceção, por exemplo, imprimir uma mensagem ou pausar o código
                print("Elemento não encontrado. Aguardando...")
                # start_aposta1()

            # Segundo loop interno
            while True:
                # Aguardando a presença do elemento antes de interagir com ele novamente
                try:
                    ec = driver.find_elements(By.CLASS_NAME, 'payout.ng-star-inserted')
                except NoSuchElementException:
                    # Lidar com a exceção, por exemplo, imprimir uma mensagem ou pausar o código
                    print("Elemento não encontrado. Aguardando...")
                    # start_aposta1()
                if ec:
                    try:
                        verificacao = []
                        for n in ec[:5]:
                            try:
                                valueVela = n.text.replace('x', '')
                            except StaleElementReferenceException:
                                print("Elemento não encontrado. Aguardando...")

                            if valueVela:
                                try:
                                    verificacao.append(float(valueVela))
                                except NoSuchElementException:
                                    # Lidar com a exceção, por exemplo, imprimir uma mensagem ou pausar o código
                                    print("Elemento não encontrado. Aguardando...")
                        if verificacao != resultados:
                            break
                    except NoSuchElementException:
                        # Lidar com a exceção, por exemplo, imprimir uma mensagem ou pausar o código
                        print("Elemento não encontrado. Aguardando...")
                        # start_aposta1()
                else:
                    start_aposta1()
    except NoSuchElementException:
        # Lidar com a exceção externa
        print("Elemento não encontrado. Tentando novamente...")
        # start_aposta1()

start_aposta1()