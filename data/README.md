\# Dataset



The dataset used in this project is not included in this repository because it exceeds GitHub's 100 MB file size limit.



\## Download



Download the dataset from the following Google Drive folder:



\*\*Google Drive:\*\*  

<PASTE\_YOUR\_GOOGLE\_DRIVE\_LINK\_HERE>



\## Google Colab Setup



If you are running the notebooks in Google Colab, mount your Google Drive:



```python

from google.colab import drive

drive.mount('/content/drive')

```



Then update the dataset path if necessary. For example:



```python

df = pd.read\_csv(

&#x20;   "/content/drive/MyDrive/phishing-url-detection/cleaned\_phishing\_dataset\_with\_features.csv"

)

```



\## Local Setup



If you are running the notebooks locally, download the dataset and place it inside the `data/` directory.



Example:



```text

project/

├── data/

│   └── cleaned\_phishing\_dataset\_with\_features.csv

├── notebooks/

├── models/

└── README.md

```



Then update the dataset path accordingly, for example:



```python

df = pd.read\_csv("data/cleaned\_phishing\_dataset\_with\_features.csv")

```



\## Notes



\- Ensure the dataset filename matches the one used in the notebooks.

\- If you store the dataset in a different location, update the file path in the notebook before running it.

