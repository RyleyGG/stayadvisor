import argparse
from services import setup_service
from services import analysis_service
from services.config_service import config

def main():
    argParser = argparse.ArgumentParser()
    argParser.add_argument('-noauth', action='store_true')
    args = argParser.parse_args()
    config.kaggleAuth = not args.noauth

    if config.kaggleAuth:
        # Validate Kaggle connection
        print('=== VALIDATING KAGGLE CREDENTIALS ===')
        setup_service.validateKaggle()

    # Validating existence of other required files
    print('=== VALIDATING SCHEMA REFERENCES ===')
    setup_service.validateSchemaFiles()

    # Validate datasets and download to replace as needed
    print('=== VALIDATING DATASETS ===')
    dfDict = setup_service.validateDatasets()

    # Homogenize data to get only relevant information
    print('=== HOMOGENIZING DATA ===')
    combinedDf = analysis_service.homogenizeData(dfDict)

    # Once data has been collected into one data object, remove unwanted rows
    print('=== PREFILTERING DATA ===')
    combinedDf = analysis_service.prefilterData(combinedDf)

    # print('=== RUNNING TFIDF MODEL ===')
    # analysis_service.tfidf(combinedDf)

    print('=== RUNNING DEEP LEARNING MODEL ===')
    analysis_service.feedForwardNet(combinedDf)

if __name__ == '__main__':
    main()