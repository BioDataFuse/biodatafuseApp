import pandas as pd
import base64


def download_tsv_as_link(data: pd.DataFrame, filename: str):
    """create a download link for the output table of queries.

    @param data: combined output table
    @param filename: filename
    """

    res = data.to_csv(index=False, sep="\t").encode("utf-8")
    b64 = base64.b64encode(res).decode()
    download_url = f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}.tsv">**Download output tsv file**</a>'

    return download_url


def download_parquet_as_link(data: pd.DataFrame, filename: str):
    """create a download link for the output of queries in parquet format.

    @param data: combined output table in parquet
    @param filename: filename
    """

    res = data.to_parquet()
    b64 = base64.b64encode(res).decode()
    download_url = f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}.pq">**Download output parquet file**</a>'

    return download_url
