from fastapi import FastAPI, Response
import sqlite3 as sq
from pydantic import BaseModel
from datetime import datetime as dt

#класс для заполнения в post запросе
class Shop(BaseModel):
    Name: str
    City: str
    Street: str
    House: int
    Open_Time: int
    Close_Time: int


app = FastAPI()


#Обработка Post запроса на запись магазина

@app.post("/shop/")
async def create_item(info: Shop):
    connection = sq.connect('Citys')
    cursor = connection.cursor()
    try:
        request_to_read_data = "SELECT Street.id, City.id FROM Street, City WHERE Street.Name = '" + info.Street + "'" \
                                "AND City.Name = '" + info.City + "'"
        cursor.execute(request_to_read_data)
        ids = cursor.fetchall()[0]
        print(ids[0])
        #вставка в Базуданных данные полученные от пользователся
        request_to_insert_data = "INSERT INTO Shop (Name, City, Street, House, Open_Time, Close_Time) VALUES (?, ?, ?, ?, ?, ?)"
        cursor.execute(request_to_insert_data, (info.Name, ids[0], ids[1],
                                                info.House, info.Open_Time, info.Close_Time,))
        connection.commit()
        #получение ид созданной записи
        cursor.execute("SELECT Shop.id FROM Shop WHERE Shop.Name = '" + info.Name + "' AND Shop.City = "+ str(ids[0]) +\
                       " AND Shop.Street = "+ str(ids[1]) + " AND Shop.House = " + str(info.House) +\
                       " AND Shop.Open_Time = "+ str(info.Open_Time) +" AND Shop.Close_Time = "+ str(info.Close_Time))
        data = cursor.fetchall()
        connection.commit()
        Response.status_code = 200
        return {"Received data": data}
    except Exception:
        Response.status_code = 400
        return {"message": "BAD_REQUEST"}

#Get запрос на получение всех городов
@app.get("/city/")
async def root():
    connection = sq.connect('Citys')
    cursor = connection.cursor()
    request_to_read_cities = "SELECT * FROM City"

    cursor.execute(request_to_read_cities)

    data = cursor.fetchall()
    connection.close()
    Response.status_code = 200
    return {"All Cities": data}

# Get запрос на получение всех улиц города где {city_id} ид города из которого нужно получить список улиц
@app.get("/city/{city_id}/street/")
async def root(city_id):
    connection = sq.connect('Citys')
    cursor = connection.cursor()
    request_to_read_street = "SELECT * FROM Street WHERE City_id = '" + city_id + "'"
    cursor.execute(request_to_read_street)
    data = cursor.fetchall()
    connection.close()
    Response.status_code = 200
    return {"All Streets": data}

