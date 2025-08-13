import pandas as pd
import numpy as np
from sklearn.impute import KNNImputer

def apply_mapping(df: pd.DataFrame, mapping: dict) -> pd.DataFrame:
    """
    Rename columns based on mapping dict: {old_name: new_name}
    """
    return df.rename(columns=mapping)


def validate_and_clean(df: pd.DataFrame, config: dict) -> (pd.DataFrame, dict):
    """
    Cleans dataset based on config and returns cleaned dataframe + cleaning report.
    Config example:
    {
        "fill_missing": "median",    # median, mean, mode, knn
        "outlier_method": "remove",  # remove, winsorize
        "drop_duplicates": True,
        "type_map": {"Age": "int", "Weight": "float"}
    }
    """
    report = {
        "rows_before": len(df),
        "missing_filled": {},
        "outliers_removed": {},
        "duplicates_removed": 0,
        "type_conversions": []
    }

    # 1. Enforce data types if provided
    if "type_map" in config:
        for col, dtype in config["type_map"].items():
            if col in df.columns:
                try:
                    df[col] = df[col].astype(dtype)
                    report["type_conversions"].append(col)
                except:
                    pass

    # 2. Handle missing values
    if config.get("fill_missing") in ["median", "mean", "mode"]:
        for col in df.columns:
            if df[col].isnull().sum() > 0:
                if df[col].dtype in [np.float64, np.int64]:
                    if config["fill_missing"] == "median":
                        val = df[col].median()
                    elif config["fill_missing"] == "mean":
                        val = df[col].mean()
                    else:  # mode
                        val = df[col].mode()[0]
                else:
                    val = df[col].mode()[0]
                report["missing_filled"][col] = int(df[col].isnull().sum())
                df[col] = df[col].fillna(val)

    elif config.get("fill_missing") == "knn":
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        imputer = KNNImputer(n_neighbors=5)
        df[numeric_cols] = imputer.fit_transform(df[numeric_cols])
        # Count missing filled
        for col in numeric_cols:
            report["missing_filled"][col] = 0  # KNN fills all

    # 3. Handle outliers
    if config.get("outlier_method") in ["remove", "winsorize"]:
        for col in df.select_dtypes(include=[np.number]).columns:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            if config["outlier_method"] == "remove":
                before = len(df)
                df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
                removed = before - len(df)
                if removed > 0:
                    report["outliers_removed"][col] = removed

            elif config["outlier_method"] == "winsorize":
                df[col] = df[col].clip(lower=lower_bound, upper=upper_bound)

    # 4. Drop duplicates
    if config.get("drop_duplicates", False):
        before = len(df)
        df = df.drop_duplicates()
        report["duplicates_removed"] = before - len(df)

    report["rows_after"] = len(df)
    return df, report
