# EVALUATION FRAMEWORK



## Usage

### 1. Run the evaluations
- Need to be under Dev environment. If Docker not yet on, under chat-to-database-chatbot/ folder run `make dev`
- Once docker is on, go to the jupyter notebook: eval.ipynb run the steps. (recommend to use Visual studio code with Jupyter component)
- Bot Dev mode requires Python 3.11+ support from the system running the docker
- (keep eval_set.csv in the data folder)


## Folder Contents

### `eval.ipynb`
- A Jupyter Notebook that contains the data manapiluation analysis and plots.  
- The GUI of the evaluation framework.

### `evaltools.py`
- set of functions used to call LLMs, manipulate SQLs and Response from SQLs, calculate metrics. 
- Functions in this file are being called by eval.ipynb.

### `sqltr.py`
- A class that communicate with the Domain DB to call with expected or generated SQL, convert response to a dataframe.
- The Class and function in this file are being called by eval.ipynb.

### `data` 
- folder containing test dataset. 
- dataset name: `eval_set.csv`

### `html_exports`
- some sample html exports of the eval.ipynb 

### `ingestsql.py`
- customized based on chat2dbchatbot/tools/ingest.py
    - removed print statements to prevent vast printout during batch processing(still kept printout for exceptions).

### `ragsql.py`
- customized based on chat2dbchatbot/tools/rag.py
    - removed print statements to prevent vast printout during batch processing(still kept printout for exceptions).
    - reference ingestsql.py to further limit printout.
    - add in a function to parse response from Claude to retrieve SQL query embedded in text.
    - modified run_rag_pipeline to stop and return with SQL instead of natural language text. 


### `tagsql.py`
- customized based on chat2dbchatbot/tools/tag.py
    - modified run_tag_pipeline to stop and return with SQL instead of natural language text. 
    - reference and call some class functions in chat2dbchatbot/tools/tag.py

