from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import smtplib
from email.message import EmailMessage
import time

def enviar_email(destinatario, titulo_vaga, descricao):
    EMAIL_ORIGEM = "" 
    SENHA_APP = "" #nao sejam estupidos e usem senha de app, é mais seguro e fácil de configurar do que OAuth2 para esse tipo de uso simples vcs podem criar uma senha de app no painel de segurança da google

    msg = EmailMessage()
    msg['Subject'] = f"Nova Vaga de {titulo_vaga} no VagaBot!"
    msg['From'] = EMAIL_ORIGEM
    msg['To'] = destinatario
    msg.set_content(f"Olá!\n\nEncontramos uma vaga que pode te interessar:\n\n{descricao}\n\nBoa sorte!")

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ORIGEM, SENHA_APP)
            smtp.send_message(msg)
        print(f"E-mail enviado com sucesso para {destinatario}")
        return True
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
        return False

def enviar_whatsapp(numero, titulo_vaga):
    from selenium.webdriver.common.action_chains import ActionChains

    print("Iniciando o Firefox para o WhatsApp Web...")
    
    # cara isso aqui é pq eu uso firefox, entao quer for apresentar usa firefox pq ta configurado pra ele, se quiser usar outro navegador é só mudar o webdriver e as opções, mas lembra de instalar o driver correspondente (chromedriver pro Chrome, geckodriver pro Firefox, etc)
    opcoes = Options()
    # opcoes.add_argument('--headless') # descomente essa linha se quiser que o navegador rode invisível
    
    driver = webdriver.Firefox(options=opcoes)
    
    try:
        mensagem = f"Olá! Passando para avisar que uma nova vaga de *{titulo_vaga}* acabou de ser cadastrada no sistema. Confira!"
        link = f"https://web.whatsapp.com/send?phone=55{numero}&text={mensagem}"
        driver.get(link)
        
        print("Aguardando o WhatsApp Web carregar e o QR Code ser escaneado...")
        
        wait = WebDriverWait(driver, 60)
        wait.until(EC.presence_of_element_located((By.ID, 'main')))
        
        time.sleep(5)
        ActionChains(driver).send_keys(Keys.ENTER).perform()
        time.sleep(3)
        
        print(f"WhatsApp enviado com sucesso para o número {numero}")
        return True
        
    except Exception as e:
        print(f"Erro ao enviar WhatsApp: {e}")
        return False
        
    finally:
        driver.quit()


if __name__ == "__main__":
    print("--- Teste do VagaBot RPA ---")