import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVR
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.pipeline import Pipeline

from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.models import Sequential
from keras.layers import Embedding, LSTM, Dense, Flatten


def homogenizeData(dfDict):
    ###
    # Each portion of the dataset may have its own homogenizing requirements
    # The end result must be a dataframe with columns of:
    # Hotel Name, Hotel Address (Street, City, State/Province, Country), Date of Review, Review Rating, Review Text, and Data Source
    ###

    homogenizedDf = pd.DataFrame(columns=[
        'Hotel Name',
        'Hotel Address',
        'Review Date',
        'Review Rating',
        'Review Text',
        'Data Source'
    ])

    # HOMOGENIZING DATAFINIFI DATASET
    homogenizedDf = pd.concat([homogenizedDf, datafinitiHomogenizeHelper(dfDict['7282_1'])], ignore_index=True)
    print('Datafiniti file 1... COMPLETE')
    homogenizedDf = pd.concat([homogenizedDf, datafinitiHomogenizeHelper(dfDict['Datafiniti_Hotel_Reviews'])], ignore_index=True)
    print('Datafiniti file 2... COMPLETE')
    homogenizedDf = pd.concat([homogenizedDf, datafinitiHomogenizeHelper(dfDict['Datafiniti_Hotel_Reviews_Jun19'])], ignore_index=True)
    print('Datafiniti file 3... COMPLETE')

    # HOMOGENIZING BOOKING.COM DATASET
    homogenizedDf = pd.concat([homogenizedDf, bookingComHomogenizeHelper(dfDict['Hotel_Reviews'])], ignore_index=True)
    print('booking.com file 1... COMPLETE')

    return homogenizedDf

def prefilterData(combinedDf):
    def normalizeReviewScores(x):
        if x['Data Source'] == 'Datafiniti':
            x['Review Rating'] = x['Review Rating'] * 2
        return x
    print(f'Starting entry count... {len(combinedDf.index)}')
    print('(removing entries with empty review text)')
    combinedDf = combinedDf[combinedDf['Review Text'].notnull()]

    print('(removing entries with short review text)')
    combinedDf = combinedDf[combinedDf['Review Text'].apply(len) > 2]

    print('(removing entries with empty review rating)')
    combinedDf = combinedDf.dropna(subset=['Review Rating'])

    print('(normalizing review scores)')
    combinedDf = combinedDf.apply(normalizeReviewScores, result_type='expand', axis=1)

    print(f'Ending entry count... {len(combinedDf.index)}')
    return combinedDf

def bookingComHomogenizeHelper(df):
    def parseReviewText(x):
        reviewText = ''
        if x['Positive_Review'] != 'No Positive':
            reviewText += x['Positive_Review'] + ' '
        if x['Negative_Review'] != 'No Negative':
            reviewText += x['Negative_Review']
        reviewText = reviewText.strip()
        x['Review Text'] = reviewText

        return x

    curDf = df
    curDf = curDf.rename(columns={
        'Hotel_Address': 'Hotel Address',
        'Hotel_Name': 'Hotel Name',
        'Reviewer_Score': 'Review Rating',
        'Review_Date': 'Review Date'
    })
    curDf['Review Text'] = ''
    curDf = curDf.apply(parseReviewText, result_type='expand', axis=1)
    curDf['Data Source'] = 'booking.com'
    curDf = curDf[[
        'Hotel Name',
        'Hotel Address',
        'Review Date',
        'Review Rating',
        'Review Text',
        'Data Source'
        ]]
    return curDf

def datafinitiHomogenizeHelper(df):
    curDf = df
    curDf = curDf.rename(columns={
        'name': 'Hotel Name',
        'reviews.text': 'Review Text',
        'reviews.rating': 'Review Rating',
        'reviews.date': 'Review Date'
    })
    curDf['Hotel Address'] = curDf['address'] + ', ' + curDf['city'] + ', ' + curDf['province'] + ', USA'
    curDf['Data Source'] = 'Datafiniti'
    curDf = curDf[[
        'Hotel Name',
        'Hotel Address',
        'Review Date',
        'Review Rating',
        'Review Text',
        'Data Source'
        ]]
    return curDf

