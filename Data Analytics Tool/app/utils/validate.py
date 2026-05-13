import pandas as pd
def validation(df, req_cols):
    actual_cols = list(df.columns)
    actual_lower_map = {col.lower(): col for col in actual_cols}
    

    missing = []
    case_mismatch = [] 

    for col in req_cols:
        if col in actual_cols:
            continue 
        elif col.lower() in actual_lower_map: 
            case_mismatch.append((actual_lower_map[col.lower()], col))
        else:
            missing.append(col) 

    return df, missing, case_mismatch
