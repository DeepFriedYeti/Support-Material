import os
import shutil
import subprocess
from flask import Flask, request, send_file, render_template
from pylatex import Document, Section, SubFigure, Command
from pylatex.utils import NoEscape

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    num_pages = int(request.form['numPages'])
    images_dir = 'images/'
    os.makedirs(images_dir, exist_ok=True)

    # Save the uploaded images
    image_paths = []
    for page in range(num_pages):
        drawing = request.files.get(f'drawing{page}')
        main = request.files.get(f'main{page}')
        if drawing and main:
            drawing_path = os.path.join(images_dir, f'drawing_{page}.png')
            main_path = os.path.join(images_dir, f'main_{page}.png')
            drawing.save(drawing_path)
            main.save(main_path)
            image_paths.append((drawing_path, main_path))

    # Save the uploaded images
    # for page in range(num_pages):
    #     image = request.files.get(f'image{page}')
    #     if image:
    #         image_path = f'image_{page}.png'
    #         image.save(image_path)
    #         image_paths.append(image_path)

    # Generate the LaTeX code
    latex_code = r'''\documentclass{article}
    \usepackage{graphicx}
    \usepackage{subcaption}
    
    \begin{document}
    
    '''

    for image_path in image_paths:
        main_path=image_path[1]
        drawing_path=image_path[0]
        latex_code += r'''\section{Page}
        \begin{figure}[!h]
            \centering
            \includegraphics[width=0.5\textwidth]{{''' + drawing_path + r'''}}
            \caption{drawing}
        \end{figure}
        \begin{figure}[!h]
            \centering
            \includegraphics[width=0.5\textwidth]{{''' + main_path + r'''}}
            \caption{main}
        \end{figure}
    
        '''

    latex_code += r'''\end{document}'''

    # Write the LaTeX code to a .tex file
    tex_file = 'document.tex'
    with open(tex_file, 'w') as file:
        file.write(latex_code)

    # Compile the LaTeX document using pdflatex command
    subprocess.run(['pdflatex', tex_file])

    # Move the generated PDF to the current directory
    pdf_file = 'output.pdf'
    shutil.move('document.pdf', pdf_file)

    # Remove the intermediate files generated during compilation
    for file in ['document.tex', 'document.log', 'document.aux']:
        os.remove(file)

    # Remove the intermediate image files
    for image_path in image_paths:
        os.remove(image_path[0])
        os.remove(image_path[1])

    # Return the generated PDF file for download
    return send_file(pdf_file, as_attachment=True)

if __name__ == '__main__':
    app.run()
