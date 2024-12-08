# Intent Classification

## Folder Contents

### `combined_sql_classifier.pkl`
- A pre-trained classifier model saved as a pickle file.  
- This model is used to classify intents and provide additional metadata for SQL-related queries.

### `classifier_test.py`
- A standalone script to test the classifier.  
- It loads the classifier model and classifies a given prompt.

### `Final_Intent_Classifier_Pipeline.ipynb`
- A Jupyter Notebook that contains the pipeline for training and evaluating the intent classifier.  
- It includes data preprocessing, model training, and evaluation steps.

## Usage

### 1. Testing the Classifier
To test the classifier using the `classifier_test.py` script:
- This script will load the classifier model from `combined_sql_classifier.pkl` and classify a given prompt.

### 2. Training the Classifier
To run and train the classifier using the Jupyter Notebook:
1. Open `Final_Intent_Classifier_Pipeline.ipynb` in Jupyter Notebook or Google Colab.
2. Follow the steps in the notebook to preprocess the data, train the model, and evaluate its performance.