def tfidf(df):
    # Take a random subset of the data for hyperparameter tuning
    xTrain, xTest, yTrain, yTest = train_test_split(df['Review Text'], df['Review Rating'], test_size=0.2, random_state=42)

    # Create a pipeline with TF-IDF vectorizer and LinearSVR
    # TF-IDF vectorizer quantifies the text & LinearSVR is used to regress on these quantities
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(stop_words='english')),
        ('svr', LinearSVR())
    ])

    # Hyperparameters
    ###
    # TF-IDF converts words and/or n-grams (combinations of adjacent words) into a numerical form.
    # The Max Features hyperparameter only considers the top 5000 most frequent words and/or n-grams
    # An n-gram range of (1, 2) means that both unigrams and bigrams are considered
    # svr__C refers to regularization strength in the SVR model.
    ### 
    paramGrid = {
        'tfidf__max_features': [5000],
        'tfidf__ngram_range': [(1, 2)],
        'svr__C': [0.1, 1, 10]
    }

    # Grid search to tune hyperparameters
    gridSearch = GridSearchCV(pipeline, paramGrid, cv=3, verbose=3, n_jobs=-1)
    gridSearch.fit(xTrain, yTrain)

    # Prediction
    YPredSVR = gridSearch.predict(xTest)

    # Evaluation
    errorSVR = mean_squared_error(yTest, YPredSVR)
    print(f'Mean Squared Error using LinearSVR: {errorSVR}')

    # Example usage
    reviews = ["The hotel was clean, and the staff was friendly. Great experience!",
               "Absolutely awful. The room was extremely dirty and the staff were rude. Terrible!",
               "It was alright. Not great, but not bad either."]

    for review in reviews:
        predicted_rating = gridSearch.predict([review])
        print(f'Review: "{review}" - Predicted Rating: {predicted_rating[0]}')

def feedForwardNet(df):
    xTrain, xTest, yTrain, yTest = train_test_split(df['Review Text'], df['Review Rating'], test_size=0.2, random_state=42)

    # Tokenization and sequence padding
    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(xTrain)
    xTrainSeq = tokenizer.texts_to_sequences(xTrain)
    xTestSeq = tokenizer.texts_to_sequences(xTest)

    maxLength = min(200, max([len(seq) for seq in xTrainSeq]))
    xTrainPad = pad_sequences(xTrainSeq, maxlen=maxLength)
    xTestPad = pad_sequences(xTestSeq, maxlen=maxLength)

    # Building Feed Forward model
    modelFFNN = Sequential()
    modelFFNN.add(Embedding(input_dim=len(tokenizer.word_index) + 1, output_dim=32, input_length=maxLength))
    modelFFNN.add(Flatten())
    modelFFNN.add(Dense(32, activation='relu'))
    modelFFNN.add(Dense(1, activation='linear'))

    modelFFNN.compile(optimizer='adam', loss='mean_squared_error')
    modelFFNN.fit(xTrainPad, yTrain, epochs=3, batch_size=256)

    # Prediction
    yPredFFNN = modelFFNN.predict(xTestPad)

    # Evaluation
    errorFFNN = mean_squared_error(yTest, yPredFFNN)
    print(f'Mean Squared Error using Feed Forward NN: {errorFFNN}')

    # Example predictions
    reviews = ["The hotel was clean, and the staff was friendly. Great experience!",
               "Absolutely awful. The room was extremely dirty and the staff were rude. Terrible!",
               "It was alright. Not great, but not bad either."]
    example_sequences = tokenizer.texts_to_sequences(reviews)
    example_padded = pad_sequences(example_sequences, maxlen=maxLength)
    example_predictions = modelFFNN.predict(example_padded)

    for review, prediction in zip(reviews, example_predictions):
        print(f'Review: "{review}" - Predicted Rating: {prediction[0]}')