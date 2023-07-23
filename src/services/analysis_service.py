import pandas as pd
import os
import glob
import json


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