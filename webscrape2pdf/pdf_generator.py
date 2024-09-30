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
            @page {
                size: letter;
                margin: 2cm;
            }
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
            h2 {
                font-size: 16px;
                color: #444;
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
        
        # Remove all image tags
        for img in soup.find_all('img'):
            img.decompose()
        
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
        
        # Remove any remaining problematic characters or patterns
        cleaned_html = re.sub(r'[^\x00-\x7F]+', ' ', cleaned_html)
        
        html_content += f"<h1>URL: {url}</h1>{cleaned_html}<hr>"
    
    html_content += "</body></html>"
    
    result_file = io.BytesIO()
    
    try:
        pdf = pisa.pisaDocument(io.BytesIO(html_content.encode("UTF-8")), result_file)
        
        if not pdf.err:
            with open(output_file, 'wb') as f:
                f.write(result_file.getvalue())
            print(f"PDF created successfully: {output_file}")
        else:
            print(f"Error creating PDF: {pdf.err}")
    except Exception as e:
        print(f"An error occurred while creating the PDF: {str(e)}")