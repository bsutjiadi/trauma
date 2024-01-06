import json
import sys
import pandas as pd
from xgboost import XGBClassifier

import genvars


def main():
    dictfile = open("variable_codes.json", "r")
    thedict = json.load(dictfile)
    dictfile.close()

    incsv = open(sys.argv[1], "r")
    header, ptrows = genvars.compare_parallel(thedict, incsv)
    incsv.close()

    df = pd.DataFrame(ptrows, columns=header)

    xgbcomplete = XGBClassifier()
    xgbcomplete.load_model("model.json")

    X_data = df.drop(['inc_key', 'mortality'], axis=1)

    predicted_mortality = xgbcomplete.predict_proba(X_data)[:, 1]

    inputdata = pd.read_csv(sys.argv[1])
    data2 = inputdata.assign(transcore=predicted_mortality)

    data2.to_csv('output.csv', index=False)
    return


if __name__ == "__main__":
    main()
