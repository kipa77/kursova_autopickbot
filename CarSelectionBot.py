from models.car_models import *
from database.repository import CarRepository

if __name__ == "__main__":
    repo = CarRepository('database/cars.db')

    target_body = "Седан"    #Будь-який         
    target_fuel = "Не має значення"   #Не має значення      
    limit_price = 50000             
 

    print(f"ПОШУК: {target_body} , {target_fuel} , до ${limit_price}")

    results = repo.find_cars(target_body, target_fuel, limit_price)

    if not results:
        print("Нічого не знайдено за такими критеріями.")
    else:
        print(f"Знайдено варіантів: {len(results)}\n")
        
        for item, car in enumerate(results, 1):
            print(f"Варіант {item}")
            print(car.get_full_info())
            print("-" * 30)


#CarSelectionBot.py