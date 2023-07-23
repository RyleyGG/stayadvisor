import pandas as pd
import kaggle
import os
import glob
import json

def validateKaggle():
    try:
        kaggle.api.authenticate()
    except OSError:
        print('Kaggle was unable to authenticate. It is likely you have not set up your token credentials correctly.\
              Please review the instructions at https://www.kaggle.com/docs/api and re-run this program.')
        exit(1)
    except Exception as e:
        print('An unknown error occurred while authenticating with the Kaggle API. This may be a result of not setting up\
              token credentials correctly. Please review the instructions at https://www.kaggle.com/docs/api and re-run this program.')
        print(f'ERROR MSG: {str(e)}') # Provide error msg in catch-all incase the error is not related to token

def validateSchemaFiles():
    # Ensuring schema file is present and has keys with 1:1 match with files in 
    if not glob.glob('file_schemas.json'):
        print('File schema reference... MISSING')
        print('Redownload from repository. Exiting...')
        exit(1)

def validateDatasets():
    dataFinitiValid = True
    bookingComValid = True

    # Ensuring schema file is present and has keys with 1:1 match with files in
    fileSchemas = json.load(open('./file_schemas.json'))
    filenames = glob.glob('./data/*.csv')
    filenames = [filename.split('./data\\')[1].split('.csv')[0] for filename in filenames]
    for filename in filenames:
        if filename not in fileSchemas.keys():
            print(f'Key mismatch between schema file and data directory: {filename}. Exiting...')
            exit(1)

    for schemaKey in fileSchemas.keys():
        if schemaKey not in filenames:
            print(f'Key mismatch between schema file and data directory: {schemaKey}. Exiting...')
            exit(1)

    # First, ensure files from both datasets are present
    dataFinitiFiles = [
        '7282_1',
        'Datafiniti_Hotel_Reviews_Jun19',
        'Datafiniti_Hotel_Reviews',
    ]
    bookingComFiles = [
        'Hotel_Reviews'
    ]
    dataFinitiValid = validateDatasetFilesExist(dataFinitiFiles, 'Datafiniti')
    bookingComValid = validateDatasetFilesExist(bookingComFiles, 'booking.com')
    
    # Second, check schemas for files if all files for that dataset are present
    dataFinitiValid = validateDatasetFileSchema(dataFinitiFiles, fileSchemas)
    bookingComValid = validateDatasetFileSchema(bookingComFiles, fileSchemas)

    downloadDatasets(dataFinitiValid, bookingComValid)
    print('DATA VALIDATION... COMPLETE')
    print('INITIAL DATA INGEST... STARTED')
    
    allFilenames = []
    allFilenames.extend(dataFinitiFiles)
    allFilenames.extend(bookingComFiles)
    dfDict = ingestData(allFilenames)
    print('INITIAL DATA INGEST... COMPLETE')
    return dfDict

def downloadDatasets(dataFiniti, bookingCom):
    if not dataFiniti:
        print('Datafiniti dataset invalid or missing. Downloading...')
        kaggle.api.dataset_download_files('datafiniti/hotel-reviews', path=f'{os.getcwd()}/data', unzip=True)
    if not bookingCom:
        print('Booking.com dataset invalid or missing. Downloading...')
        kaggle.api.dataset_download_files('jiashenliu/515k-hotel-reviews-data-in-europe', path=f'{os.getcwd()}/data', unzip=True)

def validateDatasetFilesExist(filenames, datasetName):
    for filename in filenames:
        if not glob.glob(f'./data/{filename}.csv'):
            print(f'{datasetName}... MISSING FILES')
            return False
    return True

def validateDatasetFileSchema(filenames, schemaObj):
    for filename in filenames:
        validCols = schemaObj[filename]
        fileDf = pd.read_csv(f'./data/{filename}.csv')
        for col in fileDf.columns:
            if col not in validCols:
                print(f'Unexpected column "{col}" in file {filename}.csv. Marking for redownload...')
                return False
        
        for col in validCols:
            if col not in fileDf.columns:
                print(f'Expected column "{col}" not found in file {filename}.csv. Marking for redownload...')
                return False
        return True
    
def ingestData(filenames):
    returnObj = {}
    for filename in filenames:
        returnObj[filename] = pd.read_csv(f'./data/{filename}.csv')
    return returnObj