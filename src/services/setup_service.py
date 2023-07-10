import pandas as pd
import kaggle
import os

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

def validateDatasets():
    dataFinitiValid = True
    tripAdvisorValid = True
    bookingCom = True

    downloadDatasets(not dataFinitiValid, not tripAdvisorValid, not bookingCom)
    print('All datasets have either been deemed valid or redownloaded')

def downloadDatasets(dataFiniti = False, tripAdvisor = False, bookingCom = False):
    if not dataFiniti:
        print('Datafiniti dataset invalid or missing. Downloading...')
        kaggle.api.dataset_download_files('datafiniti/hotel-reviews', path=f'{os.getcwd()}/data', unzip=True)
    if not tripAdvisor:
        print('TripAdvisor dataset invalid or missing. Downloading...')
        kaggle.api.dataset_download_files('larxel/trip-advisor-hotel-reviews', path=f'{os.getcwd()}/data', unzip=True)
    if not bookingCom:
        print('Booking.com dataset invalid or missing. Downloading...')
        kaggle.api.dataset_download_files('jiashenliu/515k-hotel-reviews-data-in-europe', path=f'{os.getcwd()}/data', unzip=True)