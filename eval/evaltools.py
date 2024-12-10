from difflib import SequenceMatcher
import sqlglot
import importlib
import re
import sys
import os
project_dir = os.path.abspath("..") 
chat2dbchatbot_dir = os.path.join(project_dir, "chat2dbchatbot")
if chat2dbchatbot_dir not in sys.path:
    sys.path.append(chat2dbchatbot_dir)
import tagsql
import ragsql
importlib.reload(ragsql)
importlib.reload(tagsql)
import pandas as pd
import numpy as np

from sklearn.preprocessing import MinMaxScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# rag call wrapper function
def gen_rag_query(textQuery: str, llm_provider: str = "OpenAI", temperature: float = 0.1)->str:
        result = ""
        try:
            result = ragsql.run_rag_pipeline(textQuery, llm_provider, temperature)
            return clean_sql(result)
        except Exception as e:
            print(e)
            return "error"
        
# tag call wrapper function
async def gen_tag_query(textQuery: str, llm_provider: str = "OpenAI", temperature: float = 0.1)->str:
        result = ""
        try:
            result = await tagsql.run_tag_pipeline(textQuery, llm_provider, temperature, "query_synthesis")
            return clean_sql(result)
        except Exception as e:
            print(e)
            return "error"

#check SQL validity through sqlglot
def check_sql_errors(rq: str)->dict:
    try:
        parsed = sqlglot.parse_one(rq, dialect='postgres') #specify the database type
        return {
                "isValid": True,
                "errMessage": "",
            }
    except Exception as e:
        print(e)
        return {
                "isValid": False,
                "errMessage": str(e),
            }
#check if the query is an SQL query
def is_sql_check(rq: str) -> bool:
    isSQL = False
    rq  = rq.strip().upper()
    if (rq and (rq != "ERROR") and (rq.startswith('SELECT') or rq.startswith('WITH') or rq.startswith('CREATE TABLE'))):
            isSQL = True
    return isSQL

#check if translatability identified by chatbot is the same as actual translatability
def confirm_type(rq: str, isExpectSQL:bool) -> bool:
    if is_sql_check(rq) == isExpectSQL:
         return True
    else: return False


#clean unnecessary characters from the sql string, especially for Claude RAG, need to remove noise: text before and after the SQL script, line breaks, SQL comment through "--"
def clean_sql(rq: str)->str:
    result = ""
    try:
        no_comm = re.sub(r"--.*?(\n|$)", "", rq)
        result = re.sub(r"[\r\n\s]+", " ", no_comm).strip()
        return result
    except Exception as e:
        print(e)
        return "error"

#remove all the white spaces and linebreaks and standardize the letter cases.       
def flatten_sql(rq: str)->str:
    try:
        flattened = re.sub(r"[\s;]+", "", rq).lower()
        return flattened
    except sqlglot.ParseError as e:
        print(e)        
        return "error"

#check how similar the generated SQL is to expected SQL          
def sql_compare_score(esql: str, gsql: str) -> float:
    try:
        esql_flat = flatten_sql(esql)
        gsql_flat = flatten_sql(gsql)
        score = SequenceMatcher(None, esql_flat, gsql_flat).ratio()
        return score
    except Exception as e:
        print(e)        
        return -1    

# len(expected sql) - len(generated sql), the more positive the better
def sql_length_score(esql: str, gsql: str) -> int:
    try:
        esql_flat = flatten_sql(esql)
        gsql_flat = flatten_sql(gsql)
        gsql_len = len(gsql_flat)
        esql_len = len(esql_flat)
        if(gsql_len<1):
            return -10000
        else:
            return (esql_len - gsql_len)
    except Exception as e:
        print(e)        
        return -10000
    

