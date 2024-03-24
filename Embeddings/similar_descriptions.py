from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim
import pandas as pd
import numpy as np
import json


# Constraints
data_path = r"dataset\awarded_books_with_availability.json"
model = SentenceTransformer("distiluse-base-multilingual-cased-v1")


if __name__ == '__main__':
    df = pd.read_json(data_path, lines=True, orient='records')
    df = df.fillna('')
    book_titles = df['Title'].values.tolist()
    book_mappings = dict(enumerate(book_titles))
    book_tags = dict(enumerate(df['Genre'].values.tolist()))
    book_descriptions = df['Description'].values.tolist()
    encoded_descriptions = [model.encode(description, convert_to_tensor=True) for description in book_descriptions]

    print('Calculating similarity scores')
    similarity_results = np.zeros((len(encoded_descriptions), len(encoded_descriptions)))
    # Calculate similarity scores
    for i in range(len(encoded_descriptions)):
        for j in range(i + 1, len(encoded_descriptions)):
            similarity_score = cos_sim(encoded_descriptions[i], encoded_descriptions[j])
            similarity_results[i, j] = similarity_score
            similarity_results[j, i] = similarity_score

    results = {}
    for i in range(len(encoded_descriptions)):
        book_results = similarity_results[i]
        book_results = np.argsort(book_results)
        top_5 = book_results[::-1][1:6]
        print(book_mappings[i])
        print([book_mappings[x] for x in top_5])
        results[i] = ','.join([str(x) for x in top_5])

    # save results to file
    with open(r"dataset\similar_books.json", 'w', encoding='utf-8') as f:
        f.write(json.dumps(results, ensure_ascii=False, indent=4))
