# from mysql.connector import Error
import pandas as pd
import numpy as np
from tensorflow.keras.preprocessing.text import Tokenizer
import re
# from databases import mysql
from databases import connect_with_connector
from numpy.linalg import norm
import pymysql
from sqlalchemy import text

err = ''


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
def mhe_vector(tokenized, unique_token, token_to_indeks):
    mhs = []
    for sequence in tokenized:
        multiple_hot_vector = np.zeros(len(unique_token))
        for token in sequence:
            multiple_hot_vector[token_to_indeks[token]] = 1
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


def input_to_dataframe(lis, df_data, col_location, col_name):
    new_column_list = lis
    # Add the new column to the DataFrame
    df_data.insert(col_location, col_name, new_column_list)
    return df_data


try:
    # Koneksi ke Database
    data = connect_with_connector()

    # Mengambil data dari tabel
    with data.connect() as connect:
        connect.execute(text('SELECT * FROM competitions'))
        result = connect.fetchall()
        connect.commit()
        lomba_df = result.mappings().all()
        # lomba_df = [dict((connect.description[i][0], value) for i, value in enumerate(row)) for row in ]

        connect.execute(text('SELECT * FROM users'))
        result = connect.fetchall()
        connect.commit()
        user_df = result.mappings().all()
        # user_df = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]

    # Meng-convert data menjadi np.array
    lomba_df = np.array(lomba_df)
    user_df = np.array(user_df)

    # Mengekstrak data yang dibutuhkan
    categories = extract_data(lomba_df, 'category')
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
    word_index = tokenizer.word_index
    word_index = list(word_index.keys())

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
    prize = extract_data(lomba_df, 'reward')
    # Memasukkan data number yang telah di-clean
    prize = [extract_numbers(item) for item in prize]
    # Cleansing data prize
    cleaned_prize = clean_data(prize)

    # Mengambil data prize_pool
    regis_price = extract_data(lomba_df, 'pricePerItem')
    # Apply the function to each item in the list
    regis_price = [extract_numbers(item) for item in regis_price]
    # Flatten the list of lists and remove empty strings within inner lists
    cleaned_regis_price = clean_data(regis_price)

    # Membuat variabel untuk data lomba bersih
    lomba_df_bersih = multiple_hot_encoded.tolist()
    # Mengubah data MHE Lomba menjadi Dataframe
    lomba_df_bersih = pd.DataFrame(lomba_df_bersih, columns=word_index)
    # Memasukkan ID lomba ke dalam DataFrame
    lomba_df_bersih = input_to_dataframe(extract_data(lomba_df, 'id'), lomba_df_bersih, 0, 'id')

    # normalisasi prize_pool supaya range-nya dari 0 ke 0.5
    prize_array = np.array(cleaned_prize)
    # Normalize the data using Min-Max scaling
    normalized_prize = ((prize_array - np.min(prize_array)) / (np.max(prize_array) - np.min(prize_array))) / 2
    # Memasukkan Normalized_Prize ke DataFrame
    lomba_df_bersih = input_to_dataframe(normalized_prize, lomba_df_bersih, lomba_df_bersih.shape[1], 'prize')

    # normalisasi prize_pool supaya range-nya dari 0 ke 0.5
    regis_price_array = np.array(cleaned_regis_price)
    # Normalize the data using Min-Max scaling
    normalized_regis_price = ((regis_price_array - np.min(regis_price_array)) / (
                np.max(regis_price_array) - np.min(regis_price_array))) / 2
    # Memasukkan normalized_regis_price ke DataFrame
    lomba_df_bersih = input_to_dataframe(normalized_regis_price, lomba_df_bersih, lomba_df_bersih.shape[1],
                                         'pricePerItem')

    # Membuat variabel untuk data user bersih
    user_df_bersih = user_mhe.tolist()
    # Mengubah data MHE User menjadi Dataframe
    user_df_bersih = pd.DataFrame(user_df_bersih, columns=word_index)
    # Memasukkan ID user ke dalam DataFrame
    user_df_bersih = input_to_dataframe(extract_data(user_df, 'id'), user_df_bersih, 0, 'id')
    # Memasukkan PrioritizePrize ke DataFrame
    user_df_bersih = input_to_dataframe(extract_data(user_df, 'isPrioritizePrize'), user_df_bersih,
                                        user_df_bersih.shape[1], 'isPrioritizePrize')
    # Memasukkan ConsiderRegisPrice ke DataFrame
    user_df_bersih = input_to_dataframe(extract_data(user_df, 'isConsiderRegisPrice'), user_df_bersih,
                                        user_df_bersih.shape[1], 'isConsiderRegisPrice')

    # Perubahan data bersih tadi dalam bentuk vektor
    com_train = lomba_df_bersih.values
    user_com_train = user_df_bersih.values
    lomba_id = extract_data(lomba_df, 'id')
    lomba_title = extract_data(lomba_df, 'title')

except (ValueError, pymysql.MySQLError) as e:
    if ValueError:
        err = "Database kosong, " + str(e)
    elif pymysql.MySQLError:
        err = "Database Bermasalah, " + str(e)


def vector_rec(user_id, error=err):
    if err == "":
        try:
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
            data.close()
            return full_rec_data
        except NameError:
            error = "User ID " + str(user_id) + " tidak dapat ditemukan"
            data.close()
            return error
    else:
        error = 'Masalah pada database : ' + str(error)
        data.close()
        return error
