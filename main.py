import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLineEdit, QMessageBox, QLabel, QListWidget, QVBoxLayout, QWidget, QHBoxLayout, QFileDialog
from PyQt5.QtCore import Qt, QThread
import openai

try:
    with open("key.txt", 'r', encoding='utf-8') as key:
        openai.api_key = key.read().strip()
except FileNotFoundError:
    QMessageBox.critical(None, "Error", "API key file not found!")
    sys.exit(1)

class Article_Generator(QThread):
    def __init__(self, prompt_list, input_file, output_file):
        super().__init__()
        self.prompt_list = prompt_list
        self.input_file = input_file
        self.output_file = output_file

    def read_article(self,file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    def generate_html(self,article_text):
        prompt = (
            "Convert the following article to HTML. "
            "Do not include <html>, <head> or <body> tags"
            "Use appropriate headings (h1, h2, h3), paragraphs (p) and image places. "
            "For images, use the <img src='image_placeholder.jpg'> tag and add an alt attribute with an image description. "
            "Place a short caption in the <figcaption> tag below the image. "
            "Do not use CSS or JS, just plain HTML. "
        )

        for i in range(self.prompt_list.count()):
            item = self.prompt_list.item(i)
            text = item.text()
            prompt += text+". "
        
        prompt += "Article content: \n\n" + article_text

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

    def save_html(self,file_path, html_content):
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(html_content)

    def run(self):
        article_text = self.read_article(self.input_file)
        html_content = self.generate_html(article_text)
        self.save_html(self.output_file, html_content)

class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.input_file = 'artykul.txt'
        self.output_file = 'artykul.html'  

        # Set the main window properties
        self.setWindowTitle('AI Open API App')
        self.setGeometry(100, 100, 900, 600)

        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Add a label
        self.label = QLabel('Enter your prompt:', self)
        layout.addWidget(self.label)

        # Add a line edit (text input)
        self.text_input = QLineEdit(self)
        layout.addWidget(self.text_input)

        # Add a horizontal layout for buttons
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

        # Add a submit button
        self.submit_button = QPushButton('Submit', self)
        button_layout.addWidget(self.submit_button)
        self.submit_button.clicked.connect(self.add_prompt)
        self.submit_button.setCursor(Qt.PointingHandCursor)

        # Add a delete button
        self.delete_button = QPushButton('Delete Selected Prompt', self)
        button_layout.addWidget(self.delete_button)
        self.delete_button.clicked.connect(self.delete_selected_prompt)
        self.delete_button.setCursor(Qt.PointingHandCursor)

        # Add a clear all button
        self.clear_all_button = QPushButton('Clear All Prompts', self)
        button_layout.addWidget(self.clear_all_button)
        self.clear_all_button.clicked.connect(self.clear_all_prompts)
        self.clear_all_button.setCursor(Qt.PointingHandCursor)

        self.prompt_list = QListWidget(self)
        layout.addWidget(self.prompt_list)

        # Add article content button
        self.add_article_content_button = QPushButton('Article content', self)
        layout.addWidget(self.add_article_content_button)
        self.add_article_content_button.clicked.connect(self.select_article_path)

        # Add make article button
        self.make_article_button = QPushButton('Make Article HTML', self)
        layout.addWidget(self.make_article_button)
        self.make_article_button.clicked.connect(self.make_article)

        # Apply CSS style to the app
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
                font-family: Arial, sans-serif;
            }
            QLabel {
                font-size: 16px;
                margin-bottom: 5px;
                color: #333;
            }
            QLineEdit {
                padding: 5px;
                font-size: 14px;
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: #fff;
            }
            QPushButton {
                padding: 10px;
                font-size: 14px;
                color: white;
                background-color: #007bff;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:disabled {
                background-color: #C0C0C0;
            }               
            QPushButton:pressed {
                background-color: #003f7f;
            }
            QListWidget {
                font-size: 14px;
                background-color: #fff;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 10px;
            }
            QListWidget::item {
                padding: 5px;
                border-radius: 3px;
            }
            QListWidget::item:selected {
                background-color: #007bff;
                color: white;
            }
        """)

    def add_prompt(self):
        # Get the text from the input field
        prompt_text = self.text_input.text()

        # Validate and add the prompt to the list widget
        if prompt_text.strip():
            self.prompt_list.addItem(prompt_text)
            self.text_input.clear()
        else:
            QMessageBox.warning(self, 'Warning', 'Please enter a prompt!')

    def delete_selected_prompt(self):
        # Get the selected item
        selected_items = self.prompt_list.selectedItems()

        # If an item is selected, remove it
        if selected_items:
            for item in selected_items:
                self.prompt_list.takeItem(self.prompt_list.row(item))
        else:
            QMessageBox.warning(self, 'Warning', 'Please select a prompt to delete!')

    def select_article_path(self):
    # Open file dialog and get the selected file path
        file,_= QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;Text Files (*.txt)")
        self.input_file = file
        items = []
        for i in range(self.prompt_list.count()):
            item = self.prompt_list.item(i)
            items.append(item.text())

    def clear_all_prompts(self):
        # Clear all prompts from the list
        self.prompt_list.clear()

    def generation_ended(self):
        QMessageBox.information(self, "Information", "HTML Generation Ended")
        self.submit_button.setEnabled(True)
        self.delete_button.setEnabled(True)
        self.clear_all_button.setEnabled(True)
        self.add_article_content_button.setEnabled(True)
        self.make_article_button.setEnabled(True)

    def make_article(self): 
        self.submit_button.setEnabled(False)
        self.delete_button.setEnabled(False)
        self.clear_all_button.setEnabled(False)
        self.add_article_content_button.setEnabled(False)
        self.make_article_button.setEnabled(False)
        self.generator = Article_Generator(self.prompt_list, self.input_file, self.output_file)
        self.generator.finished.connect(self.generation_ended)
        self.generator.start()
        
def main():
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
