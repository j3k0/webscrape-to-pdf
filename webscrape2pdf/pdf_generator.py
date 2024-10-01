from bs4 import BeautifulSoup
from xhtml2pdf import pisa
import io
import re
from urllib.parse import urljoin

def create_pdf(content, output_file):
    html_content = """
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {
                font-family: Arial, sans-serif;
                font-size: 12px;
                line-height: 1.6;
            }
            h1 {
                font-size: 18px;
                color: #333;
                margin-top: 20px;
            }
            a {
                color: #0066cc;
                text-decoration: none;
            }
        </style>
    </head>
    <body>
    """
    
    for url, html in content:
        # Parse the HTML content
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove all script tags
        for script in soup.find_all('script'):
            script.decompose()
        
        # Remove all style tags
        for style in soup.find_all('style'):
            style.decompose()
        
        # Convert relative URLs to absolute
        for a in soup.find_all('a', href=True):
            a['href'] = urljoin(url, a['href'])
        
        cleaned_html = str(soup)
        
        html_content += f"<h1>URL: {url}</h1>{cleaned_html}<hr>"
    
    html_content += "</body></html>"
    
    result_file = io.BytesIO()
    
    pdf = pisa.pisaDocument(io.BytesIO(html_content.encode("UTF-8")), result_file)
    
    if not pdf.err:
        with open(output_file, 'wb') as f:
            f.write(result_file.getvalue())
        print(f"PDF created successfully: {output_file}")
    else:
        print(f"Error creating PDF: {pdf.err}")