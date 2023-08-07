import pandas as pd
import kaggle
import os
import glob
import json
from services.config_service import config

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
    # Ensuring schema file is present and has keys with 1:1 match with files in data directory
    if not glob.glob(f'{config.cwd}/file_schemas.json'):
        print('File schema reference... MISSING')
        print('Redownload from repository. Exiting...')
        exit(1)

def validateDatasets():
    dataFinitiValid = True
    bookingComValid = True

    # Ensuring schema file is present and has keys with 1:1 match with files in
    fileSchemas = json.load(open(f'{config.cwd}/file_schemas.json'))
    filenames = glob.glob(f'{config.cwd}/data/*.csv')
    filenames = [filename.replace('\\', '/') for filename in filenames]
    filenames = [filename.split(f'{config.cwd}/data/')[1].split('.csv')[0] for filename in filenames]
    for filename in filenames:
        if filename not in fileSchemas.keys():
            print(f'Entry for file {filename} not found in schema file. Exiting...')
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
    downloadDatasets(dataFinitiValid, bookingComValid)
    
    # Second, check schemas for files if all files for that dataset are present
    dataFinitiValid = validateDatasetFileSchema(dataFinitiFiles, fileSchemas)
    bookingComValid = validateDatasetFileSchema(bookingComFiles, fileSchemas)
    downloadDatasets(dataFinitiValid, bookingComValid)

    # Final validity check
    dataFinitiValid = validateDatasetFileSchema(dataFinitiFiles, fileSchemas)
    bookingComValid = validateDatasetFileSchema(bookingComFiles, fileSchemas)
    if not dataFinitiValid or not bookingComValid:
        print('Files were redownloaded, but issues were still present during schema check procedure')
        print('It is possible the script is expecting an older version of the datasets. Exiting...')
        exit(1)

    print('DATA VALIDATION... COMPLETE')
    print('INITIAL DATA INGEST... STARTED')
    
    allFilenames = []
    allFilenames.extend(dataFinitiFiles)
    allFilenames.extend(bookingComFiles)
    dfDict = ingestData(allFilenames)
    print('INITIAL DATA INGEST... COMPLETE')
    return dfDict

def downloadDatasets(dataFiniti, bookingCom):
    if not config.kaggleAuth and (not dataFiniti or not bookingCom):
        print('There were issues with the downloaded files, but Kaggle authentication is disabled')
        print('Unable to remedy issues. Exiting...')
        exit(1)
    if not dataFiniti:
        print('Datafiniti dataset invalid or missing. Downloading...')
        kaggle.api.dataset_download_files('datafiniti/hotel-reviews', path=f'{config.cwd}/data', unzip=True)
    if not bookingCom:
        print('Booking.com dataset invalid or missing. Downloading...')
        kaggle.api.dataset_download_files('jiashenliu/515k-hotel-reviews-data-in-europe', path=f'{config.cwd}/data', unzip=True)

def validateDatasetFilesExist(filenames, datasetName):
    for filename in filenames:
        if not glob.glob(f'{config.cwd}/data/{filename}.csv'):
            print(f'{datasetName}... MISSING FILES')
            return False
    return True

def validateDatasetFileSchema(filenames, schemaObj):
    for filename in filenames:
        validCols = schemaObj[filename]
        fileDf = pd.read_csv(f'{config.cwd}/data/{filename}.csv')
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
        returnObj[filename] = pd.read_csv(f'{config.cwd}/data/{filename}.csv')
    return returnObj