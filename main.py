import os
import re

import pandas as pd
import fitz  # PyMuPDF for handling and highlighting PDFs
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads'  # Directory to store uploaded PDFs
app.config['HIGHLIGHTED_FOLDER'] = 'highlighted'  # Directory to store modified PDFs with highlights

ALLOWED_EXTENSIONS = {'pdf'}  # Only allow PDF files

# Define a color map for the categories
CATEGORY_COLORS = {
    "Lesser Evil": (0 / 255, 102 / 255, 255 / 255),  # Blue
    "Lack of Accuracy": (255 / 255, 87 / 255, 34 / 255),  # Orange
    "Lack of Transmission into Real Product Features": (153 / 255, 102 / 255, 255 / 255),  # Purple
    "Lack of Evidence in Communicating Marketing Activities": (255 / 255, 99 / 255, 132 / 255),  # Red
    "Hidden Alternative Costs": (128 / 255, 128 / 255, 128 / 255)  # Grey
}
# Function to check if the file has a valid extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to highlight text in the PDF
def highlight_pdf(pdf_path, output_path, highlights, min_word_match=3, ngram_size=2):
    """Highlights specified text in the PDF if a minimum number of words match and uses n-grams for more refined matching."""
    doc = fitz.open(pdf_path)
    highlighted = False  # Keep track of whether any highlights were made

    # Loop through each page
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)

        # Get the full text of the page to find sentences
        full_text = page.get_text("text")
        
        # Loop through each highlight text and search on all pages
        for highlight in highlights:
            highlight_text = highlight["text"]
            category = highlight["category"]
            
            # Tokenize the search text into words
            search_words = re.findall(r'\b\w+\b', highlight_text.lower())

            # Generate n-grams from the search text (to find more precise matches)
            search_ngrams = set(zip(*[search_words[i:] for i in range(ngram_size)]))

            # Split the page text into sentences
            sentences = re.split(r'(?<=[.!?])\s+', full_text)
            
            for sentence in sentences:
                # Tokenize the sentence into words
                sentence_words = re.findall(r'\b\w+\b', sentence.lower())
                
                # Generate n-grams from the sentence
                sentence_ngrams = set(zip(*[sentence_words[i:] for i in range(ngram_size)]))

                # Check how many n-grams match between the search text and the sentence
                match_count = len(search_ngrams & sentence_ngrams)
                
                # Highlight only if enough n-grams match and the sentence length is reasonable
                if match_count >= min_word_match and len(sentence_words) < 50:
                    # Search for this sentence in the PDF page and highlight it
                    highlight_instances = page.search_for(sentence.strip())
                    if highlight_instances:
                        for inst in highlight_instances:
                            # Add highlight and set its color based on the category
                            highlight = page.add_highlight_annot(inst)
                            highlight.set_colors(stroke=CATEGORY_COLORS[category])  # Set highlight color
                            highlight.update()
                            highlighted = True
                    else:
                        print(f"Sentence '{sentence}' not found on page {page_num}")

    if not highlighted:
        print("No highlights were applied to the PDF.")

    # Save the modified PDF
    doc.save(output_path)

def load_highlights_from_csv(file_path: str):
    # Read the CSV file
    df = pd.read_csv(file_path, sep=',')
    df.dropna()
    
    # Convert the DataFrame into a list of dictionaries with 'text' and 'category' keys
    highlights = []
    for index, row in df.iterrows():
        highlight = {
            "text": row['report_chunk'],  # Get the text and strip any extra spaces
            "category": row['category']  # Get the category
        }
        highlights.append(highlight)
        # print(highlight)
    
    return highlights

# Function to handle file uploads and save them
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if 'file' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            try:
                filename = file.filename
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)

                # Test highlights with categories
                csv_file_path = './data/sample_labels/greenwashing_analysis.csv'  # Path to your labeled CSV file
                highlights = load_highlights_from_csv(csv_file_path)
                # print(highlights)


                # highlights = [
                #     {"text": "Covering fiscal year 2020 Environmental  Progress  Report", "category": "Lack of Evidence in Communicating Marketing Activities"},
                #     {"text": "While we helped bring more than 4 gigawatts of renewable energy online", "category": "Lack of Evidence in Communicating Marketing Activities"},
                #     {"text": "Materials     Water stewardship     Zero waste to landfill", "category": "Lack of Evidence in Communicating Marketing Activities"},
                #     {"text": "This commitment acknowledges our responsibility for our entire value chain", "category": "Lack of Evidence in Communicating Marketing Activities"},
                #     # {"text": "Achieve carbon neutrality for our entire carbon footprint by 2030", "category": "Lesser Evil"}
                # ]


                # The path to save the highlighted PDF
                highlighted_filepath = os.path.join(app.config['HIGHLIGHTED_FOLDER'], f"highlighted_{filename}")

                # Highlight the PDF without specifying pages
                highlight_pdf(filepath, highlighted_filepath, highlights)

                # Simulating LLM response: Greenwashing score
                score = 85  # Placeholder score for testing

                # Send success flash message
                flash('File successfully uploaded and processed!', 'success')

                # Send the filename of the highlighted PDF to the template
                return render_template('index.html', score=score, highlighted_filename=f"highlighted_{filename}")
            
            except Exception as e:
                flash(f'An error occurred while processing the file: {e}', 'error')
                return redirect(request.url)
        else:
            flash('Invalid file type. Please upload a PDF.', 'error')
            return redirect(request.url)

    return render_template('index.html')

# Route for serving the highlighted PDF file
@app.route('/highlighted/<filename>')
def highlighted_file(filename):
    return send_from_directory(app.config['HIGHLIGHTED_FOLDER'], filename)

# Create the uploads and highlighted directories if they don't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

if not os.path.exists(app.config['HIGHLIGHTED_FOLDER']):
    os.makedirs(app.config['HIGHLIGHTED_FOLDER'])

if __name__ == "__main__":
    app.run(debug=True)