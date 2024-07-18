import pandas as pd
from xgboost import XGBClassifier
import sys


def main():
    xgbcomplete = XGBClassifier()
    xgbcomplete.load_model("model.json")

    filename = sys.argv[1]
    data = pd.read_csv(filename)
    X_data = data.drop(['inc_key', 'mortality'], axis=1, errors='ignore')

    predicted_mortality = xgbcomplete.predict_proba(X_data)[:, 1]

    inputdatafn = sys.argv[2]
    inputdata = pd.read_csv(inputdatafn)
    data2 = inputdata.assign(transcore=predicted_mortality)

    data2.to_csv('output.csv', index=False)
    return


if __name__ == "__main__":
    main()
