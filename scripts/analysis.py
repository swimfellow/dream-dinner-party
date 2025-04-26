import pandas as pd
import requests
from collections import Counter, defaultdict

# Load and clean data
data = pd.read_csv('responses.csv')
data = data[data['likert_response'].notna()]
data['person'] = data['person'].apply(lambda x: x.split('/')[-1])

dream = data[data['likert_response'] < 3][['person', 'likert_response']].copy()
dream.loc[dream['likert_response'] == 2, 'likert_response'] = 0.5
nightmare = data[data['likert_response'] > 3][['person', 'likert_response']].copy()
nightmare['likert_response'] = (nightmare['likert_response'] - 3) / 2

# Helper functions
def fetch_wikidata_info(entity_id):
    url = f"https://www.wikidata.org/wiki/Special:EntityData/{entity_id}.json"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    return response.json()['entities'][entity_id]

def fetch_label(entity_id):
    """Fetch human-readable label for a property or value ID."""
    url = f"https://www.wikidata.org/wiki/Special:EntityData/{entity_id}.json"
    response = requests.get(url)
    if response.status_code != 200:
        return entity_id  # fallback to ID if cannot resolve
    data = response.json()
    entity = data['entities'][entity_id]
    labels = entity.get('labels', {})
    label_en = labels.get('en', {})
    return label_en.get('value', entity_id)  # fallback

def build_smart_sparql_query(property_value_pairs):
    query = """PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX bd: <http://www.bigdata.com/rdf#>

SELECT ?item ?itemLabel (COUNT(?match) AS ?matches) WHERE {
  ?item wdt:P31 wd:Q5.  # Candidate filter (example: humans)
"""
    
    for pair in property_value_pairs:
        prop_id = pair['property_id']
        val_id = pair['value_id']
        query += f"  OPTIONAL {{ ?item wdt:{prop_id} wd:{val_id}. BIND(1 AS ?match) }}\n"
    
    query += """  
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
}
GROUP BY ?item ?itemLabel
ORDER BY DESC(?matches)
"""
    return query



# Main function
def get_common_features(entity_list, output_csv_name='top_property_value_pairs.csv'):
    entities = entity_list['person'].tolist()
    strength = entity_list['likert_response'].tolist()
    strength = [s*2 for s in strength]  # fix typo
    
    property_counter = Counter()
    property_values = defaultdict(list)

    for eid in entities:
        features = fetch_wikidata_info(eid)
        if features and 'claims' in features:
            claims = features['claims']
            for prop_id, claim_list in claims.items():
                property_counter[prop_id] += 1
                for claim in claim_list:
                    mainsnak = claim.get('mainsnak', {})
                    datavalue = mainsnak.get('datavalue', {})
                    if datavalue:
                        property_values[prop_id].append(datavalue)

    printed = 0  # to track how many properties we printed
    results = []

    print("\nTop 10 Most Common Properties (excluding properties with unique top values):")
    for prop_id, count in property_counter.most_common():
        if printed >= 10:
            break

        prop_label = fetch_label(prop_id)

        # Collect and count values
        values = []
        for v in property_values[prop_id]:
            if v['type'] == 'wikibase-entityid':
                values.append(v['value']['id'])
            elif v['type'] == 'string':
                values.append(v['value'])
            elif v['type'] == 'quantity':
                values.append(str(v['value']['amount']))
            elif v['type'] == 'time':
                values.append(v['value']['time'])
            else:
                values.append(str(v['value']))

        value_counter = Counter(values)

        # Check if the top value occurs more than once
        if not value_counter:
            continue
        top_value, top_count = value_counter.most_common(1)[0]
        if top_count <= 1:
            continue  # skip this property
        
        # If good, print it
        print(f"\n{prop_label} ({prop_id}): {count} times")
        for val_id, val_count in value_counter.most_common(5):
            if isinstance(val_id, str) and (val_id.startswith('Q') or val_id.startswith('P')):
                val_label = fetch_label(val_id)
            else:
                val_label = val_id
            print(f"  {val_label} ({val_id}): {val_count} times")

            results.append({
                'property_id': prop_id,
                'property_label': prop_label,
                'value_id': val_id,
                'value_label': val_label,
                'property_count': count,
                'value_count': val_count
            })

        printed += 1

    # Save results to CSV
    df_results = pd.DataFrame(results)
    df_results.to_csv(output_csv_name, index=False)
    print(f"\nSaved top property-value pairs to {output_csv_name}")

    # Build and print SPARQL query
    if results:
        # Just use the first result per property
        first_value_per_property = []
        seen_properties = set()
        for r in results:
            if r['property_id'] not in seen_properties:
                first_value_per_property.append(r)
                seen_properties.add(r['property_id'])
        
        sparql_query = build_smart_sparql_query(first_value_per_property)
        print("\nSuggested SPARQL Query:\n")
        print(sparql_query)

# Run it
get_common_features(dream)
get_common_features(nightmare, output_csv_name='bottom_property_value_pairs.csv')