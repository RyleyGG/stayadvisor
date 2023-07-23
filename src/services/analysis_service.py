import pandas as pd
import os
import glob
import json


def homogenizeData(dfDict):
    ###
    # Each portion of the dataset may have its own homogenizing requirements
    # The end result must be a dataframe with columns of:
    # Hotel Name, Hotel Address (Street, City, State/Province, Country), Date of Review, Review Rating, Review Text 
    ###

    homogenizedDf = pd.DataFrame(columns=[
        'Hotel Name',
        'Hotel Address',
        'Review Date',
        'Review Rating',
        'Review Text'
    ])

    # HOMOGENIZING DATAFINIFI DATASET
    homogenizedDf = pd.concat([homogenizedDf, datafinitiHomogenizeHelper(dfDict['7282_1'])], ignore_index=True)
    homogenizedDf = pd.concat([homogenizedDf, datafinitiHomogenizeHelper(dfDict['Datafiniti_Hotel_Reviews'])], ignore_index=True)
    homogenizedDf = pd.concat([homogenizedDf, datafinitiHomogenizeHelper(dfDict['Datafiniti_Hotel_Reviews_Jun19'])], ignore_index=True)

    # HOMOGENIZING BOOKING.COM DATASET
    homogenizedDf = pd.concat([homogenizedDf, bookingComHomogenizeHelper(dfDict['Hotel_Reviews'])], ignore_index=True)

    return homogenizedDf

def prefilterData(dfArr):
    pass

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
    curDf = curDf[[
        'Hotel Name',
        'Hotel Address',
        'Review Date',
        'Review Rating',
        'Review Text'
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
    curDf = curDf[[
        'Hotel Name',
        'Hotel Address',
        'Review Date',
        'Review Rating',
        'Review Text'
        ]]
    return curDf