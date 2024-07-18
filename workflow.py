import json
import sys
import pandas as pd
from xgboost import XGBClassifier
import argparse

import genvars


def main():
    parser = argparse.ArgumentParser(description="generate transcore from input")
    parser.add_argument('patient_id', help="patient identifier string")
    parser.add_argument('icd10_codes', nargs='+', help="list of ICD10 codes")
    args = parser.parse_args()

    dictfile = open("variable_codes.json", "r")
    thedict = json.load(dictfile)
    dictfile.close()

    header, ptrows = genvars.compare_single(thedict, args.patient_id, args.icd10_codes)

    df = pd.DataFrame([ptrows], columns=header)

    xgbcomplete = XGBClassifier()
    xgbcomplete.load_model("model.json")

    X_data = df.drop(['inc_key', 'mortality'], axis=1, errors='ignore')

    predicted_mortality = xgbcomplete.predict_proba(X_data)[:, 1]

    print(predicted_mortality[0])
    return


if __name__ == "__main__":
    main()
