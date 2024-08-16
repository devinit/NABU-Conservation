from datasets import Dataset, load_dataset
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import nltk
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
import pandas as pd


def remove_string_special_characters(s):
    # removes special characters with ' '
    stripped = re.sub(r'[^\w\s]', ' ', s)

    # Change any white space to one space
    stripped = re.sub('\s+', ' ', stripped)

    # Remove start and end white spaces
    stripped = stripped.strip()
    if stripped != '':
        return stripped.lower()

def remove_stop_words(s):
    stop_words = set(stopwords.words('english')) | set(stopwords.words('spanish')) | set(stopwords.words('french')) | set(stopwords.words('german'))
    try:
        return ' '.join([word for word in nltk.word_tokenize(s) if word not in stop_words])
    except TypeError:
        return ' '


def features(vectorizer, result):
    feature_array = np.array(vectorizer.get_feature_names_out())
    flat_values = result.toarray().flatten()
    zero_indices = np.where(flat_values == 0)[0]
    tfidf_sorting = np.argsort(flat_values)[::-1]
    masked_tfidf_sorting = np.delete(tfidf_sorting, zero_indices, axis=0)

    return feature_array[masked_tfidf_sorting].tolist()


def clean_text(example):
    text = "{} {} {}".format(example['project_title'], example['short_description'], example['long_description'])
    example['text'] = remove_stop_words(remove_string_special_characters(text))
    return example


dataset = pd.read_csv("large_input/crs_au.csv")
dataset = dataset[['project_title','short_description', 'long_description', 'purpose_code']]
dataset = Dataset.from_pandas(dataset, preserve_index=False)
dataset = dataset.map(clean_text, num_proc=8, remove_columns=['project_title', 'short_description', 'long_description'])
dataset = dataset.filter(lambda example: example["text"] != "" and example["text"] is not None)

# De-duplicate
df = pd.DataFrame(dataset)
print(df.shape)
df = df.drop_duplicates(subset=['text'])
print(df.shape)
dataset = Dataset.from_pandas(df, preserve_index=False)

not_conservation = dataset.filter(lambda example: example['purpose_code'] not in [41010, 41020, 41030, 41040])
conservation = dataset.filter(lambda example: example['purpose_code'] in [41010, 41020, 41030, 41040])

vectorizer = TfidfVectorizer(ngram_range=(1, 1))
vectorizer.fit(dataset['text'])

not_conservation_result = vectorizer.transform([" ".join(not_conservation['text'])])
top_not_conservation = features(vectorizer, not_conservation_result)
top_not_conservation = top_not_conservation[:250]

conservation_result = vectorizer.transform([" ".join(conservation['text'])])
top_conservation = features(vectorizer, conservation_result)
top_conservation = [word for word in top_conservation if word not in top_not_conservation]
top_conservation = top_conservation[:250]


print("Not conservation:\n")
print(top_not_conservation)

print("Conservation:\n")
print(top_conservation)