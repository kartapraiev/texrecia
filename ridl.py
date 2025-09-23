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
    """
    Remove caracteres inválidos de um nome de arquivo para que ele possa ser salvo no sistema.
    """
    # Remove caracteres que não são permitidos em nomes de arquivo no Windows/Linux/Mac
    sanitized = re.sub(r'[\\/*?:"<>|]', "", filename)
    # Limita o comprimento para evitar erros de "nome de arquivo muito longo"
    return (sanitized[:200] + '...') if len(sanitized) > 200 else sanitized

def setup_driver():
    """
    Configura e inicializa o navegador Chrome com o Selenium.
    """
    print("Configurando o driver do navegador...")
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # Descomente esta linha para executar o navegador em segundo plano (sem interface gráfica)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")
    # ADICIONADO: Opções para reduzir "ruído" no console e evitar erros gráficos.
    options.add_argument("--disable-gpu")
    options.add_argument('--log-level=3') 
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    # Instala e gerencia automaticamente o driver do Chrome
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def download_pdfs_for_keyword(driver, keyword):
    """
    Função principal que busca por uma palavra-chave, navega pelos resultados e baixa todos os PDFs encontrados.
    """
    base_url = "https://repositorio.ufpa.br/jspui"
    
    print(f"\n=================================================")
    print(f"Iniciando busca pela palavra-chave: '{keyword}'")
    print(f"=================================================")

    # Cria uma pasta para a palavra-chave, se ainda não existir
    os.makedirs(keyword, exist_ok=True)

    try:
        # 1. Navega para a página inicial
        driver.get(base_url)
        wait = WebDriverWait(driver, 20)
        
        # ADICIONADO: Lida com o banner de consentimento de cookies se ele aparecer
        try:
            cookie_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'OK')]")))
            print("Banner de cookies encontrado. Clicando em 'OK'.")
            cookie_button.click()
        except TimeoutException:
            print("Nenhum banner de cookies encontrado.")

        # 2. Encontra a caixa de pesquisa, insere a palavra-chave e submete o formulário
        print(f"Pesquisando por '{keyword}' na página inicial...")
        
        # ADICIONADO: Mecanismo de repetição para tornar a busca mais robusta.
        # Tenta encontrar a caixa de pesquisa 3 vezes, recarregando a página se falhar.
        search_box = None
        for attempt in range(3):
            try:
                search_box = wait.until(EC.presence_of_element_located((By.ID, "tfocus")))
                print(f"Caixa de pesquisa encontrada na tentativa {attempt + 1}.")
                break  # Sai do loop se o elemento for encontrado
            except TimeoutException:
                print(f"Tentativa {attempt + 1} falhou. Recarregando a página para tentar novamente...")
                driver.refresh()
                # Espera o body carregar novamente após o refresh
                wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Se a caixa de pesquisa não for encontrada após as tentativas, pula para a próxima palavra-chave
        if not search_box:
            print(f"ERRO CRÍTICO: Não foi possível encontrar a caixa de pesquisa para '{keyword}' após 3 tentativas. Pulando.")
            return

        search_box.clear() # Limpa o campo caso haja texto de uma busca anterior
        search_box.send_keys(keyword)
        search_box.submit() # Submete o formulário (equivalente a apertar Enter)

        # Espera explícita para o contêiner de resultados carregar após a busca.
        print("Aguardando a página de resultados carregar...")
        wait.until(EC.presence_of_element_located((By.ID, "aspect_discovery_SimpleSearch_div_search-results")))

        # 3. Altera a quantidade de resultados por página para 100
        print("Alterando resultados por página para 100...")
        rpp_select_element = wait.until(EC.element_to_be_clickable((By.NAME, "rpp")))
        Select(rpp_select_element).select_by_value("100")
        
        update_rpp_button = wait.until(EC.element_to_be_clickable((By.NAME, "submit_rpp")))
        update_rpp_button.click()
        
        page_number = 1
        
        # Loop para navegar entre as páginas de resultados
        while True:
            print(f"\n--- Processando página {page_number} de resultados para '{keyword}' ---")
            
            # Espera a página carregar e pega todos os links dos títulos dos documentos
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.artifact-description")))
            
            # Pega todos os handles das abas antes de começar a baixar da página atual
            main_tab = driver.current_window_handle
            
            # Coleta os links e títulos para evitar "StaleElementReferenceException"
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

            # 4. Itera sobre cada documento da página
            for i, item in enumerate(items_to_download):
                print(f"  ({i+1}/{len(items_to_download)}) Baixando: {item['title']}")
                
                try:
                    # Abre o link do documento em uma nova aba
                    driver.execute_script("window.open(arguments[0]);", item['link'])
                    doc_tab = driver.window_handles[1]
                    driver.switch_to.window(doc_tab)
                    
                    # 5. Clica no botão "Visualizar/Abrir" (View/Open)
                    view_open_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Visualizar/Abrir')]")))
                    view_open_button.click()
                    
                    # Espera a aba do PDF abrir e muda para ela
                    wait.until(lambda d: len(d.window_handles) == 3)
                    pdf_tab = driver.window_handles[2]
                    driver.switch_to.window(pdf_tab)
                    
                    # Pequena pausa para a URL do PDF carregar completamente
                    time.sleep(3) 
                    pdf_url = driver.current_url
                    
                    # 6. Salva o PDF usando a biblioteca requests
                    response = requests.get(pdf_url, stream=True, timeout=30)
                    if response.status_code == 200:
                        filepath = os.path.join(keyword, f"{item['title']}.pdf")
                        with open(filepath, "wb") as f:
                            f.write(response.content)
                        print(f"    -> Salvo com sucesso em: {filepath}")
                    else:
                        print(f"    -> ERRO: Falha ao baixar PDF. Status: {response.status_code}")

                    # 7. Fecha as abas do PDF e do documento, retornando para a aba principal
                    driver.close() # Fecha aba do PDF
                    driver.switch_to.window(doc_tab)
                    driver.close() # Fecha aba do documento
                    driver.switch_to.window(main_tab)

                except Exception as e:
                    print(f"    -> ERRO ao processar o item '{item['title']}'. Pulando. Detalhes: {e}")
                    # Garante que as abas extras sejam fechadas em caso de erro
                    while len(driver.window_handles) > 1:
                        driver.switch_to.window(driver.window_handles[-1])
                        driver.close()
                    driver.switch_to.window(main_tab)
            
            # 8. Procura pelo botão "Próximo" (Next) para ir para a próxima página
            try:
                next_page_button = driver.find_element(By.CSS_SELECTOR, "a.next-page-link")
                print("\nIndo para a próxima página...")
                next_page_button.click()
                page_number += 1
            except NoSuchElementException:
                print(f"\nFim dos resultados para '{keyword}'. Não há mais páginas.")
                break # Sai do loop while se não houver botão "Próximo"

    except Exception as e:
        print(f"Ocorreu um erro inesperado durante a automação para '{keyword}': {e}")


def main():
    """
    Função principal que orquestra todo o processo.
    """
    keywords_to_download = ["Direito", "Letras", "Ciência da Computação"]
    driver = None
    try:
        driver = setup_driver()
        for keyword in keywords_to_download:
            download_pdfs_for_keyword(driver, keyword)
        print("\n=================================================")
        print("TODOS OS DOWNLOADS FORAM CONCLUÍDOS!")
        print("=================================================")
    finally:
        if driver:
            print("Fechando o navegador...")
            driver.quit()

if __name__ == "__main__":
    main()