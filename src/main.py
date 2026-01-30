from src.obj import Volante

button = {
    "START": 12,
    "EXIT": 5,
    "SETTINGS": 3,
    "UP": 0,
    "DOWN": 1,
    "SELECT": 4,
    "RETRO_ON": 9,
    "RETRO_OFF": 8
}

axis = {
    "STEERING": 0,
    "ACCELERATOR": 5,
    "BRAKE": 1
}

option = ["Regolazione massima velocità", "Regolazione angolo massimo sterzo"]

if __name__ == "__main__":
    app = Volante(button, axis, option)
    app.run()
