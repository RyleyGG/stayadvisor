import os
from services import setup_service
from services import analysis_service

def main():
    # Validate datasets and download to replace as needed
    print('=== VALIDATING DATASETS ===')
    setup_service.validateDatasets()

    # Prefilter data to remove extraneous information
    print('=== PREFILTERING DATA ===')
    analysis_service.prefilterData()

    # Homogenize and combine data from various sources into same format
    print('=== HOMOGENIZING DATA ===')
    analysis_service.homogenizeData()

if __name__ == '__main__':
    main()