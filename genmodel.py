# import necessary packages

import pandas as pd
from xgboost import XGBClassifier
import sys


def main():
    xgbcomplete = XGBClassifier(learning_rate = 0.3, n_estimators=100, objective='binary:logistic', reg_alpha=1)

    filename = sys.argv[1]
    complete_data = pd.read_csv(filename, header=0)

    X_data_comp = complete_data.drop(['mortality', 'inc_key'], axis=1)
    y_data_comp = complete_data['mortality']

    xgbcomplete.fit(X_data_comp, y_data_comp)

    xgbcomplete.save_model("/src/model.json")

    return


if __name__ == "__main__":
    main()
