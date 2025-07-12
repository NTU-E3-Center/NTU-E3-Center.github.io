from serpapi import GoogleSearch
import pandas as pd
import json
import requests

# Get your API key at https://serpapi.com/dashboard
# addd
api_key = "9564b246509b8b5c0be41828e72e1793ddd3dafb1a6c3ba9a4c41114fb0b2c5d"

# Define the output file path
output_path = '../src/pub.json'

# Define the columns you want to get
cols = ['citationId', 'title', 'link', 'publication_date', 'journal', 'volume']

# Parameter defines the ID of an author. You can find the ID either by using our Google Scholar Profiles API or by going to the Google Scholar user profile page and getting it from there (e.g., https://scholar.google.com/citations?user={author_id}).
# author_id for Lisa
author_id = "tUbPb-QAAAAJ"

# open json
def open_json(file_path):
    try:
        # Open the JSON file for reading
        with open(file_path, 'r', encoding='utf-8') as file:
            # Load the JSON data
            data = json.load(file)
    
        return data
    
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' does not exist.")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Function to convert a title to title case
def title_case(title):
    # List of words that should not be capitalized unless they are the first or last word
    small_words = {
        'a', 'an', 'and', 'as', 'at', 'but', 'by', 'for', 
        'in', 'nor', 'of', 'on', 'or', 'so', 'the', 'to', 'up', 'with', 'yet'
    }
    
    # Split the title into words
    words = title.split()
    
    # Function to properly capitalize each word
    def capitalize_word(word, is_first_or_last):
        if word.lower() in small_words and not is_first_or_last:
            return word.lower()
        return word.capitalize()
    
    # Apply the capitalize_word function to each word
    capitalized_words = [
        capitalize_word(word, i == 0 or i == len(words) - 1) 
        for i, word in enumerate(words)
    ]
    
    # Join the words back into a single string
    return ' '.join(capitalized_words)

def get_data_from_crossref(article_title):
    """
    Searches the Crossref API for an article title and returns the DOI.
    """
    try:
        match_author_given_name = "I-Yun"
        url = f"https://api.crossref.org/works?query.bibliographic={article_title}&rows=1"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        matching_item = data['message']['items'][0]
        authors = [author['given'] for author in matching_item['author']]
        matching_author = [author for author in authors if match_author_given_name in author]
        print(authors)
        if matching_author:
            return {'doi': data['message']['items'][0]['DOI'], 'authors': authors}
        return {'doi': None, 'authors': None}
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

# start
params = {
    "engine": "google_scholar_author",
    "author_id": author_id,
    "api_key": api_key,
    "sort": "pubdate"
}
articles = GoogleSearch(params).get_dict()['articles'][:]

# Only check if the newest article has already been added
# It will loop through the articles until it finds one that is already in the list
# So the older articles will not be checked (prevent somewrong old articles to be added)
# If there are older articles that are not in the list, add it manually
old_pub = open_json(f'../src/pub.json')
existing_ids = set(pub['citationId'] for pub in old_pub)
new_articles_to_add = []
for article in articles:
    citation_id = article['citation_id']
    
    # If the article is already in your data list, stop the loop
    if citation_id in existing_ids:
        break
    else:
        # Add the new article to the list
        new_articles_to_add.append(article)

# Get the citation for each new article
df = pd.DataFrame()
for article in new_articles_to_add:
    params = {
        "engine": "google_scholar_author",
        "view_op": "view_citation",
        "citation_id": article['citation_id'],
        "api_key": api_key
    }
    citation = GoogleSearch(params).get_dict()['citation']
    temp = pd.DataFrame(list(citation.items())).set_index(0).T
    temp['citationId'] = article['citation_id']
    df = pd.concat([temp, df])

# format the data
if not df.empty:
    df = df[cols]
    df['title'] = df['title'].apply(title_case)
    df['publication_date'] = pd.to_datetime(df['publication_date'], format='mixed')
    df['year'] = df['publication_date'].dt.strftime('%y')
    print(df['publication_date'].dt)
    df['month'] = df['publication_date'].dt.strftime('%b.')
    df.drop('publication_date', axis=1, inplace=True)
    df.reset_index(drop=True, inplace=True)
    
    for i, row in df.iterrows():
        data = get_data_from_crossref(row['title'])
        if data['doi']:
            df.at[i, 'link'] = f'https://doi.org/{data['doi']}'
            df.at[i, 'authors'] = ', '.join(data['authors'])
        else:
            print(f"DOI not found for article {i+1}: {row['title']}")

# Combine the new articles with the old ones
df = pd.concat([pd.DataFrame(old_pub), df])

# Convert DataFrame to list of dictionaries
records = df.to_dict(orient='records')
cleaned_records = [{key: value for key, value in row.items() if not pd.isna(value)} for row in records]

# Save the updated list to the JSON file
with open(output_path, 'w') as f:
    json.dump(cleaned_records, f, indent=2)

print(f"Added {len(new_articles_to_add)} new articles to the list.")