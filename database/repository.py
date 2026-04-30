import sqlite3
from models.car_models import Car, CombustionCar, ElectricCar

class CarRepository:
    def __init__(self, db_path: str = 'database/cars.db'):
       
        self._db_path = db_path

    def _row_to_object(self, row: tuple) -> Car:
        
        car_id, brand, model, year, price, body_type, fuel_type, eng_vol, fuel_cons, bat_cap, range_km, images_str = row

        images_list = images_str.split(',') if images_str else []

        if fuel_type == "Електро":
            return ElectricCar(brand, model, year, price, body_type, bat_cap, range_km, images=images_list)
        else:
            return CombustionCar(brand, model, year, price, body_type, fuel_type, eng_vol, fuel_cons, images=images_list)


    def find_cars(self, body_type: str, fuel_type: str, max_price: float) -> list[Car]:
        conn = sqlite3.connect(self._db_path)
        cursor = conn.cursor()

        query = "SELECT * FROM cars WHERE price <= ?"
        parameters = [max_price]

        if body_type != "Будь-який":
            query += " AND body_type = ?"
            parameters.append(body_type)

        if fuel_type != "Не має значення":
            query += " AND fuel_type = ?"
            parameters.append(fuel_type)

        cursor.execute(query, parameters)
        rows = cursor.fetchall()
        conn.close()

        result_objects = []
        for row in rows:
            car_obj = self._row_to_object(row)
            result_objects.append(car_obj)

        return result_objects
