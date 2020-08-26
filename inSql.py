# Процесс настройки MySQL для загрузки данных в БД

# Допустим у нас есть пользователь под именем test
# Зайдем в него:
# mysql -u test -p
# Проверим правильный ли пользователь и существующие базы данных:
# SELECT USER(), DATABASE();
# если баз данных нет, то создадим например базу данных с названием "workers"
# CREATE DATABASE workers;
# выберем новую базу данных workers
# USE workers;
# теперь подключимся из Python и выгрузим в MySQL

import pandas as pd
from pandas.io import sql
from sqlalchemy import create_engine

# Считываем данные из подготовленного файла

data = pd.read_excel('output.xlsx', index_col=0)


# Подключаемся к пользователю test и базе данных workers
engine = create_engine("mysql+pymysql://{user}:{pw}@localhost/{db}"
                       .format(user="test",
                               pw="123456",
                               db="workers"))

# Закидываем данные в таблице с названием employee

data.to_sql(con=engine, name='employee', if_exists='replace')

# Сделаем global_id PRIMARY KEY
# ALTER TABLE employee ADD PRIMARY KEY (global_id);

# Из определения 6 нормальной формы следует, что переменная находится в 6НФ
# тогда и только тогда, когда она неприводима, то есть не может быть подвергнута
# дальнейшей декомпозиции без потерь, т.е. «декомпозиции до конца».

# Создадим таблицу vacancy с информацией по вакансии столбцы выбраны с учетом дополняемости, одно без другого не понятно что за вакансия,
# поэтому декомпозировать дальше нельзя
# CREATE TABLE vacancy (global_id BIGINT, Number TEXT, Prof TEXT, Specification TEXT, WorkFunction TEXT, CONSTRAINT global_id PRIMARY KEY (global_id));
# INSERT INTO vacancy (SELECT global_id, Number, Prof, Specification, WorkFunction FROM employee);
# SELECT * FROM vacancy;


# Создадим таблицу worker с информацией которая связывает global_id ваканссии с работником
# CREATE TABLE worker (ContactId BIGINT, ContactName TEXT, ProfStage BIGINT);
# INSERT INTO worker (SELECT global_id, ContactName, ProfStage FROM employee);
# ALTER TABLE worker ADD FOREIGN KEY (ContactId) REFERENCES vacancy(global_id);
# SELECT * FROM worker;

# Создадим таблицу infoemployee с контактной информацией дальнейшая декомпозиция теряет смысл поиска контакта человека
# CREATE TABLE infoemployee (ContactName TEXT, FullName TEXT, Phone TEXT, Email TEXT);
# INSERT INTO infoemployee (SELECT DISTINCT ContactName, FullName, Phone, Email FROM employee);
# ALTER TABLE infoemployee ADD id INT(11) NOT NULL FIRST;
# ALTER TABLE infoemployee ADD INDEX (id);
# ALTER TABLE infoemployee CHANGE id id INT(11) NOT NULL AUTO_INCREMENT;
# SELECT * FROM infoemployee;

# Создадим таблицу dopinfo с информацией которая связывает global_id ваканссии с дополнительной информацией по вакансии
# CREATE TABLE dopinfo (VacancyId BIGINT, Date DATETIME, CountVacancy BIGINT, DopWorkersParameters TEXT);
# INSERT INTO dopinfo (SELECT global_id, Date, CountVacancy, DopWorkersParameters FROM employee);
# ALTER TABLE dopinfo ADD FOREIGN KEY (VacancyId) REFERENCES vacancy(global_id);
# SELECT * FROM dopinfo;

# Создадим таблицу address с информацией по расположению вакансии дальнейшая декомпозиция теряет смысл поиска адресса
# CREATE TABLE address (AddressId BIGINT, geoData TEXT, WorkPlaceAdmArea TEXT, WorkPlaceDistrict TEXT, WorkPlaceLocation TEXT);
# INSERT INTO address (SELECT global_id, geoData, WorkPlaceAdmArea, WorkPlaceDistrict, WorkPlaceLocation FROM employee);
# ALTER TABLE address ADD FOREIGN KEY (AddressId) REFERENCES vacancy(global_id);
# SELECT * FROM address;

