# -*- coding: utf-8 -*-
import os
import pandas as pd

def export_to_excel(rows, output_xlsx: str):
    df = pd.DataFrame(rows, columns=["path", "file_name", "tag"])
    os.makedirs(os.path.dirname(output_xlsx), exist_ok=True)
    df.to_excel(output_xlsx, index=False)
