from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

def scrape_cifra_club(url):
    """
    Scrapes the given Cifra Club URL to extract the song title, artist, and simplified chords and lyrics.
    Removes extra blank lines left by tab removal.
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises an HTTPError for bad responses

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract song title and artist
        title = soup.find('h1', class_='t1').get_text(strip=True)
        artist = soup.find('h2', class_='t3').get_text(strip=True)

        # The main content with chords and lyrics is in a 'pre' tag
        chords_lyrics_html = soup.find('pre')

        # Return early if the main content isn't found
        if not chords_lyrics_html:
            return "Error", "Could not find chord structure on the page.", ""

        # Remove any tablature sections (solos, riffs)
        for tab in chords_lyrics_html.find_all('span', class_='tablatura'):
            tab.decompose() # This removes the element from the tree

        # Get the cleaned HTML content as a string
        simplified_chords_str = chords_lyrics_html.decode_contents()

        # --- NEW: Clean up extra newlines ---
        # This regex finds 3 or more consecutive newlines (with optional whitespace)
        # and replaces them with just two, preserving paragraph breaks but removing large gaps.
        cleaned_chords = re.sub(r'(\n\s*){3,}', '\n\n', simplified_chords_str).strip()

        return title, artist, cleaned_chords

    except requests.exceptions.RequestException as e:
        return "Error", f"Could not fetch the URL: {e}", ""
    except AttributeError:
        return "Error", "Could not find the song information on the page. Please check the URL.", ""

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Handles the main page, including the form submission for the URL.
    """
    if request.method == 'POST':
        url = request.form['url']
        if "cifraclub.com.br" in url:
            title, artist, chords = scrape_cifra_club(url)
            return render_template('index.html', title=title, artist=artist, chords=chords)
        else:
            return render_template('index.html', error="Please enter a valid Cifra Club URL.")
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
