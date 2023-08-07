### Introduction
This script was written as the final semester project for the CAP4770 data science course at the University of Florida during the Semester 2023 semester.

Taking in a large amount of hotel review data - over half a million unique reviews - the script aims to use sentiment analysis to provide better insight into hotel quality than can be provided by inconsistent and subjective star-based rating systems.

### Requirements
* [Kaggle](https://www.kaggle.com/) account with API token
    * **NOTE** Authenticating with an API token is technically optional but HIGHLY recommended. This will make the dataset download process seamless for you. The [Kaggle API Docs](https://www.kaggle.com/docs/api) contain instructions on authenticating locally with the Kaggle API, and this script will ensure you are properly authenticated before continuing.
* Python 3.10 or newer
* All library requirements are present in included in the *requirements.txt* file. Instructions on how to download these included in the Setup section.


### Setup
**NOTE:** If you have multiple versions of Python installed, you may have to change the given commands slightly to specify your version. *pip3.x* and *py -3.x* should work as alternatives to *pip* and *python* aliases.

1. Install Python 3.10 or newer
2. Pull down the most recent version of this repository to a local location.
3. Install library requirements found in *requirements.txt* by running:
    ```
    pip install -r requirements.txt
    ```
4. Either authenticate with Kaggle with an API token (instructions [here](https://www.kaggle.com/docs/api)) OR manually download the datasets:
    1. If you authenticate with Kaggle, no further action is needed at this step.
    2. If you choose to manually download the datasets, download the data for the [Booking.com](https://www.kaggle.com/datasets/jiashenliu/515k-hotel-reviews-data-in-europe) and [Datafiniti](https://www.kaggle.com/datasets/datafiniti/hotel-reviews) datasets. You will recieve a set of .zip files. Extract these into the *data* directory in the code repository. The data directory should now contain a set of *.csv* files.
5. Execute the program - open a command prompt or terminal window, navigate to the *src* directory, then:
    1. If authenticated with Kaggle, run:
        ```
        python -m main
        ```
    2. If not authenticated with Kaggle, run:
        ```
        python -m main --noauth
        ```