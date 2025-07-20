from jinja2 import Environment, FileSystemLoader
import json

# Load JSON data
with open('../src/new.json', encoding='utf-8') as f:
    newsList = json.load(f)

# Set up Jinja2 environment
env = Environment(loader=FileSystemLoader('./templates'))
template = env.get_template('more.html')

# Render the template with multiple variables
newsHtml = template.render(newsList=newsList)

with open('../news/index.html', 'w', encoding='utf-8') as f:
    f.write(newsHtml)