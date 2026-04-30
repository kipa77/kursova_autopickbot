from abc import ABC, abstractmethod

class Car(ABC):
    def __init__(self, brand: str, model: str, year: int, price: float, body_type: str, images: list = None):
        self._brand = brand
        self._model = model
        self._year = year
        self._price = price
        self._body_type = body_type
        self._images = images if images else []

    @property
    def brand(self) -> str:
        return self._brand

    @property
    def model(self) -> str:
        return self._model

    @property
    def year(self) -> int:
        return self._year

    @property
    def price(self) -> float:
        return self._price

    @property
    def body_type(self) -> str:
        return self._body_type

    @property
    def images(self) -> list:
        return self._images

    @property
    def main_image(self) -> str:
        return self._images[0] if self._images else "https://static.vecteezy.com/system/resources/previews/022/059/000/non_2x/no-image-available-icon-vector.jpg"

    @abstractmethod
    def get_full_info(self) -> str:
        pass

class CombustionCar(Car):
    def __init__(self, brand: str, model: str, year: int, price: float, body_type: str, fuel_type: str, engine_volume: float, fuel_consumption: float, images: list = None):
        super().__init__(brand, model, year, price, body_type, images)
        self._fuel_type = fuel_type
        self._engine_volume = engine_volume
        self._fuel_consumption = fuel_consumption

    @property
    def fuel_type(self)-> str:
        return self._fuel_type

    @property
    def fuel_consumption(self) -> float:
        return self._fuel_consumption

    def get_full_info(self):
        return (f"{self._brand} {self._model} ({self._year})\n"
                f"Кузов: {self._body_type} | Двигун: {self._fuel_type} {self._engine_volume}л\n"
                f"Витрата пального: {self._fuel_consumption} л/100 км\n"
                f"Ціна: ${self._price}")

class ElectricCar(Car):
    def __init__(self, brand: str, model: str, year: int, price: float, body_type: str, battery_capacity: int, range_km: int, images: list = None):
        super().__init__(brand, model, year, price, body_type, images)
        self._battery_capacity = battery_capacity
        self._range_km = range_km
        
        @property
        def fuel_type(self) -> str:
            return "Електро"

   
    def get_full_info(self) -> str:
        return (f"{self._brand} {self._model} ({self._year})\n"
                f"Кузов: {self._body_type} | Батарея: {self._battery_capacity} кВт⋅год | Запас ходу: {self._range_km} км\n"
                f"Ціна: ${self._price}")