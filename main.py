from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
from googletrans import Translator
import asyncio
def scrape_article_content(url):
    """Scrape full article content from a given URL"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Different websites structure content differently
        if 'yahoo.com' in url:
            article_body = soup.select('div.caas-body')
            if article_body:
                paragraphs = article_body[0].find_all('p')
                content = ' '.join([p.text for p in paragraphs])
                return content
        elif 'guardian' in url:
            article_body = soup.select('div.article-body-content')
            if article_body:
                paragraphs = article_body[0].find_all('p')
                content = ' '.join([p.text for p in paragraphs])
                return content
        else:
            article_body = soup.find('article')
            if article_body:
                paragraphs = article_body.find_all('p')
                content = ' '.join([p.text for p in paragraphs])
                return content

            paragraphs = soup.find_all('p')
            content = ' '.join([p.text for p in paragraphs])
            return content

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def process_article_batch(article_list, competition_name):
    """Process a batch of articles and store in database"""
    results = []
    for article in article_list:
        time.sleep(1)  # Delay to avoid overloading servers
        url = article.get('url')
        if not url:
            continue

        content = scrape_article_content(url)
        if content:
            full_article = {
                'source': article.get('source'),
                'author': article.get('author'),
                'title': article.get('title'),
                'description': article.get('description'),
                'url': url,
                'urlToImage': article.get('urlToImage'),
                'publishedAt': article.get('publishedAt'),
                'content': content,
                'retrieved_at': datetime.now().isoformat(),
            }
            results.append(full_article)
    return results

competitions = {
    2001: {'name': 'UEFA Champions League'},
    2002: {'name': 'Bundesliga'},
    2015: {'name': 'Ligue 1'},
    2014: {'name': 'La Liga'},
    2019: {'name': 'Serie A'},
    2021: {'name': 'Premier League'},
}

app = Flask(__name__)

@app.route('/api/scrape-articles/<int:id>', methods=['GET'])
def scrape_articles(id):
    competition = competitions.get(id)
    if not competition:
        return jsonify({"error": "Competition not found."}), 404

    competition_name = competition['name']
    articles = requests.get('https://newsapi.org/v2/everything', params={
        'q': competition_name,
        'apiKey': '36d9028b015549a6a0baa43b932bc06e',
        'language': 'en',
        'pageSize': 3,
        'sortBy': 'publishedAt',
    }).json().get('articles', [])

    results = process_article_batch(articles, competition_name)
    return jsonify({"competition_id": id, "competition_name": competition_name, "results": results})
translator = Translator()

@app.route('/translate', methods=['POST'])
def translate_text():
    if request.is_json:
        data = request.get_json()
        text = data.get('text', '')
    else:
        text = request.form.get('text', '')

    if not text:
        return jsonify({'error': 'Missing text input'}), 400

    try:
        result = asyncio.run(translator.translate(text, src='en', dest='vi'))
        return jsonify({
            'input_text': text,
            'translated_text': result.text
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
