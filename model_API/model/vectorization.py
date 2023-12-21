import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
import re
from databases import mysql
from numpy.linalg import norm


# Function untuk mengambil data dari dictionary
def extract_data(dic, key):
    new_list = []
    for i in range(len(dic)):
        new_list.append(dic[i][key])
    return new_list


# Function untuk lowercasing data dari list
def lowercasing(lis):
    new_list = []
    for i in range(len(lis)):
        new_list.append(lis[i].lower().replace(' ', ''))
    return new_list


# Function untuk melakukan MHV kepada tokenized data
def mhe_vector(tokenized, unique_tokens, token_to_index):
    mhs = []
    for sequence in tokenized:
        multiple_hot_vector = np.zeros(len(unique_tokens))
        for token in sequence:
            multiple_hot_vector[token_to_index[token]] = 1
        mhs.append(multiple_hot_vector)
    return mhs


# Mengambil value nilai dari data string
def extract_numbers(s):
    return [int(''.join(re.findall(r'\d+', num))) if re.findall(r'\d+', num) else '' for num in s.split(',')]


def clean_data(lis):
    cleaned_list = [[0] if not sublist else sublist for sublist in lis]
    cleaned_list = [[item for item in sublist if item != ''] for sublist in cleaned_list]
    cleaned_list = [sublist[0] if sublist else 0 for sublist in cleaned_list]
    return cleaned_list


# Koneksi ke Database
data = mysql()

# Mengambil data dari tabel
with data.cursor() as cursor:
    cursor.execute('SELECT * FROM lomba')
    lomba_df = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]

with data.cursor() as cursor:
    cursor.execute('SELECT * FROM user')
    user_df = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]

# Meng-convert data menjadi np.array
lomba_df = np.array(lomba_df)
user_df = np.array(user_df)

# Mengekstrak data yang dibutuhkan
categories = extract_data(lomba_df, 'category_id')
user_categories = extract_data(user_df, 'interestCategory')

# Lowercase kategori
categories = lowercasing(categories)
user_categories = lowercasing(user_categories)

# Tokenisasi kategori
tokenizer = Tokenizer()
tokenizer.fit_on_texts(categories)
categories_tokenized = tokenizer.texts_to_sequences(categories)
user_categories_tokenized = tokenizer.texts_to_sequences(user_categories)

# Pengecekan Tokenisasi
# word_index = tokenizer.word_index
# print(word_index)

# Mengambil token unik
unique_tokens = list(set(item for sublist in categories_tokenized for item in sublist))
# Indexing token
token_to_index = {token: index for index, token in enumerate(unique_tokens)}

# Memasukkan MHV ke dalam list
multiple_hot_encoded = mhe_vector(categories_tokenized, unique_tokens, token_to_index)
user_mhe = mhe_vector(user_categories_tokenized, unique_tokens, token_to_index)
# Mengubah MHV menjadi np.array
multiple_hot_encoded = np.array(multiple_hot_encoded)
user_mhe = np.array(user_mhe)

# Mengambil data prize_pool
prize = extract_data(lomba_df, 'prize_pool')
# Memasukkan data number yang telah di-clean
prize = [extract_numbers(item) for item in prize]
# Cleansing data prize
cleaned_prize = clean_data(prize)

# Mengambil data prize_pool
regis_price = extract_data(lomba_df, 'regis_price')
# Apply the function to each item in the list
regis_price = [extract_numbers(item) for item in regis_price]
# Flatten the list of lists and remove empty strings within inner lists
cleaned_regis_price = clean_data(regis_price)

# Membuat CSV data lomba bersih
data_csv = multiple_hot_encoded
# Header CSV
header = 'seni, bisnisdankewirausahaan, debat, karyatulis, teknologidaninovasi, olahraga, itdevelopment, olimpiadebahasainggris, programing, fotografi, sains'
# file path
csv_file_path = 'data_lomba_bersih.csv'
# Menyimpan np.array menjadi CSV file dengan header
np.savetxt(csv_file_path, data_csv, delimiter=',', fmt='%1.1f', header=header, comments='')

new_column_list = extract_data(lomba_df, 'id')
# Read the existing CSV file into a DataFrame
df = pd.read_csv(csv_file_path)
# Add the new column to the DataFrame
df.insert(0, 'id', new_column_list)
# Save the modified DataFrame back to the CSV file
df.to_csv(csv_file_path, index=False)

