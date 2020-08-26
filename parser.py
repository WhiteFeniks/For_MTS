import requests
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab

from matplotlib.pyplot import figure
from sqlalchemy import create_engine

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
plt.style.use('ggplot')
matplotlib.rcParams['figure.figsize'] = (10, 8)
pd.options.mode.chained_assignment = None


# Выгрузка данных с сайта 1362 - идентификатор набора данных, $orderby - указывает поле для сортировки
# результирующего списка. А также добавление в DataFrame.

data = requests.get('https://apidata.mos.ru/v1/datasets/1362/rows?'
                    '$orderby=global_id&api_key=c0d29b6eade55d26f28e1c5bee1bf2f8').json()
res = []
for r in data:
    res.append(r['Cells'])
df = pd.DataFrame(res)
pd.set_option('display.max_columns', None)

print("\nРазмер данных: ", df.shape, '\n')
print("Типы данных:\n", df.dtypes)


# отбор числовых колонок

df_numeric = df.select_dtypes(include=[np.number])
numeric_cols = df_numeric.columns.values
print("Числовые колонки: ", numeric_cols)


# отбор нечисловых колонок

df_non_numeric = df.select_dtypes(exclude=[np.number])
non_numeric_cols = df_non_numeric.columns.values
print("\nНечисловые колонки: ", non_numeric_cols)


# Тепловая карта пропущенных значений

cols = df.columns[:30]
colours = ['#000099', '#ffff00']
sns.heatmap(df[cols].isnull(), cmap=sns.color_palette(colours))
plt.show()


# Процентный список пропущенных данных

for col in df.columns:
    pct_missing = np.mean(df[col].isnull())
    print('{} - {}%'.format(col, round(pct_missing * 100)))


# Гистограмма пропущенных данных по оси X количество пропущенных значений. По оси У количество записей.
# Создаем индикатор для признаков с пропущенными данными

for col in df.columns:
    missing = df[col].isnull()
    num_missing = np.sum(missing)
    if num_missing > 0:
        # print('created missing indicator for: {}'.format(col))
        df['{}_ismissing'.format(col)] = missing


# На основе индикатора строим гистограмму

ismissing_cols = [col for col in df.columns if 'ismissing' in col]
df['num_missing'] = df[ismissing_cols].sum(axis=1)
df['num_missing'].value_counts().reset_index().sort_values(by='index').plot.bar(x='index', y='num_missing')
plt.show()

# 39 записей не имею ни одного пропущенного значения


# Лишь небольшое количество строк содержат более 7 пропусков. Отбросим строки которые содержат 8 пропусков

ind_missing = df[df['num_missing'] > 7].index
df = df.drop(ind_missing, axis=0)


# Отбрасывание признаков. Отбросим все, которые имеют высокий процент недостоящих значений >= 46%

cols_to_drop = [['InterviewPlaceNote'], ['InterviewPlaceAdmArea'], ['InterviewPlaceDistrict'],
                ['InterviewPlaceLocation'], ['WorkPlaceNote']]
for i in cols_to_drop:
    df = df.drop(i, axis=1)


# Для числовых признаков заменим все недостающие значение медианной этого признака


df_numeric = df.select_dtypes(include=[np.number])
numeric_cols = df_numeric.columns.values
for col in numeric_cols:
    missing = df[col].isnull()
    num_missing = np.sum(missing)

    if num_missing > 0:
        # print('imputing missing values for: {}'.format(col))
        df['{}_ismissing'.format(col)] = missing
        med = df[col].median()
        df[col] = df[col].fillna(med)


# Для нечисловых признаков заменим все недостающие значение наиболее часто встречающимся значением


df_numeric = df.select_dtypes(include=[np.number])
numeric_cols = df_numeric.columns.values
for col in numeric_cols:
    missing = df[col].isnull()
    num_missing = np.sum(missing)
    if num_missing > 0:
        # print('imputing missing values for: {}'.format(col))
        df['{}_ismissing'.format(col)] = missing
        med = df[col].median()
        df[col] = df[col].fillna(med)


# Добавим недостающие значения дефолтными

df['ContactName'] = df['ContactName'].fillna('Нет данных по ФИО')
df['Phone'] = df['Phone'].fillna('Нет данных по телефону')
df['Email'] = df['Email'].fillna('Не указан email')
df['Specification'] = df['Specification'].fillna('Нет данных по спецификации')
df['DopWorkersParameters'] = df['DopWorkersParameters'].fillna('Нет данных по дополнительным параметрам')
df['WorkPlaceLocation'] = df['WorkPlaceLocation'].fillna('Нет адресса')
df['WorkPlaceDistrict'] = df['WorkPlaceDistrict'].fillna('Нет округа')
df['WorkPlaceAdmArea'] = df['WorkPlaceDistrict'].fillna('Нет района')


# Обнаружение и удаление дубликатов
# Проверим на наличие дубликатов global_id, а остальные стоблцы могут быть не уникальными

if df.global_id.nunique(dropna=True) == len(df.index):
    print("Дубликаты не обнаружены")
else:
    df = df.drop_duplicates('global_id')


# Приведем дату к типу datetime

df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)


# Удалим столбцы созданные для гистограммы

df.drop(df.iloc[:, 25:41], inplace=True, axis=1)


# Удалим лишние пробелы и точки

df_non_numeric = df.select_dtypes(exclude=[np.number])
for column in df_non_numeric:
    if column not in ['Date', 'SpecialWorkPlace', 'geoData']:
        df[column] = df[column].str.strip()
        df[column] = df[column].str.replace('\.', '')

print(df.head())


# Закинем в xlsx файл для дальнейшей работы

df.to_excel("output.xlsx", index=False)
