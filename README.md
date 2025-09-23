# Ferramenta de análise estilométrica

Este projeto consiste em um conjunto de duas ferramentas Python projetadas para baixar e analisar documentos acadêmicos, especificamente do repositório da Universidade Federal do Pará (UFPA).

1.  **`ridl.py`**: Um web scraper para automatizar o download em massa de trabalhos de conclusão de curso (TCCs), dissertações e teses.
2.  **`main.py`**: Um analisador de estilometria que examina o texto de um arquivo PDF para identificar padrões e marcadores linguísticos comumente associados a modelos de linguagem de IA generativa.

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

#### Propósito

Fornecer uma análise estatística e baseada em marcadores sobre o estilo de escrita de um documento. Ele serve como uma ferramenta auxiliar para identificar textos que se desviam dos padrões de escrita humana e se alinham com os de IAs conhecidas.

#### Funcionamento

O script utiliza a biblioteca **pdfplumber** para extrair texto de arquivos PDF e realiza uma série de análises.

1.  **Extração e Pré-processamento**:
      * O script abre o arquivo PDF especificado e extrai todo o seu conteúdo textual.
      * O texto é "limpo": convertido para minúsculas, e a maioria dos caracteres especiais e pontuações é removida para focar apenas nas palavras.
2.  **Análise de Frequência**: Conta as palavras mais comuns no documento para dar uma visão geral do vocabulário utilizado.
3.  **Detecção de Marcadores (Stylometry)**:
      * O núcleo da análise. O script possui dicionários pré-definidos com palavras e frases ("marcadores") que são estatisticamente mais comuns em textos gerados por IAs como **ChatGPT**, **Gemini**, e **DeepSeek**.
      * Exemplos de marcadores incluem "é importante destacar que", "em suma" (geral), "robusto", "alavancar", "tapeçaria" (ChatGPT), entre outros.
4.  **Cálculo de Pontuação**:
      * O script varre o texto em busca desses marcadores.
      * Uma pontuação é atribuída com base no número de marcadores encontrados. Frases têm um peso maior que palavras isoladas.
      * Uma **pontuação normalizada** (ocorrências a cada 1000 palavras) é calculada para permitir a comparação justa entre documentos de diferentes tamanhos.
5.  **Geração de Relatório**:
      * Um relatório é impresso no terminal, contendo:
          * O total de palavras analisadas.
          * As palavras mais frequentes.
          * A detecção de caracteres "ocultos" ou de formatação especial.
          * Uma conclusão sobre o "autor mais provável" (a IA com a maior pontuação normalizada).
          * Um detalhamento dos marcadores específicos encontrados para cada modelo de IA.

## Como Usar

### Pré-requisitos

  * Python 3.x instalado.
  * Navegador Google Chrome instalado.

### Instalação

Abra seu terminal ou prompt de comando e instale as bibliotecas necessárias:

```bash
pip install selenium webdriver-manager requests pdfplumber
```

### Execução Passo a Passo

**Passo 1: Baixar os Documentos**

Execute o script `ridl.py` para começar o download dos TCCs. Ele criará pastas no mesmo diretório onde o script está localizado.

```bash
python ridl.py
```

Aguarde a conclusão. Este processo pode demorar dependendo da sua conexão com a internet e da quantidade de documentos.

**Passo 2: Analisar um Documento**

Após o download, escolha um dos PDFs baixados e use o script `main.py` para analisá-lo. Você deve passar o caminho do arquivo como um argumento na linha de comando.

Por exemplo, para analisar um arquivo chamado `"TCC sobre Direito Digital.pdf"` que foi salvo na pasta `Direito`:

```bash
python main.py "Direito/TCC sobre Direito Digital.pdf"
```

O relatório da análise será exibido diretamente no seu terminal.

-----