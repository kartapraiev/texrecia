import pdfplumber
import re
import collections
import sys
import os

AI_GENERAL_MARKERS = {
    "phrases": [
        "é importante destacar que",
        "em suma",
        "em resumo",
        "além disso",
        "consequentemente",
        "that being said",
        "at its core",
        "to put it simply",
        "this underscores the importance of",
        "from a broader perspective"
    ]
}

CHATGPT_MARKERS = {
    "phrases": [
        "vamos mergulhar neste tópico",
        "it's important to note",
        "navigating the complexities of",
        "as an al language model",
        "generally speaking",
        "broadly speaking"
    ],
    "words": [
        "robusto", "tapeçaria", "alavancar", "nuanceado",
        "delve", "tapestry", "vibrant", "landscape", "realm", "intricate", "pivotal", "moreover",
        "utilizar",
        "align", "underscore", "noteworthy", "versatile", "commendable",
        "arguably", "facilitate", "bolster", "differentiate", "implication", "complexity"
    ]
}

GEMINI_MARKERS = {
    "phrases": [
        "explore mais sobre",
        "com base em dados",
        "vamos analisar passo a passo"
    ],
    "words": [
        "generate", "summarise", "analyze", "explore",
        "sugar"
    ]
}

DEEPSEEK_MARKERS = {
    "phrases": [
        "com base em meu treinamento",
        "posso ajudar com",
        "a beat.",
        "somewhere in the distance"
    ],
    "words": []
}

HIDDEN_CHARS = {
    '\u200b': "Espaço de Largura Zero (U+200B)",
    '\u200c': "Não-Conector de Largura Zero (U+200C)",
    '\u200d': "Conector de Largura Zero (U+200D)",
    '\ufeff': "Marca de Ordem de Byte (BOM) (U+FEFF)",
    '\u2014': "Travessão (Em Dash) (U+2014)",
    '\u201c': "Aspas Duplas Abertas (U+201C)",
    '\u201d': "Aspas Duplas Fechadas (U+201D)",
    '\u2018': "Aspas Simples Abertas (U+2018)",
    '\u2019': "Aspas Simples Fechadas (U+2019)",
    '\u00a0': "Espaço Não-Quebrável (U+00A0)",
    '\u202f': "Espaço Estreito Não-Quebrável (U+202F)"
}

