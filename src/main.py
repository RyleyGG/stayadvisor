import os
from services import setup_service
from services import analysis_service

def main():
    print(os.getcwd())
    # Validate datasets and download to replace as needed
    setup_service.validateDatasets()

    # Prefilter data to remove extraneous information
    analysis_service.prefilterData()

    # Homogenize and combine data from various sources into same format
    analysis_service.homogenizeData()

if __name__ == '__main__':
    main()