# Get запрос на получение магазинов, присутствуют необязательные параметры фильтрации street, city, open=1/0
@app.get("/shop/")
async def root(street: str = '', city: str='', open: int=-1):
    connection = sq.connect('Citys')
    cursor = connection.cursor()
    current_time = str(dt.time(dt.now()).hour) + str(dt.time(dt.now()).minute)
    #очень кривая обработка всех возможных вариаций получения нужных данных по параметрам фильрации
    try:
        if open == 1:
            if street and city:
                request_to_read_shops = "SELECT Shop.id, Shop.Name, Shop.Open_Time , Shop.Close_Time, City.Name , Street.Name "\
                                        "FROM City, Shop, Street  WHERE " + current_time + " BETWEEN Open_Time AND Close_Time " \
                                        "AND Street.id = '" + street + "' AND City.id = '"+ city +"' " \
                                        "AND Shop.Street = '"+ street +"' AND Shop.City = '"+ city +"'"
            elif street:
                request_to_read_shops = "SELECT Shop.id, Shop.Name, Shop.Open_Time , Shop.Close_Time, City.Name , Street.Name " \
                                        "FROM City, Shop, Street  WHERE " + current_time + " BETWEEN Open_Time AND Close_Time " \
                                        "AND Street.id = '" + street + "' AND Shop.Street = '" + street + "' " \
                                        "AND Shop.City = City.id"
            elif city:
                request_to_read_shops = "SELECT Shop.id, Shop.Name, Shop.Open_Time , Shop.Close_Time, City.Name , Street.Name " \
                                        "FROM City, Shop, Street  WHERE " + current_time + " BETWEEN Open_Time AND Close_Time " \
                                        "AND City.id = '" + city + "' AND Shop.City = '" + city + "'"\
                                        "AND Shop.Street = Street.id"
            else:
                request_to_read_shops = "SELECT Shop.id, Shop.Name, Shop.Open_Time , Shop.Close_Time, City.Name, Street.Name "\
                                        "FROM City, Shop, Street WHERE " + current_time + " BETWEEN Open_Time AND Close_Time " \
                                        "AND Shop.Street = Street.id AND Shop.City = City.id"
        elif open == 0:
            if street and city:
                request_to_read_shops = "SELECT Shop.id, Shop.Name, Shop.Open_Time , Shop.Close_Time, City.Name , Street.Name "\
                                        "FROM City, Shop, Street WHERE " + current_time + " NOT BETWEEN Open_Time AND Close_Time " \
                                        "AND Street.id = '" + street + "' AND City.id = '"+ city +"' " \
                                        "AND Shop.Street = '"+ street +"' AND Shop.City = '"+ city +"'"
            elif street:
                request_to_read_shops = "SELECT Shop.id, Shop.Name, Shop.Open_Time , Shop.Close_Time, City.Name , Street.Name " \
                                        "FROM City, Shop, Street  WHERE " + current_time + " NOT BETWEEN Open_Time AND Close_Time " \
                                        "AND Street.id = '" + street + "' AND Shop.Street = '" + street + "' " \
                                        "AND Shop.City = City.id"
            elif city:
                request_to_read_shops = "SELECT Shop.id, Shop.Name, Shop.Open_Time , Shop.Close_Time, City.Name , Street.Name " \
                                        "FROM City, Shop, Street  WHERE " + current_time + " NOT BETWEEN Open_Time AND Close_Time " \
                                        "AND City.id = '" + city + "' AND Shop.City = '" + city + "'"\
                                        "AND Shop.Street = Street.id"
            else:
                request_to_read_shops = "SELECT Shop.id, Shop.Name, Shop.Open_Time , Shop.Close_Time, City.Name, Street.Name "\
                                        "FROM City, Shop, Street WHERE " + current_time + " NOT BETWEEN Open_Time AND Close_Time " \
                                        "AND Shop.Street = Street.id AND Shop.City = City.id"
        else:
            if street and city:
                request_to_read_shops = "SELECT Shop.id, Shop.Name, Shop.Open_Time , Shop.Close_Time, City.Name , Street.Name "\
                                        "FROM City, Shop, Street WHERE Street.id = '" + street + "' AND City.id = '" + city +"' " \
                                        "AND Shop.Street = '" + street + "' AND Shop.City = '" + city + "'"
            elif street:
                request_to_read_shops = "SELECT Shop.id, Shop.Name, Shop.Open_Time , Shop.Close_Time, City.Name , Street.Name " \
                                        "FROM City, Shop, Street  WHERE Street.id = '" + street + "' AND Shop.Street = '" + street + "' " \
                                        "AND Shop.City = City.id"
            elif city:
                request_to_read_shops = "SELECT Shop.id, Shop.Name, Shop.Open_Time , Shop.Close_Time, City.Name , Street.Name " \
                                        "FROM City, Shop, Street  WHERE City.id = '" + city + "' AND Shop.City = '" + city + "'"\
                                        "AND Shop.Street = Street.id"
            else:
                request_to_read_shops = "SELECT Shop.id, Shop.Name, Shop.Open_Time , Shop.Close_Time, City.Name, Street.Name " \
                                        "FROM City, Shop, Street WHERE  Shop.Street = Street.id AND Shop.City = City.id"

        cursor.execute(request_to_read_shops)
        data = cursor.fetchall()
        connection.close()
        Response.status_code = 200
        return {"Shops": data}
    except Exception:
        Response.status_code=400
        return {"message": "BAD_REQUEST"}
