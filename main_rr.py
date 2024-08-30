import pickle
import pandas as pd
import csv
from csv_creator import Creator

creator = Creator()

creator.generate_fields(["mode", "mean", "median", "std", "min", "max", "trim_mean", "iqr", "mad", "cv",
                         "rms"], "rrg")
creator.create_csv("rrg", "data_rrg_big")

clf = 'model_rr.pk'
with open(clf, 'rb') as f:  # открытие обученной модели ML
    loaded_model = pickle.load(f)

data = pd.read_csv("data_rrg_big_xui.csv")
data = data.dropna()
data_names = data["id"].to_list()
data = data[list(data.columns[1:-1])].astype(int)
# получаем предсказания диагнозов
predictions = [i[0] for i in loaded_model.predict(data)]

result = list(map(list, zip(data_names, predictions)))


name_save = "result_patient"
with open(f'{name_save}.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file, delimiter=',')
    writer.writerow(["id", "patient"])
    writer.writerows(result)
