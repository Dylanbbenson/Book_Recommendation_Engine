import pandas as pd
import requests
from datetime import date, datetime
import numpy as np
from genre_mapping import genre_mapping
current_date = date.today().strftime('%Y-%m-%d')
current_year = date.today().year

def categorize_pages(pages):
    if pages < 150: return "Short"
    elif pages < 300: return "Medium"
    else: return "Long"


def get_genre_from_openlibrary(isbn, author, title):
    # Build the query
    if isbn:
        query = f"{isbn}"
        response = requests.get(f"https://openlibrary.org/search.json?isbn={query}")
    else:
        query = f"{title} {author}"
        response = requests.get(f"https://openlibrary.org/search.json?title={query}")

    if response.status_code == 200:
        data = response.json()
        try:
            # Get the subjects (genres) from the first result
            subjects = data['docs'][0].get('subject', [])
            if subjects:
                # Return the first subject or join multiple as a string
                return ", ".join(subjects[:3])  # Limit to top 3 subjects
            else:
                return "Unknown"
        except (KeyError, IndexError):
            return "Unknown"
    return "Unknown"

# Function to normalize genres
def normalize_genres(genres_str, mapping):
    # Split the string into a list of genres
    genres = [genre.strip() for genre in genres_str.split(",")]
    normalized = set()  # Use a set to avoid duplicates
    for genre in genres:
        if genre in mapping:
            normalized.add(mapping[genre])  # Map to the broader category
        else:
            normalized.add(genre)  # Keep the original genre if not in mapping
    return list(normalized)  # Convert back to a list


def prep_data(df):
    books = df[
        ['Title', 'ISBN', 'Author', 'Additional Authors', 'My Rating', 'Average Rating', 'Publisher', 'Number of Pages',
         'Year Published', 'Original Publication Year', 'Date Read', 'Exclusive Shelf']]
    books = books.rename(columns={'Additional Authors': 'Additional_Authors', 'My Rating': 'My_Rating',
                                  'Average Rating': 'Average_Rating', 'Number of Pages': 'Number_of_Pages',
                                  'Year Published': 'Year_Published',
                                  'Original Publication Year': 'Original_Publication_Year', 'Date Read': 'Date_Read',
                                  'Exclusive Shelf': 'Exclusive_Shelf'})

    # cleanup
    books['My_Rating'].replace(0, np.nan, inplace=True)
    books.dropna(subset=['Title'])
    books[['Title', 'Series_Info']] = books['Title'].str.extract(r'^(.*?)(\s\([^)]*\))?$')
    books['Series_Info'] = books['Series_Info'].fillna('Standalone')
    books = books.drop_duplicates(subset=['Title', 'Author'])
    books['Date_Read'] = pd.to_datetime(books['Date_Read'])
    books['is_series'] = books['Title'].str.contains(r'\(.*#\d+\)', regex=True)
    books['book_age'] = current_year - books['Original_Publication_Year']
    books['ISBN'] = books['ISBN'].str.replace(r"[\"=]", '')
    books['have_read'] = books['Exclusive_Shelf'].replace({
        'to-read': False,
        'read': True
    })

    books['length_category'] = books['Number_of_Pages'].apply(categorize_pages)
    books['Genre'] = books.apply(lambda row: get_genre_from_openlibrary(row['ISBN'], row['Title'], row['Author']), axis=1)

    # Apply the normalization
    books['Normalized_Genres'] = books['Genre'].apply(lambda x: normalize_genres(x, genre_mapping))

    return books

if __name__ == '__main__':
    df = pd.read_csv('./data/goodreads_library_export.csv')
    books = prep_data(df)
    books.to_csv('./data/cleaned_data.csv')
