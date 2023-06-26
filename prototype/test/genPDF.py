# setupstuff
# sudo apt-get install wkhtmltopdf
# export PATH="$HOME/bin:$PATH"


import pdfkit

with open('./index.html', 'r') as f:
    stuff = f.read()
    pdfkit.from_string(stuff, 'out.pdf')
