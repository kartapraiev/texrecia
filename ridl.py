import os
import time
import requests
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def sanitize_filename(filename):
    sanitized = re.sub(r'[\\/*?:"<>|]', "", filename)
    return (sanitized[:200] + '...') if len(sanitized) > 200 else sanitized

def setup_driver():
    print("Configurando o driver do navegador...")
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-gpu")
    options.add_argument('--log-level=3') 
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def download_pdfs_for_keyword(driver, keyword):
    base_url = "https://repositorio.ufpa.br/jspui"
    
    print(f"Iniciando busca pela palavra-chave: '{keyword}'")

    os.makedirs(keyword, exist_ok=True)

    try:
        driver.get(base_url)
        wait = WebDriverWait(driver, 20)
        
        try:
            cookie_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'OK')]")))
            print("Banner de cookies encontrado. Clicando em 'OK'.")
            cookie_button.click()
        except TimeoutException:
            print("Nenhum banner de cookies encontrado.")

        print(f"Pesquisando por '{keyword}' na página inicial...")
        
        search_box = None
        for attempt in range(3):
            try:
                search_box = wait.until(EC.presence_of_element_located((By.ID, "tfocus")))
                print(f"Caixa de pesquisa encontrada na tentativa {attempt + 1}.")
                break
            except TimeoutException:
                print(f"Tentativa {attempt + 1} falhou. Recarregando a página para tentar novamente...")
                driver.refresh()
                wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        if not search_box:
            print(f"ERRO CRÍTICO: Não foi possível encontrar a caixa de pesquisa para '{keyword}' após 3 tentativas. Pulando.")
            return

        search_box.clear()
        search_box.send_keys(keyword)
        search_box.submit()

        print("Aguardando a página de resultados carregar...")
        wait.until(EC.presence_of_element_located((By.ID, "aspect_discovery_SimpleSearch_div_search-results")))

        print("Alterando resultados por página para 100...")
        rpp_select_element = wait.until(EC.element_to_be_clickable((By.NAME, "rpp")))
        Select(rpp_select_element).select_by_value("100")
        
        update_rpp_button = wait.until(EC.element_to_be_clickable((By.NAME, "submit_rpp")))
        update_rpp_button.click()
        
        page_number = 1
        
        while True:
            print(f"\n--- Processando página {page_number} de resultados para '{keyword}' ---")
            
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.artifact-description")))
            
            main_tab = driver.current_window_handle
            
            items_to_download = []
            try:
                artifact_wrappers = driver.find_elements(By.CSS_SELECTOR, "div.artifact-browser-item")
                for item in artifact_wrappers:
                    title_element = item.find_element(By.CSS_SELECTOR, "div.artifact-title a")
                    link = title_element.get_attribute("href")
                    title = sanitize_filename(title_element.text)
                    items_to_download.append({"title": title, "link": link})
            except NoSuchElementException:
                print("Nenhum item encontrado nesta página.")
                break

            if not items_to_download:
                print("Não foram encontrados mais documentos para baixar.")
                break

            for i, item in enumerate(items_to_download):
                print(f"  ({i+1}/{len(items_to_download)}) Baixando: {item['title']}")
                
                try:
                    driver.execute_script("window.open(arguments[0]);", item['link'])
                    doc_tab = driver.window_handles[1]
                    driver.switch_to.window(doc_tab)
                    
                    view_open_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Visualizar/Abrir')]")))
                    view_open_button.click()
                    
                    wait.until(lambda d: len(d.window_handles) == 3)
                    pdf_tab = driver.window_handles[2]
                    driver.switch_to.window(pdf_tab)
                    
                    time.sleep(3) 
                    pdf_url = driver.current_url
                    
                    response = requests.get(pdf_url, stream=True, timeout=30)
                    if response.status_code == 200:
                        filepath = os.path.join(keyword, f"{item['title']}.pdf")
                        with open(filepath, "wb") as f:
                            f.write(response.content)
                        print(f"    -> Salvo com sucesso em: {filepath}")
                    else:
                        print(f"    -> ERRO: Falha ao baixar PDF. Status: {response.status_code}")

                    driver.close()
                    driver.switch_to.window(doc_tab)
                    driver.close()
                    driver.switch_to.window(main_tab)

                except Exception as e:
                    print(f"    -> ERRO ao processar o item '{item['title']}'. Pulando. Detalhes: {e}")
                    while len(driver.window_handles) > 1:
                        driver.switch_to.window(driver.window_handles[-1])
                        driver.close()
                    driver.switch_to.window(main_tab)
            
            try:
                next_page_button = driver.find_element(By.CSS_SELECTOR, "a.next-page-link")
                print("\nIndo para a próxima página...")
                next_page_button.click()
                page_number += 1
            except NoSuchElementException:
                print(f"\nFim dos resultados para '{keyword}'. Não há mais páginas.")
                break

    except Exception as e:
        print(f"Ocorreu um erro inesperado durante a automação para '{keyword}': {e}")


def main():
    keywords_to_download = ["Direito", "Letras", "Ciência da Computação"]
    driver = None
    try:
        driver = setup_driver()
        for keyword in keywords_to_download:
            download_pdfs_for_keyword(driver, keyword)
        print("TODOS OS DOWNLOADS FORAM CONCLUÍDOS!")
    finally:
        if driver:
            print("Fechando o navegador...")
            driver.quit()

if __name__ == "__main__":
    main()