#cosine similarity of the SQL call response data frames
def cosin_sim(edf, gdf) -> float:
    try:
        if not isinstance(edf, pd.DataFrame) or not isinstance(gdf, pd.DataFrame):
            # print("Error: One or both inputs are not valid DataFrames")
            return 0

        # Ensure DataFrames are not empty
        if edf.empty or gdf.empty:
            # print("Error: One or both DataFrames are empty")
            return 0

        common_columns = list(set(edf.columns) & set(gdf.columns))
        if not common_columns:
            # print("Error: No common columns found")
            return 0
        
        cdf1 = edf[common_columns].copy()
        cdf2 = gdf[common_columns].copy()

        numeric_columns = cdf1.select_dtypes(include=['number']).columns.tolist()
        text_columns = cdf1.select_dtypes(include=['object']).columns.tolist()

        # handle numeric column and text column separately
        #text column needs to do Tfidf to do vectorization
        if numeric_columns:
            constant_columns = cdf1[numeric_columns].nunique() == 1
            non_constant_columns = cdf1[numeric_columns].loc[:, ~constant_columns]

            if not non_constant_columns.empty:
                scaler = MinMaxScaler()
                scaled_non_constant1 = scaler.fit_transform(non_constant_columns)
                scaled_non_constant2 = scaler.transform(cdf2[non_constant_columns.columns])
            else:
                scaled_non_constant1 = np.zeros((len(cdf1), 0))
                scaled_non_constant2 = np.zeros((len(cdf2), 0))

            if constant_columns.any():
                constant_values1 = cdf1[constant_columns.index[constant_columns]].values
                constant_values2 = cdf2[constant_columns.index[constant_columns]].values

                constant_values1 = constant_values1.reshape(-1, 1) if len(constant_values1.shape) == 1 else constant_values1
                constant_values2 = constant_values2.reshape(-1, 1) if len(constant_values2.shape) == 1 else constant_values2

                numeric1 = np.hstack((scaled_non_constant1, constant_values1))
                numeric2 = np.hstack((scaled_non_constant2, constant_values2))
            else:
                numeric1, numeric2 = scaled_non_constant1, scaled_non_constant2
        else:
            numeric1, numeric2 = np.zeros((len(cdf1), 0)), np.zeros((len(cdf2), 0))

        if text_columns:
            cdf1['combined_text'] = cdf1[text_columns].apply(lambda x: ' '.join(x.astype(str)), axis=1)
            cdf2['combined_text'] = cdf2[text_columns].apply(lambda x: ' '.join(x.astype(str)), axis=1)

            vectorizer = TfidfVectorizer()
            text_vectors1 = vectorizer.fit_transform(cdf1['combined_text'])
            text_vectors2 = vectorizer.transform(cdf2['combined_text'])
            text_vectors1 = text_vectors1.toarray()
            text_vectors2 = text_vectors2.toarray()
        else:
            text_vectors1, text_vectors2 = np.zeros((len(cdf1), 0)), np.zeros((len(cdf2), 0))

        if numeric1.size > 0 and text_vectors1.size > 0:
            vectors1 = np.hstack((numeric1, text_vectors1))
            vectors2 = np.hstack((numeric2, text_vectors2))
        elif numeric1.size > 0:
            vectors1, vectors2 = numeric1, numeric2
        elif text_vectors1.size > 0:
            vectors1, vectors2 = text_vectors1, text_vectors2
        else:
            return 0

        cosine_sim = cosine_similarity(vectors1, vectors2)
        return np.mean(cosine_sim)
    
    except Exception as e:
        # print("Error:", e)
        return 0

