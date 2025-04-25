import pandas as pd
import requests

people = pd.read_csv('wikidata/people.csv')
characters = pd.read_csv('wikidata/characters.csv')

n = 1000
ratio = 0.5

people = people.sample(n=round(n*ratio))
characters = characters.sample(n=round(n*(1-ratio)))

def fetch_wikidata_info(entity_id):
    """
    Given a Wikidata entity ID (like 'Q12400'), fetch the English label, description, and Wikipedia URL.
    """
    print(entity_id)
    url = f"https://www.wikidata.org/wiki/Special:EntityData/{entity_id}.json"
    response = requests.get(url)

    if response.status_code != 200:
        return {'label': None, 'description': None, 'wikipedia_url': None}

    data = response.json()
    entity = data['entities'][entity_id]

    # Label and description
    label = entity.get('labels', {}).get('en', {}).get('value', None)
    description = entity.get('descriptions', {}).get('en', {}).get('value', None)

    # English Wikipedia sitelink
    wikipedia_url = None
    sitelinks = entity.get('sitelinks', {})
    if 'enwiki' in sitelinks:
        wikipedia_url = sitelinks['enwiki']['url']

    return {
        'label': label,
        'description': description,
        'wikipedia_url': wikipedia_url
    }

def enrich_characters_dataframe(characters_df):
    """
    Given the characters dataframe, fetch Wikidata info for each person URL.
    """
    # Extract just the Q-id from the URL
    characters_df = characters_df.copy()
    characters_df['entity_id'] = characters_df['person'].apply(lambda x: x.split('/')[-1])

    # Fetch data
    enriched_data = characters_df['entity_id'].apply(fetch_wikidata_info)
    enriched_df = pd.json_normalize(enriched_data)

    characters_df = characters_df.reset_index(drop=True)

    # Merge back
    final_df = pd.concat([characters_df, enriched_df], axis=1)
    return final_df

people_enriched = enrich_characters_dataframe(people)
characters_enriched = enrich_characters_dataframe(characters)

full_list = pd.concat([people_enriched, characters_enriched])
full_list = full_list.sample(frac=1).reset_index(drop=True)

full_list['user'] = 'swimfellow'
full_list['likert_response'] = None

full_list.to_csv('responses.csv')