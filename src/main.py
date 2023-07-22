import os
from services import setup_service
from services import analysis_service

def main():
    # Validate datasets and download to replace as needed
    print('=== VALIDATING DATASETS ===')
    dfArr = setup_service.validateDatasets()

    # Prefilter data to remove extraneous information
    print('=== PREFILTERING DATA ===')
    dfArr = analysis_service.prefilterData(dfArr)

    # Homogenize and combine data from various sources into same format
    print('=== HOMOGENIZING DATA ===')
    combinedArr = analysis_service.homogenizeData(dfArr)

if __name__ == '__main__':
    main()