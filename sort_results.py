import os
import numpy as np
import pandas as pd
import datefinder
from datetime import datetime


def main():
    df = pd.read_csv(os.path.join("results", "combined_results.csv"))
    dates = []
    for index, row in df.iterrows():
        try:
            date = list(datefinder.find_dates(row.deadline))
            if len(date) == 1:
                dates.append(date[0])
            else:
                dates.append(np.nan)
        except TypeError:
            dates.append(np.nan)
    df["date"] = dates
    df.dropna(inplace=True)
    df.drop("deadline", axis=1, inplace=True)
    df = df[~(df["date"] < datetime.today())]
    df.sort_values(by=["date"], inplace=True)
    df.to_csv(os.path.join("results", "combined_results_sorted.csv"), index=False)


if __name__ == "__main__":
    main()
