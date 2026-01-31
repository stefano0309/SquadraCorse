from src.obj import Volante
from src.utils import  *

path = "./config.json"
button = ["START", "EXIT", "SETTINGS", "UP", "DOWN", "SELECT", "RETRO_ON", "RETRO_OFF"]
axis = ["STEERING", "ACCELERATOR", "BRAKE"]
option = ["Regolazione massima velocità", "Regolazione angolo massimo sterzo"]

if __name__ == "__main__":
    buttonMap(button, axis, path)
    buttonMp, axisMp = loadMap(path)
    app = Volante(buttonMp, axisMp, option)
    app.run()