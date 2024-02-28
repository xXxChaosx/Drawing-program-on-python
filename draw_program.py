from main import * #імпортує весь код з draw_program.py

if __name__ == "__main__":
    root = tk.Tk() #ініціалізується головне вікно root за допомогою tk.Tk()
    drawing_app = DrawingProgram(root) #створюється об'єкт класу DrawingProgram та передається головне вікно root в конструктор
    drawing_app.run() #викликається метод run для запуску програми