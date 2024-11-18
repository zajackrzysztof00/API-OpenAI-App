import openai

with open("key.txt",'r',encoding = 'utf-8') as key:
    openai.api_key = key.read()

def read_article(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def generate_html(article_text):
    prompt = (
        "Convert the following article to HTML. "
        "Do not include <html>, <head> or <body> tags"
        "Use appropriate headings (h1, h2, h3), paragraphs (p) and image places. "
        "For images, use the <img src='image_placeholder.jpg'> tag and add an alt attribute with an image description. "
        "Place a short caption in the <figcaption> tag below the image. "
        "Do not use CSS or JS, just plain HTML. "
        "Article content: \n\n" + article_text
    )
    
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",  
        messages=[
            {"role": "system", "content": "You are an assistant that formats articles into structured HTML."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=3000,  
        temperature=0.5
    )
    return response.choices[0].message.content.strip()

def save_html(file_path, html_content):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(html_content)

def main():
    input_file = 'artykul.txt'
    output_file = 'artykul.html'  
    
    article_text = read_article(input_file)
    html_content = generate_html(article_text)
    save_html(output_file, html_content)
    print(f"Wygenerowany kod HTML zapisano w pliku {output_file}.")

if __name__ == "__main__":
    main()