class AIStylometryAnalyzer:
    def __init__(self, pdf_path):
        if not os.path.exists(pdf_path):
            print(f"Erro: O arquivo '{pdf_path}' não foi encontrado.")
            sys.exit(1)
        self.pdf_path = pdf_path
        self.raw_text = self._extract_text()
        if not self.raw_text:
            print("Erro: Não foi possível extrair texto do PDF. O arquivo pode estar vazio ou ser uma imagem.")
            sys.exit(1)
        self.clean_text = self._preprocess_text(self.raw_text)
        self.tokens = self.clean_text.split()
        self.word_count = len(self.tokens)

    def _extract_text(self):
        print(f"📄 Extraindo texto de '{os.path.basename(self.pdf_path)}'...")
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                full_text = "".join(page.extract_text() or "" for page in pdf.pages)
            return full_text
        except Exception as e:
            print(f"Ocorreu um erro ao ler o PDF: {e}")
            return None

    def _preprocess_text(self, text):
        text_lower = text.lower()
        clean_text = re.sub(r'[^\w\s\'-]', ' ', text_lower)
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        return clean_text

    def analyze_word_frequency(self, top_n=15):
        if not self.tokens:
            return {}, 0        
        meaningful_tokens = [token for token in self.tokens if len(token) > 2]
        word_counts = collections.Counter(meaningful_tokens)
        return word_counts.most_common(top_n)

    def detect_hidden_characters(self):
        found_chars = collections.defaultdict(int)
        for char in self.raw_text:
            if char in HIDDEN_CHARS:
                found_chars[HIDDEN_CHARS[char]] += 1
        return dict(found_chars)

    def _calculate_score(self, markers):
        score = 0
        found_markers = collections.defaultdict(int)
        for phrase in markers.get("phrases", []):
            count = self.clean_text.count(phrase)
            if count > 0:
                score += count * 2
                found_markers[phrase] = count
        
        for word in markers.get("words", []):
            count = len(re.findall(r'\b' + re.escape(word) + r'\b', self.clean_text))
            if count > 0:
                score += count
                found_markers[word] = count
                
        return score, dict(found_markers)

    def analyze_ai_stylometry(self):
        results = {}
        
        models = {
            "Geral de IA": AI_GENERAL_MARKERS,
            "ChatGPT": CHATGPT_MARKERS,
            "Gemini": GEMINI_MARKERS,
            "DeepSeek": DEEPSEEK_MARKERS
        }
        
        for model_name, markers in models.items():
            score, found = self._calculate_score(markers)
            normalized_score = (score / self.word_count * 1000) if self.word_count > 0 else 0
            results[model_name] = {
                "score": score,
                "normalized_score": normalized_score,
                "found_markers": found
            }
            
        return results

    def generate_report(self):
        print("\n" + "="*80)
        print(" " * 25 + "RELATÓRIO DE ANÁLISE ESTILOMÉTRICA")
        print("="*80)
        print(f"Analisando o arquivo: {self.pdf_path}")
        print(f"Total de palavras analisadas: {self.word_count}\n")

        print("-" * 30 + "\nPalavras mais frequentes\n" + "-" * 30)
        top_words = self.analyze_word_frequency()
        if top_words:
            for word, count in top_words:
                print(f"  - '{word}': {count} vezes")
        else:
            print("  - Nenhuma palavra com mais de 2 caracteres foi encontrada.")
        print("\n")

        print("-" * 30 + "\nDetecção de caracteres\n" + "-" * 30)
        hidden_chars = self.detect_hidden_characters()
        if hidden_chars:
            for char, count in hidden_chars.items():
                print(f"  - {char}: {count} ocorrências")
        else:
            print("  - Nenhum caractere oculto ou de formatação especial foi detectado.")
        print("\n")

        print("-" * 30 + "\nAnálise de estilometria\n" + "-" * 30)
        style_results = self.analyze_ai_stylometry()
        
        model_scores = {
            name: data for name, data in style_results.items() if name != "Geral de IA"
        }
        
        if any(data['score'] > 0 for data in model_scores.values()):
            sorted_models = sorted(model_scores.items(), key=lambda item: item[1]['normalized_score'], reverse=True)
            
            most_likely_author, highest_score_data = sorted_models[0]
            
            print(f"Autor mais provável: {most_likely_author} (Pontuação normalizada: {highest_score_data['normalized_score']:.2f})\n")
            
            for model_name, data in sorted_models:
                print(f"--- {model_name} (Pontuação: {data['score']}, normalizada: {data['normalized_score']:.2f}) ---")
                if data['found_markers']:
                    for marker, count in data['found_markers'].items():
                        print(f"  - Encontrado '{marker}': {count} vez(es)")
                else:
                    print("  - Nenhum marcador específico encontrado.")
                print()
            
            general_data = style_results["Geral de IA"]
            print(f"--- Marcadores gerais de IA (Pontuação: {general_data['score']}) ---")
            if general_data['found_markers']:
                 for marker, count in general_data['found_markers'].items():
                    print(f"  - Encontrado '{marker}': {count} vez(es)")
            else:
                print("  - Nenhum marcador geral de IA encontrado.")
            print()

        else:
            print("  - O texto não apresentou marcadores estilísticos fortes de nenhum dos modelos de IA analisados.")
            
        print("="*80)
        print("Nota: Esta análise é baseada em padrões estatísticos e estilísticos. A pontuação normalizada \n(ocorrências a cada 1000 palavras) ajuda a comparar textos de diferentes tamanhos.")
        print("="*80)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python seu_script.py /caminho/para/seu/arquivo.pdf")
        sys.exit(1)
        
    pdf_file_path = sys.argv[1]
    analyzer = AIStylometryAnalyzer(pdf_file_path)
    analyzer.generate_report()