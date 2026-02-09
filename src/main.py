from src.objController import *
from src.objControllerDebug import *

if __name__ == "__main__":
    if input("Tipo di input:\n1. Volante\n2. Debug con tastiera\nSCELTA-> ") == 1:
        app = Controller()
        app.run()
    else:
        app = ControllerDebug()
        app.run()