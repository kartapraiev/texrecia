# Ferramenta de análise estilométrica

Este projeto consiste em um conjunto de duas ferramentas Python projetadas para baixar e analisar documentos acadêmicos, especificamente do repositório da Universidade Federal do Pará (UFPA).

1.  **`ridl.py`**: Um web scraper para automatizar o download em massa de trabalhos de conclusão de curso (TCCs), dissertações e teses.
2.  **`main.py`**: Um analisador de estilometria que examina o texto de um arquivo PDF para identificar padrões e marcadores linguísticos comumente associados a modelos de linguagem de IA generativa.
3.  **`app.py` & `index.html`**: Uma interface gráfica web para usar o analisador de forma fácil e intuitiva, diretamente no navegador.

O objetivo do projeto é permitir a coleta de um corpo de textos acadêmicos e, em seguida, analisá-los individualmente em busca de indícios de geração por inteligência artificial.

## Componentes

### 1\. `ridl.py` - Downloader do Repositório (RIDL)

Este script automatiza a navegação e o download de documentos do [Repositório Institucional da UFPA](https://repositorio.ufpa.br/jspui).

#### Propósito

Coletar de forma eficiente um grande volume de documentos em formato PDF para análise posterior. Em vez de baixar manualmente cada arquivo, o script busca por palavras-chave (como nomes de cursos) e salva todos os resultados encontrados.

#### Funcionamento

O script utiliza as bibliotecas **Selenium** para controlar um navegador web (Google Chrome) e **Requests** para realizar o download dos arquivos de forma eficiente.

1.  **Inicialização**: O script configura e inicia uma instância do Google Chrome automatizada.
2.  **Busca**: Para cada palavra-chave definida (ex: "Direito", "Letras", "Ciência da Computação"), ele:
      * Acessa a página inicial do repositório.
      * Insere a palavra-chave no campo de busca e submete a pesquisa.
      * Ajusta a exibição de resultados para 100 itens por página, a fim de minimizar a navegação.
3.  **Navegação e Download**:
      * O script percorre cada item na página de resultados.
      * Para cada documento, ele abre o link em uma nova aba.
      * Na página do documento, ele clica no botão "Visualizar/Abrir", que abre o PDF em uma terceira aba.
      * Com a URL do PDF em mãos, ele utiliza a biblioteca `requests` para baixar o conteúdo do arquivo.
      * O arquivo é salvo em uma pasta local nomeada com a palavra-chave da busca (ex: `./Direito/`), e o nome do arquivo é uma versão sanitizada do título do trabalho.
4.  **Paginação**: Após baixar todos os documentos de uma página, o script procura pelo botão "Próximo" e repete o processo até que não haja mais páginas de resultados para a palavra-chave atual.
5.  **Finalização**: Ao concluir todas as palavras-chave, o navegador é fechado.

### 2\. `main.py` - Analisador de Estilometria de IA

Este script analisa o conteúdo textual de um único arquivo PDF para avaliar a probabilidade de ter sido gerado por um modelo de IA.

### 3\. `app.py` - Servidor da Interface Gráfica

Este script utiliza o micro-framework **Flask** para criar um servidor web local. Ele é responsável por:

  * Exibir a página da interface (`index.html`).
  * Receber o arquivo PDF enviado pelo usuário.
  * Chamar o script `main.py` em segundo plano para realizar a análise.
  * Retornar o relatório gerado para ser exibido na página.

## Como Usar

Existem duas maneiras de usar as ferramentas: através da interface gráfica (recomendado) ou via linha de comando.

### Modo 1: Interface Gráfica

Este modo é o mais simples e ideal para analisar arquivos individualmente.

#### Pré-requisitos

  * Python 3.x instalado.
  * Navegador Google Chrome instalado (apenas para o downloader `ridl.py`).

#### Instalação

Abra seu terminal ou prompt de comando e instale todas as bibliotecas necessárias com um único comando:

```bash
pip install selenium webdriver-manager requests pdfplumber Flask
```

#### Execução

**Passo 1: Baixar os Documentos**

Se você ainda não tem os PDFs para analisar, execute o script `ridl.py` para baixar os TCCs do repositório.

```bash
python ridl.py
```

Aguarde a conclusão. Os arquivos serão salvos em pastas como `Direito/`, `Letras/`, etc.

**Passo 2: Iniciar o Servidor da Aplicação Web**

No seu terminal, execute o script `app.py`:

```bash
python app.py
```

Você verá uma mensagem indicando que o servidor está rodando, algo como `Running on http://127.0.0.1:5000`.

**Passo 3: Usar a Interface no Navegador**

1.  Abra seu navegador de internet (Chrome, Firefox, etc.).
2.  Acesse o endereço: **[http://127.0.0.1:5000](https://www.google.com/url?sa=E&source=gmail&q=http://127.0.0.1:5000)**
3.  Na página, clique para selecionar um arquivo PDF ou simplesmente arraste e solte o arquivo na área indicada.
4.  Clique no botão **"Analisar Arquivo"**.
5.  Aguarde alguns segundos enquanto a análise é processada. O relatório completo aparecerá na tela.

### Modo 2: Linha de Comando (Uso Avançado)

Este modo é útil para automação ou se você preferir não usar a interface gráfica.

#### Instalação

As mesmas do modo gráfico. Se você já instalou, não precisa fazer novamente.

```bash
pip install selenium webdriver-manager requests pdfplumber
```

#### Execução

**Passo 1: Baixar os Documentos**

Use o script `ridl.py` conforme descrito no modo anterior.

**Passo 2: Analisar um Documento via Terminal**

Execute o script `main.py` passando o caminho do arquivo PDF como um argumento.

Por exemplo, para analisar um arquivo chamado `"TCC sobre Direito Digital.pdf"` salvo na pasta `Direito`:

```bash
python main.py "Direito/TCC sobre Direito Digital.pdf"
```

O relatório da análise será exibido diretamente no seu terminal.