# compare SQL response data frame first get column similarity then row similarity
def qr_compare(edf, gdf) -> dict:
    try:
        common_columns = list(set(edf.columns) & set(gdf.columns))
        if (not common_columns) or (edf.columns.size == 0):
            return {
                "common_cols": [],
                "cols_sim_score": 0,
                "rows_sim_score": 0,
                "total_sim_score": 0
            } 
        else:         

            cols_sim_score = len(common_columns) / len(edf.columns)
            edf_common = edf[common_columns]
            gdf_common = gdf[common_columns]

            edf_len = len(edf_common)
            gdf_len = len(gdf_common)
            num_len_diff = abs(edf_len - gdf_len)

            if (edf_len == 0) and (gdf_len == 0):
                rows_sim_score = 1
            elif (edf_len == 0) and (gdf_len > 0):
                rows_sim_score = 0
            else:           
                num_match_row = 0

                if edf_len < gdf_len:
                    num_len_diff_score = num_len_diff/gdf_len
                    for i in range(edf_len):
                        matched = False
                        for j in range(gdf_len):
                            if(edf_common.iloc[i].equals(gdf_common.iloc[j])):
                                matched = True
                                break
                        if matched:            
                            num_match_row = num_match_row + 1
                
                else:
                    num_len_diff_score = num_len_diff/edf_len
                    for i in range(gdf_len):
                        matched = False
                        for j in range(edf_len):
                            if(gdf_common.iloc[i].equals(edf_common.iloc[j])):
                                matched = True
                                break
                        if matched:            
                            num_match_row = num_match_row + 1
        
                rows_sim_score = num_match_row/edf_len

            #weighted sum num_len_diff_score is a penalty
            total_sim_score = (cols_sim_score * 0.5) + (rows_sim_score * 0.5) - (num_len_diff_score*0.1)
            if(total_sim_score<0):
                total_sim_score = 0

            return {
                "common_cols": common_columns,
                "cols_sim_score": cols_sim_score,
                "rows_sim_score": rows_sim_score,
                "total_sim_score": total_sim_score
            }  

    except Exception as e:
        print("exception happened, ", e)
        return {
            "common_cols": [],
            "cols_sim_score": 0,
            "rows_sim_score": 0,
            "total_sim_score": 0
        }  

#Compare contents, columns with certain number of consecutive matching characters are considered same
def qr_compare_fuz(edf, gdf, fuz_len=0) -> dict:
    try:

        def preprocess_column_name(col_name):
            return re.sub(r'[^a-zA-Z]', '', col_name)

        edf_cols_processed = {col: preprocess_column_name(col) for col in edf.columns}
        gdf_cols_processed = {col: preprocess_column_name(col) for col in gdf.columns}

        # Precompute substrings of length fuz_len for all columns
        def compute_substrings(col_name, fuz_len):
            return {col_name[i:i+fuz_len] for i in range(len(col_name) - fuz_len + 1)}

        edf_substrings = {
            col: compute_substrings(proc_col, fuz_len)
            for col, proc_col in edf_cols_processed.items()
        }
        gdf_substrings = {
            col: compute_substrings(proc_col, fuz_len)
            for col, proc_col in gdf_cols_processed.items()
        }

        # Find common columns with fuz_len logic
        column_mapping = {}
        for gdf_orig, gdf_subs in gdf_substrings.items():
            for edf_orig, edf_subs in edf_substrings.items():
                if gdf_subs & edf_subs:  # Fast set intersection
                    column_mapping[gdf_orig] = edf_orig
                    break

        common_columns = list(column_mapping.values())

        if not common_columns or edf.columns.size == 0:
            return {
                "common_cols": [],
                "cols_sim_score": 0,
                "rows_sim_score": 0,
                "total_sim_score": 0
            }

        # Rename gdf columns based on matches
        gdf_renamed = gdf.rename(columns=column_mapping)
        cols_sim_score = len(common_columns) / len(edf.columns)
        edf_common = edf[common_columns]
        gdf_common = gdf_renamed[common_columns]

        edf_len = len(edf_common)
        gdf_len = len(gdf_common)

        if edf_len == 0 and gdf_len == 0:
            rows_sim_score = 1
        elif edf_len == 0 and gdf_len > 0:
            rows_sim_score = 0
        else:
            num_match_row = 0
            if edf_len < gdf_len:
                for i in range(edf_len):
                    for j in range(gdf_len):
                        if edf_common.iloc[i].equals(gdf_common.iloc[j]):
                            num_match_row += 1
            else:
                for i in range(gdf_len):
                    for j in range(edf_len):
                        if gdf_common.iloc[i].equals(edf_common.iloc[j]):
                            num_match_row += 1

            rows_sim_score = num_match_row / edf_len

        total_sim_score = (cols_sim_score * 0.5) + (rows_sim_score * 0.5)

        return {
            "common_cols": common_columns,
            "cols_sim_score": cols_sim_score,
            "rows_sim_score": rows_sim_score,
            "total_sim_score": total_sim_score
        }

    except Exception as e:
        print("Exception happened:", e)
        return {
            "common_cols": [],
            "cols_sim_score": 0,
            "rows_sim_score": 0,
            "total_sim_score": 0
        }