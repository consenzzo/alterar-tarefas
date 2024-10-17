import os
import openai
import PyPDF2  # Para PDF
import docx  # Para arquivos .docx
import pypandoc
from dotenv import load_dotenv
from fpdf import FPDF

load_dotenv()
# Obter a chave da API da variável de ambiente
openai.api_key = os.getenv("OPENAI_API_KEY")

def processar_documento(arquivo):
    """Processa um documento e retorna uma lista de exercícios."""
    texto = ""
    if arquivo.endswith(".pdf"):
        with open(arquivo, 'rb') as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                texto += page.extract_text()
    elif arquivo.endswith(".txt"):
        with open(arquivo, 'r', encoding='utf-8') as txt_file:
            texto = txt_file.read()
    elif arquivo.endswith(".doc") or arquivo.endswith(".docx"):
        try:
            # Se for .doc, converte para .docx usando pypandoc
            if arquivo.endswith(".doc"):
                novo_arquivo = arquivo + 'x'  # Cria o nome do novo arquivo .docx
                pypandoc.convert_file(arquivo, 'docx', outputfile=novo_arquivo)
                arquivo_para_processar = novo_arquivo
            else:
                arquivo_para_processar = arquivo

            doc = docx.Document(arquivo_para_processar)
            full_text = []
            for para in doc.paragraphs:
                full_text.append(para.text)
            texto = '\n'.join(full_text)

            # Remove o arquivo .docx temporário se ele foi criado
            if arquivo.endswith(".doc") and os.path.exists(novo_arquivo):
                os.remove(novo_arquivo)
        except Exception as e:
            print(f"Erro ao processar o arquivo .doc/.docx: {e}")
            texto = ""
    else:
        print("Formato de arquivo não suportado.")
        texto = ""

    # Dividir o texto em exercícios (implementar lógica de divisão aqui)
    # Por exemplo, pode-se dividir por quebras de linha duplas ou por palavras-chave
    exercicios = texto.split("\n\n")
    return exercicios

def adaptar_exercicios(exercicios, comandos):
    """Adapta os exercícios usando a API da OpenAI."""
    exercicios_adaptados = []
    for exercicio, comando in zip(exercicios, comandos):
        prompt = f"Adapte o seguinte exercício de acordo com o comando: {comando}\nExercício: {exercicio}"
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente que adapta provas para pessoas neurodivergentes."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2048,
            temperature=0.7,
        )
        exercicios_adaptados.append(response.choices[0].message)
    return exercicios_adaptados

def criar_arquivo_texto(exercicios_adaptados, nome_arquivo="exercicios_adaptados.txt"):
    """Cria um arquivo de texto a partir da lista de exercícios adaptados."""
    with open(nome_arquivo, 'w', encoding='utf-8') as arquivo:
        for exercicio in exercicios_adaptados:
            # Extrair o conteúdo textual do objeto ChatCompletionMessage
            texto_exercicio = exercicio.content
            arquivo.write(texto_exercicio + '\n')

executar = input('Informe sim para rodar: ')

if executar.lower() == 'sim':
    # Exemplo de uso
    arquivo = "Redação.pdf"
    comandos = ["Não utilize metáforas", "Substitua metáforas por frases mais concretas", "Resuma textos grandes", "Simplifique a linguagem", "Não deixe nada subtendido"]

    exercicios = processar_documento(arquivo)
    exercicios_adaptados = adaptar_exercicios(exercicios, comandos)

    # for exercicio in exercicios_adaptados:
    #     print(exercicio)
    
    criar_arquivo_texto(exercicios_adaptados)

else:
    print('Você escolheu sair')