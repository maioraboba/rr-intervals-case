import os
import csv
import pandas as pd
from scipy import stats
import numpy as np


class Creator:
    def __init__(self):
        self.data = list()  # Список для хранения данных из файлов
        self.num_fields = 16
        self.fields = list()
        self.folder_path = 'data'   # Папка, содержащая файлы
        self.patient = [None] * self.num_fields  # строчка пациента
        self.name_last, self.name_check, self.type_patient = "", "", ""
        self.stats = list()

    def calculate_stats(self, line):
        res = list()
        mode = line.mode()[0]
        mean = line.mean()
        median = line.median()
        std = line.std(ddof=1)
        minimal = line.min()
        maximum = line.max()
        trim_mean = stats.trim_mean(line, 0.1)  # Усеченное среднее
        iqr = line.quantile(0.75) - line.quantile(0.25)     # Межквартильный размах
        mad = stats.median_abs_deviation(line)  # Median Absolute Deviation
        coefficient_of_variation = (std / mean) * 100   # Коэффициент вариации

        differences = line.diff().dropna()
        squared_differences = differences ** 2
        mean_squared_difference = squared_differences.mean()
        rms_difference = np.sqrt(mean_squared_difference)   # Среднеквадратичное различие

        # Расчет абсолютного прироста
        absolute_growth = line.diff()

        # Расчет темпа роста
        growth_rate = absolute_growth / line.shift(1)

        average_absolute_growth = absolute_growth.mean()
        average_growth_rate = growth_rate.mean()

        dct_stats = {"mode": mode, "mean": int(mean), "median": int(median), "std": int(std), "min": minimal, "max": maximum,
                     "trim_mean": trim_mean, "iqr": iqr, "mad": mad, "cv": coefficient_of_variation,
                     "rms": rms_difference, "aag": average_absolute_growth, "agr": average_growth_rate}

        for i in self.stats:
            res.append(dct_stats[i])    # Берём из словаря только те значения, которые передали в параметры
        return res

    @classmethod
    def name_to_default_style(cls, nm):
        name_chk = nm
        for i in ["_СТОЯ", "_ЛЕЖА", "СТОЯ", "ЛЕЖА"]:
            name_chk = name_chk.replace(i, "")  # приводим имена файла к единому виду для сравнения
        name_chk = name_chk.strip()
        return name_chk

    def generate_fields(self, stats, type_file, positions=("лежа", "стоя")):
        res = ["id"]
        for m in stats:
            for j in positions:
                res.append(f"{type_file}_{m}_{j}")
        res.append("patient")
        self.fields = res
        self.num_fields = len(res) - 2
        self.stats = stats

    def append_patient_to_data(self):
        self.patient.insert(0, self.name_last)
        self.patient.append(self.type_patient)
        self.data.append(self.patient)
        self.patient = [None] * self.num_fields

    def save_data_to_csv(self, name_save):
        # Сохранить результат в новый CSV-файл
        with open(f'{name_save}.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerow(self.fields)
            writer.writerows(self.data)

    def create_csv(self, file_type, name_file_to_save):
        # Прочитать каждый файл в папке и сохранить данные в список
        for self.type_patient in os.listdir(self.folder_path):
            self.name_last = ""
            self.patient = [None] * self.num_fields
            for file_name in os.listdir(os.path.join(self.folder_path, self.type_patient)):
                with open(os.path.join(self.folder_path, self.type_patient, file_name), 'r', encoding='mbcs') as file:
                    lines = file.readlines()
                    name = " ".join(lines[0].split()[:-3])
                    self.name_check = self.name_to_default_style(name)

                    if self.name_last != "" and self.name_last != self.name_check:
                        self.append_patient_to_data()

                    if file_type == "rrg":
                        if file_name[-3:] == 'rrg':
                            lines = pd.Series([60 / float(line.strip()) for line in lines[2:-1] if float(line.strip())])
                            info = self.calculate_stats(lines)
                            if "СТОЯ" in name:
                                for i in range(self.num_fields // 2):
                                    self.patient[i * 2 + 1] = info[i]
                            else:
                                for i in range(self.num_fields // 2):
                                    self.patient[i * 2] = info[i]
                    else:
                        if file_name[-3:] == "rrn":
                            lines = pd.Series([float(line.strip()) for line in lines[1:-1] if float(line.strip())])
                            info = self.calculate_stats(lines)
                            if "СТОЯ" in name:
                                for i in range(self.num_fields // 2):
                                    self.patient[i * 2 + 1] = info[i]
                            else:
                                for i in range(self.num_fields // 2):
                                    self.patient[i * 2] = info[i]

                    self.name_last = self.name_check

            self.append_patient_to_data()

        self.save_data_to_csv(name_file_to_save)


if __name__ == '__main__':
    creator = Creator()

    # creator.generate_fields(["mode", "max", "min", "mean", "cv", "rms", "aag", "agr"], "rrn")
    # creator.create_csv("rrn", "data_rrn_big_new")

    creator.generate_fields(["mode", "mean", "median", "std", "min", "max", "trim_mean", "iqr", "mad", "cv",
                             "rms"], "rrg")
    creator.create_csv("rrg", "data_rrg_big")
