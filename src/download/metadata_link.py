import json
import base64

def download_json_as_link(
    metadata_path: str,
    filename: str):
    """create a download link for the metadata of the queries.

    @param metadata_path: the path to the metadata
    @param filename: filename     
    """

    metadata = json.load(open(metadata_path))    
    res = json.dumps(
        metadata,
        indent = 4,
        ensure_ascii = False).encode('utf-8')
    b64 = base64.b64encode(res).decode()
    download_url = f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}.json">**Download the query information**</a>'
    
    return download_url