# normalisasi prize_pool supaya range-nya dari 0 ke 0.5
prize_array = np.array(cleaned_prize)
# Normalize the data using Min-Max scaling
normalized_prize = ((prize_array - np.min(prize_array)) / (np.max(prize_array) - np.min(prize_array))) / 2
new_column_list = normalized_prize
# Read the existing CSV file into a DataFrame
df = pd.read_csv(csv_file_path)
# Add the new column to the DataFrame
df.insert(df.shape[1], 'prize', new_column_list)
# Save the modified DataFrame back to the CSV file
df.to_csv(csv_file_path, index=False)

# normalisasi prize_pool supaya range-nya dari 0 ke 0.5
regis_price_array = np.array(cleaned_regis_price)
# Normalize the data using Min-Max scaling
normalized_regis_price = ((regis_price_array - np.min(regis_price_array)) / (
        np.max(regis_price_array) - np.min(regis_price_array))) / 2
new_column_list = normalized_regis_price
# Read the existing CSV file into a DataFrame
df = pd.read_csv(csv_file_path)
# Add the new column to the DataFrame
df.insert(df.shape[1], 'regis_price', new_column_list)
# Save the modified DataFrame back to the CSV file
df.to_csv(csv_file_path, index=False)

# Membuat CSV data user bersih
data_csv = user_mhe
# file path
updated_user_csv_file_path = 'data_user_bersih.csv'
# Menyimpan np.array menjadi CSV file dengan header
np.savetxt(updated_user_csv_file_path, data_csv, delimiter=',', fmt='%1.1f', header=header, comments='')

new_column_list = extract_data(user_df, 'id')
# Read the existing CSV file into a DataFrame
df = pd.read_csv(updated_user_csv_file_path)
# Add the new column to the DataFrame
df.insert(0, 'id', new_column_list)
# Save the modified DataFrame back to the CSV file
df.to_csv(updated_user_csv_file_path, index=False)

new_column_list = extract_data(user_df, 'PrioritizePrize')
# Read the existing CSV file into a DataFrame
df = pd.read_csv(updated_user_csv_file_path)
# Add the new column to the DataFrame
df.insert(df.shape[1], 'isPrioritizePrize', new_column_list)
# Save the modified DataFrame back to the CSV file
df.to_csv(updated_user_csv_file_path, index=False)

new_column_list = extract_data(user_df, 'ConsiderRegisPrice')
# Read the existing CSV file into a DataFrame
df = pd.read_csv(updated_user_csv_file_path)
# Add the new column to the DataFrame
df.insert(df.shape[1], 'isConsiderRegisPrice', new_column_list)
# Save the modified DataFrame back to the CSV file
df.to_csv(updated_user_csv_file_path, index=False)

# Perubahan data bersih tadi dalam bentuk vektor
data_bersih = pd.read_csv(csv_file_path)
com_train = data_bersih.values
user_data_bersih = pd.read_csv(updated_user_csv_file_path)
user_com_train = user_data_bersih.values
lomba_id = extract_data(lomba_df, 'id')
lomba_title = extract_data(lomba_df, 'title')


def vector_rec(user_id):
    data_dict = {lomba_id[i]: [lomba_title[i]] for i in range(len(lomba_id))}
    for index in range(len(user_com_train)):
        if user_com_train[index, 0:1] == user_id:
            vector_user = user_com_train[index][1:]
    for vector_com in com_train:
        cosine_similarity = np.dot(vector_user, vector_com[1:]) / (norm(vector_user) * norm(vector_com[1:]))
        data_dict[int(vector_com[0])].append(round(cosine_similarity, 2))

    sorted_dict = sorted(data_dict.items(), key=lambda x: x[1][-1], reverse=True)

    full_rec_data = {"status": "success", "data": []}
    iterate = 0
    for key, value in sorted_dict:
        if value[1] >= 0.5:
            for i in range(len(lomba_df)):
                if np.isin(lomba_df[i]['id'], key):
                    full_rec_data["data"].append(lomba_df[i])
                    full_rec_data["data"][iterate].update({"recommendation": value[1]})
            iterate += 1
        else:
            break

    return full_rec_data
