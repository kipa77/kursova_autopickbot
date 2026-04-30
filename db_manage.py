import sqlite3

class DBManager:
    def __init__(self, db_path: str = 'database/cars.db'):
        self._db_path = db_path

    def add_car(self, brand: str, model: str, year: int, price: float, body_type: str, 
                fuel_type: str, engine_volume: float = None, fuel_consumption: float = None, 
                battery_capacity: int = None, range_km: int = None, images: str = None):
        
        conn = sqlite3.connect(self._db_path)
        cursor = conn.cursor()

        query = """
        INSERT INTO cars (
            brand, model, year, price, body_type, 
            fuel_type, engine_volume, fuel_consumption, 
            battery_capacity, range_km, images
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        try:
            cursor.execute(query, (
                brand, model, year, price, body_type, 
                fuel_type, engine_volume, fuel_consumption, 
                battery_capacity, range_km, images
            ))
            conn.commit()
            print(f" Автомобіль {brand} {model} успішно додано.")
        except sqlite3.Error as e:
            print(f" Помилка при додаванні: {e}")
        finally:
            conn.close()

    def delete_car_by_id(self, car_id: int):
        conn = sqlite3.connect(self._db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM cars WHERE id = ?", (car_id,))
            if cursor.rowcount > 0:
                conn.commit()
                print(f" Автомобіль з ID {car_id} видалено.")
            else:
                print(f" Автомобіль з ID {car_id} не знайдено.")
        except sqlite3.Error as e:
            print(f" Помилка при видаленні: {e}")
        finally:
            conn.close()

if __name__ == "__main__":
    manager = DBManager('database/cars.db')

    #manager.add_car("Volkswagen", "Golf", 2019, 18500, "Хетчбек", "Бензин", 1.4, 6.5,"https://bex-auto.com/storage/products/-dec2sqsS.jpg.webp,https://bex-auto.com/storage/products/-dec2sqsS.jpg.webp")

    #manager.add_car("Audi", "e-tron", 2021, 55000, "Позашляховик", "Електро", battery_capacity=95, range_km=400,"https://bex-auto.com/storage/products/-dec2sqsS.jpg.webp")

    print("Видалити авто? (y/n)")
    delcar = input().lower()
    if delcar == 'y':
        car_id_to_delete = int(input("Введіть ID для видалення: "))
        manager.delete_car_by_id(car_id_to_delete)
    
#database/db_manage.py
       