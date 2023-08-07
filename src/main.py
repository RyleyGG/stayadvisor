import os
from services import setup_service
from services import analysis_service


def main():
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

if __name__ == '__main__':
    main()