# Для каждой вакансии рассмотрим требования
# CREATE TABLE education (global_id BIGINT, Education TEXT, Skills TEXT);
# INSERT INTO education (SELECT global_id, Education, Skills FROM employee);
# ALTER TABLE education ADD FOREIGN KEY (global_id) REFERENCES vacancy(global_id);
# SELECT * FROM education;

# Покажем отдельно какие виды образования можно выделить
# CREATE TABLE typeEducation (Education TEXT);
# INSERT INTO typeEducation (SELECT DISTINCT Education FROM employee);
# ALTER TABLE typeEducation ADD id INT(11) NOT NULL FIRST;
# ALTER TABLE typeEducation ADD INDEX (id);
# ALTER TABLE typeEducation CHANGE id id INT(11) NOT NULL AUTO_INCREMENT;
# SELECT * FROM typeEducation;

# Создадим таблицу vcondition условий вакансии
# CREATE TABLE vcondition (global_id BIGINT, SpecialWorkPlace TEXT, MinZarplat BIGINT, MaxZarplat BIGINT, WorkRegim TEXT, WorkOsob TEXT, WorkType TEXT);
# INSERT INTO vcondition (SELECT global_id, SpecialWorkPlace, MinZarplat, MaxZarplat, WorkRegim, WorkOsob, WorkType FROM employee);
# ALTER TABLE vcondition ADD FOREIGN KEY (global_id) REFERENCES vacancy(global_id);
# SELECT * FROM vcondition;


# Создадим таблицу по возожностям для инвалидов
# CREATE TABLE specwork(SpecialWorkPlace TEXT);
# INSERT INTO specwork(SELECT DISTINCT SpecialWorkPlace FROM employee);
# ALTER TABLE specwork ADD id INT(11) NOT NULL FIRST;
# ALTER TABLE specwork ADD INDEX (id);
# ALTER TABLE specwork CHANGE id id INT(11) NOT NULL AUTO_INCREMENT;
# SELECT * FROM specwork;

# Создадим таблицу по режиму работы
# CREATE TABLE regim (WorkRegim TEXT);
# INSERT INTO regim(SELECT DISTINCT WorkRegim FROM employee);
# ALTER TABLE regim ADD id INT(11) NOT NULL FIRST;
# ALTER TABLE regim ADD INDEX (id);
# ALTER TABLE regim CHANGE id id INT(11) NOT NULL AUTO_INCREMENT;
# SELECT * FROM regim;

# Создадим таблицу по особенностям работы
# CREATE TABLE workosob (WorkOsob TEXT);
# INSERT INTO workosob(SELECT DISTINCT WorkOsob FROM employee);
# ALTER TABLE workosob ADD id INT(11) NOT NULL FIRST;
# ALTER TABLE workosob ADD INDEX (id);
# ALTER TABLE workosob CHANGE id id INT(11) NOT NULL AUTO_INCREMENT;
# SELECT * FROM workosob;

# Создадим таблицу по типам работы
# CREATE TABLE worktype (WorkType TEXT);
# INSERT INTO worktype(SELECT DISTINCT WorkType FROM employee);
# ALTER TABLE worktype ADD id INT(11) NOT NULL FIRST;
# ALTER TABLE worktype ADD INDEX (id);
# ALTER TABLE worktype CHANGE id id INT(11) NOT NULL AUTO_INCREMENT;
# SELECT * FROM worktype;

# Если таблица исходная не нужна, то можно ее удалить
# DROP TABLE employee;



# Итоговый скрипт для MySQL:

# ALTER TABLE employee ADD PRIMARY KEY (global_id);
#
# CREATE TABLE vacancy (global_id BIGINT, Number TEXT, Prof TEXT, Specification TEXT, WorkFunction TEXT, CONSTRAINT global_id PRIMARY KEY (global_id));
# INSERT INTO vacancy (SELECT global_id, Number, Prof, Specification, WorkFunction FROM employee);
#
# CREATE TABLE worker (ContactId BIGINT, ContactName TEXT, ProfStage BIGINT);
# INSERT INTO worker (SELECT global_id, ContactName, ProfStage FROM employee);
# ALTER TABLE worker ADD FOREIGN KEY (ContactId) REFERENCES vacancy(global_id);
#
# CREATE TABLE infoemployee (ContactName TEXT, FullName TEXT, Phone TEXT, Email TEXT);
# INSERT INTO infoemployee (SELECT DISTINCT ContactName, FullName, Phone, Email FROM employee);
# ALTER TABLE infoemployee ADD id INT(11) NOT NULL FIRST;
# ALTER TABLE infoemployee ADD INDEX (id);
# ALTER TABLE infoemployee CHANGE id id INT(11) NOT NULL AUTO_INCREMENT;
#
# CREATE TABLE dopinfo (VacancyId BIGINT, Date DATETIME, CountVacancy BIGINT, DopWorkersParameters TEXT);
# INSERT INTO dopinfo (SELECT global_id, Date, CountVacancy, DopWorkersParameters FROM employee);
# ALTER TABLE dopinfo ADD FOREIGN KEY (VacancyId) REFERENCES vacancy(global_id);
#
# CREATE TABLE address (AddressId BIGINT, geoData TEXT, WorkPlaceAdmArea TEXT, WorkPlaceDistrict TEXT, WorkPlaceLocation TEXT);
# INSERT INTO address (SELECT global_id, geoData, WorkPlaceAdmArea, WorkPlaceDistrict, WorkPlaceLocation FROM employee);
# ALTER TABLE address ADD FOREIGN KEY (AddressId) REFERENCES vacancy(global_id);
#
# CREATE TABLE education (global_id BIGINT, Education TEXT, Skills TEXT);
# INSERT INTO education (SELECT global_id, Education, Skills FROM employee);
# ALTER TABLE education ADD FOREIGN KEY (global_id) REFERENCES vacancy(global_id);
#
# CREATE TABLE typeEducation (Education TEXT);
# INSERT INTO typeEducation (SELECT DISTINCT Education FROM employee);
# ALTER TABLE typeEducation ADD id INT(11) NOT NULL FIRST;
# ALTER TABLE typeEducation ADD INDEX (id);
# ALTER TABLE typeEducation CHANGE id id INT(11) NOT NULL AUTO_INCREMENT;
#
# CREATE TABLE vcondition (global_id BIGINT, SpecialWorkPlace TEXT, MinZarplat BIGINT, MaxZarplat BIGINT, WorkRegim TEXT, WorkOsob TEXT, WorkType TEXT);
# INSERT INTO vcondition (SELECT global_id, SpecialWorkPlace, MinZarplat, MaxZarplat, WorkRegim, WorkOsob, WorkType FROM employee);
# ALTER TABLE vcondition ADD FOREIGN KEY (global_id) REFERENCES vacancy(global_id);
#
# CREATE TABLE specwork(SpecialWorkPlace TEXT);
# INSERT INTO specwork(SELECT DISTINCT SpecialWorkPlace FROM employee);
# ALTER TABLE specwork ADD id INT(11) NOT NULL FIRST;
# ALTER TABLE specwork ADD INDEX (id);
# ALTER TABLE specwork CHANGE id id INT(11) NOT NULL AUTO_INCREMENT;
#
# CREATE TABLE regim (WorkRegim TEXT);
# INSERT INTO regim(SELECT DISTINCT WorkRegim FROM employee);
# ALTER TABLE regim ADD id INT(11) NOT NULL FIRST;
# ALTER TABLE regim ADD INDEX (id);
# ALTER TABLE regim CHANGE id id INT(11) NOT NULL AUTO_INCREMENT;
#
# CREATE TABLE workosob (WorkOsob TEXT);
# INSERT INTO workosob(SELECT DISTINCT WorkOsob FROM employee);
# ALTER TABLE workosob ADD id INT(11) NOT NULL FIRST;
# ALTER TABLE workosob ADD INDEX (id);
# ALTER TABLE workosob CHANGE id id INT(11) NOT NULL AUTO_INCREMENT;
#
# CREATE TABLE worktype (WorkType TEXT);
# INSERT INTO worktype(SELECT DISTINCT WorkType FROM employee);
# ALTER TABLE worktype ADD id INT(11) NOT NULL FIRST;
# ALTER TABLE worktype ADD INDEX (id);
# ALTER TABLE worktype CHANGE id id INT(11) NOT NULL AUTO_INCREMENT;

