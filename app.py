import os
import shutil
import subprocess
from flask import Flask, request, send_file, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    num_pages = int(request.form['numPages'])
    images_dir = 'images/'
    os.makedirs(images_dir, exist_ok=True)
    logo_path='logo.jpg'

    # Save the uploaded images
    image_paths = []
    for page in range(num_pages):
        assembly = request.form['assembly{}'.format(page)]
        part = request.form['part{}'.format(page)]
        id = request.form['id{}'.format(page)]
        drawing = request.files.get(f'drawing{page}')
        main = request.files.get(f'main{page}')
        step_a = request.files.get(f'step_a{page}')
        step_b = request.files.get(f'step_b{page}')
        step_c = request.files.get(f'step_c{page}')
        if drawing and main and step_a and step_b and step_c:
            drawing_path = os.path.join(images_dir, f'drawing_{page}.png')
            main_path = os.path.join(images_dir, f'main_{page}.png')
            step_a_path = os.path.join(images_dir, f'step_a_{page}.png')
            step_b_path = os.path.join(images_dir, f'step_b_{page}.png')
            step_c_path = os.path.join(images_dir, f'step_c_{page}.png')
            drawing.save(drawing_path)
            main.save(main_path)
            step_a.save(step_a_path)
            step_b.save(step_b_path)
            step_c.save(step_c_path)
            image_paths.append((drawing_path, main_path,step_a_path,step_b_path,step_c_path,assembly,part,id))

    # Generate the LaTeX code
    latex_code = r'''\documentclass{article}
\usepackage{graphicx}
\usepackage{fancyhdr}
\usepackage{hyperref}
\usepackage{tabularx}
\usepackage[export]{adjustbox}
\usepackage{tikz}
\usepackage[top=1.56in, left=0.3in, right=0.3in, bottom=0.8in,headsep=1in]{geometry}
\usepackage{caption}
\usepackage[skip=1ex, belowskip=2ex]{subcaption}
\usepackage{titlesec}

\def\Arrow{\raisebox{6\height}{\scalebox{3}{$\rightarrow$}}}

\begin{document}
\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0pt}
\fancyhead[L]{\large
    \begin{tabular}{l l}
        \textbf{Car Number:} & 21                                    \\
        \textbf{University:} & Indian Institute of Technology Bombay \\
        \textbf{Team Name:}  & IIT Bombay Racing                     \\
    \end{tabular}}
\fancyhead[R]{
    \vspace{-1.2cm}
    \includegraphics[scale=0.4]{{''' + logo_path + r'''}}}
\fancyfoot[L]{{\Large \textbf{Supporting Material}}}
\fancyfoot[R]{{\Large \textbf{\thepage}}}
\renewcommand{\footrulewidth}{0pt}

\tableofcontents
\vspace{2cm}
\textbf{All dimensions are in mm}
\vspace{2cm}
\newpage
    '''

    for image_path in image_paths:
        step_a_path=image_path[2]
        step_b_path=image_path[3]
        step_c_path=image_path[4]
        main_path=image_path[1]
        drawing_path=image_path[0]
        assembly=image_path[5]
        part=image_path[6]
        id=image_path[7]
        latex_code += r'''
        \section{{'''+assembly+r'''}}
        \begin{center}
            \begin{tabular}{p{0.4\textwidth} p{0.4\textwidth} p{0.4\textwidth}}
                {\large
                \textbf{Assembly:} {'''+assembly+r'''}} & {\large \textbf{Part:} {''' + part + r'''}} & {\large \textbf{Part ID:} {''' + id + r'''}} \\
            \end{tabular}
        \end{center}
        \begin{figure}[!ht]
            \centering
            \begin{subfigure}{5.13in}
                \framebox(5.13in,4.1in){
                \includegraphics[width=5in,height=4in,valign=m]{{''' + drawing_path + r'''}}}
            \end{subfigure}
            \begin{subfigure}{2.5in}
                \framebox(2.5in,4.1in){
                \includegraphics[width=2.4in,height=2.4in,valign=m]{{''' + main_path + r'''}}}
            \end{subfigure}
        \end{figure}

        \vspace{-0.3in}

        \begin{figure}[!ht]
            \centering
            \begin{subfigure}{2.25in}
                \framebox(2.25in,2.25in){
                \includegraphics[width=2.2in,height=2.2in,valign=m]{{''' + step_a_path + r'''}}}
            \end{subfigure}
            \Arrow
            \begin{subfigure}{2.25in}
            \framebox(2.25in,2.25in){
                \includegraphics[width=2.2in,height=2.2in,valign=m]{{''' + step_b_path + r'''}}}
            \end{subfigure}
            \Arrow
            \begin{subfigure}{2.25in}
                \framebox(2.25in,2.25in){
                \includegraphics[width=2.2in,height=2.2in,valign=m]{{''' + step_c_path + r'''}}}
            \end{subfigure}
        \end{figure}
        \newpage
        '''

    latex_code += r'''\end{document}'''

    # Write the LaTeX code to a .tex file
    tex_file = 'document.tex'
    with open(tex_file, 'w') as file:
        file.write(latex_code)

    # Compile the LaTeX document using pdflatex command
    subprocess.run(['latexmk','-pdf', tex_file])
    subprocess.run(['latexmk','-pdf', tex_file])
    #subprocess.run(['pdflatex', tex_file])

    # Move the generated PDF to the current directory
    pdf_file = 'output.pdf'
    shutil.move('document.pdf', pdf_file)

    # Remove the intermediate files generated during compilation
    for file in ['document.tex', 'document.log', 'document.aux', 'document.out','document.toc']:
        os.remove(file)

    # Remove the intermediate image files
    for image_path in image_paths:
        os.remove(image_path[0])
        os.remove(image_path[1])
        os.remove(image_path[2])
        os.remove(image_path[3])
        os.remove(image_path[4])

    # Return the generated PDF file for download
    return send_file(pdf_file, as_attachment=True)

if __name__ == '__main__':
    app.run()
