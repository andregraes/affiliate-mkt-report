import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime

# Configuração inicial
#driver_path = 'caminho/para/seu/msedgedriver'
base_url = 'https://cbsnooper.com/reports/top-clickbank-products?table[sorts][latestStats.gravity_movement]=desc&table[filters][minimum_initial%24]=30&table[filters][minimum_average%24]=45&table[filters][minimum_gravity]=5&page={page}#google_vignette'
product_base_url = 'https://cbsnooper.com/products/'
csv_file_path = "D:\python\projects\wrongscrapper\produtos_clickbank.csv"
total_pages = 5

# Iniciar o WebDriver
driver = webdriver.Edge()


# Função para escrever os dados no arquivo CSV
def write_to_csv(data):
    with open(csv_file_path, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(data)


# Inicializar o arquivo CSV com o cabeçalho
with open(csv_file_path, 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Rank', 'Product Name', 'Title', 'Gravity', 'Movement', 'Initial $/Sale', 'Av $/Sale', 'Rebill $',
                     'First Seen Date'])


# Função para converter a data no formato desejado
def convert_date(date_str):
    try:
        date_obj = datetime.strptime(date_str, '%a, %b %d, %Y')
        return date_obj.strftime('%Y-%m-%d')
    except ValueError:
        return ''


try:
    for page in range(1, total_pages + 1):
        driver.get(base_url.format(page=page))

        # Esperar e clicar no botão de consentimento de cookies (apenas na primeira página)
        if page == 1:
            consent_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.fc-button.fc-cta-consent.fc-primary-button"))
            )
            consent_button.click()

            # Esperar a página carregar e encontrar o combobox para mudar para 50 produtos por página
            per_page_select = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "perPage"))
            )
            per_page_select.click()
            per_page_option = driver.find_element(By.XPATH, "//option[@value='50']")
            per_page_option.click()

            time.sleep(5)  # Esperar a página recarregar

        # Coletar informações da página atual
        products = driver.find_elements(By.CSS_SELECTOR, 'tr.cursor-pointer')

        for product in products:
            rank = product.find_element(By.CSS_SELECTOR, 'td:nth-child(1)').text
            name = product.find_element(By.CSS_SELECTOR, 'td:nth-child(2)').text
            title = product.find_element(By.CSS_SELECTOR, 'td:nth-child(3)').text
            gravity = product.find_element(By.CSS_SELECTOR, 'td:nth-child(4)').text
            movement = product.find_element(By.CSS_SELECTOR, 'td:nth-child(5)').text
            initial_sale = product.find_element(By.CSS_SELECTOR, 'td:nth-child(6)').text
            av_sale = product.find_element(By.CSS_SELECTOR, 'td:nth-child(7)').text
            rebill = product.find_element(By.CSS_SELECTOR, 'td:nth-child(8)').text

            # Acessar a página do produto para obter a data de "First Seen"
            product_identifier = name.strip()
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[1])
            driver.get(product_base_url + product_identifier)

            try:
                first_seen_date_elem = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "p.font-semibold.text-right.text-base.mb-2"))
                )
                first_seen_date = first_seen_date_elem.text
                formatted_date = convert_date(first_seen_date)
            except:
                formatted_date = ''

            print(
                f'Rank: {rank}, Name: {name}, Title: {title}, Gravity: {gravity}, Movement: {movement}, Initial $/Sale: {initial_sale}, Av $/Sale: {av_sale}, Rebill $: {rebill}, First Seen Date: {formatted_date}')

            # Escrever os dados no arquivo CSV
            write_to_csv([rank, name, title, gravity, movement, initial_sale, av_sale, rebill, formatted_date])

            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            time.sleep(1)  # Pequeno atraso para evitar erro de referência obsoleta

finally:
    # Fechar o WebDriver
    driver.quit()
