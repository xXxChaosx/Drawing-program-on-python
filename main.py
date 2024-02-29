from libraries import * #імпортує все необхідне для кода з файлу libraries.py

class DrawingProgram:
    def __init__(self, root):
        self.root = root #Ініціалізує головне вікно root
        self.root.title("Drawing program") #встановлює назву програми за допомогою root.title

        self.root.attributes("-fullscreen", True) #Встановлює режим повного екрану вікна за допомогою root.attributes
        self.canvas_width = self.root.winfo_screenwidth() #Визначає ширину полотна для малювання
        self.canvas_height = self.root.winfo_screenheight() #Визначає висоту полотна для малювання

        #Ініціалізація змінних для поточної кисті або інструмента:
        self.color = "black" #колір за замовчуванням
        self.brush_size = 5 #розмір за замовчуванням
        self.selected_tool = "pencil" #обраний інструмент за замовчуванням
        self.prev_x = None
        self.prev_y = None #тимчасові координати точки малювання
        self.temp_color_tag = None #тимчасовий тег для кольору, що вибирається піпеткою
        self.undo_list = [] #список останніх дій малювання для функції відміни
        self.root.after_id = None #ідентифікатор таймера для функції відміни при утриманні кнопки

        self.create_menu()
        self.create_canvas() #викликає create_menu та create_canvas для створення меню та полотна

    def create_menu(self):
        self.menu_frame = tk.Frame(self.root, bd=1, relief=tk.RAISED)
        self.menu_frame.pack(side=tk.TOP, fill=tk.X) #cтворює рамку меню menu_frame та розміщує її зверху вікна

        color_button = tk.Button(self.menu_frame, text="Select Color", command=self.choose_color)
        color_button.pack(side=tk.LEFT, padx=5, pady=5) #додає кнопку "Select Color", яка викликає метод choose_color для вибору кольору

        self.color_icon = tk.Label(self.menu_frame, width=10, height=1, bg=self.color)
        self.color_icon.pack(side=tk.LEFT, padx=5, pady=5) #створює іконку color_icon для відображення обраного кольору, додав для перевірки чи піпетка обрала колір

        size_slider = tk.Scale(self.menu_frame, from_=1, to=100, orient=tk.HORIZONTAL, label="Brush Size", command=self.set_brush_size)
        size_slider.set(self.brush_size)
        size_slider.pack(side=tk.LEFT, padx=5, pady=5) #додає повзунок size_slider для налаштування розміру інструмента та пов'язує його з методом set_brush_size

        pencil_button = tk.Button(self.menu_frame, text="Pencil", command=self.select_pencil)
        pencil_button.pack(side=tk.LEFT, padx=5, pady=5) #додає кнопку для олівця

        eraser_button = tk.Button(self.menu_frame, text="Eraser", command=self.select_eraser)
        eraser_button.pack(side=tk.LEFT, padx=5, pady=5) #додає кнопку для стрирачки

        pipette_button = tk.Button(self.menu_frame, text="Pipette", command=self.select_pipette)
        pipette_button.pack(side=tk.LEFT, padx=5, pady=5) #додає кнопку для піпетки

        fill_button = tk.Button(self.menu_frame, text="Fill background", command=self.select_fill)
        fill_button.pack(side=tk.LEFT, padx=5, pady=5) #додає кнопку для заливки фону

        clear_button = tk.Button(self.menu_frame, text="Clear Canvas", command=self.clear_canvas)
        clear_button.pack(side=tk.LEFT, padx=5, pady=5) #додає кнопку для очищення всього фону

        undo_button = tk.Button(self.menu_frame, text="Undo")
        undo_button.pack(side=tk.LEFT, padx=5, pady=5)
        undo_button.bind("<Control-z>", lambda event: self.undo_continuous(event, True))
        undo_button.bind("<ButtonPress-1>", lambda event: self.undo_continuous(event, True))
        undo_button.bind("<ButtonRelease-1>", lambda event: self.undo_continuous(event, False))
        #додає кнопку при натиснені якої відбувається відміна останьої дії, також можна зажати кнопку

        close_button = tk.Button(self.menu_frame, text="Exit", command=self.close_app)
        close_button.pack(side=tk.RIGHT, padx=5, pady=5) #додає кнопку для закриття програми яка викликає close_app

        save_button = tk.Button(self.menu_frame, text="Save as Image", command=self.save_canvas_as_image)
        save_button.pack(side=tk.LEFT, padx=5, pady=5) #додає кнопку для збереження малюнку, але зберігає фоно у вигляді малюнка

    def create_canvas(self): #створює полотно для малювання canvas з білим фоном, встановлює ширину та висоту.
        self.canvas = tk.Canvas(self.root, bg="white", width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack()

        self.canvas.bind("<B1-Motion>", self.paint) #рух миші з натиснутою лівою кнопкою - викликає paint для малювання
        self.canvas.bind("<ButtonRelease-1>", self.reset) #відпускання лівої кнопки миші - викликає reset для скидання змінних малювання

    def choose_color(self):
        self.color = colorchooser.askcolor()[1] #відкриває діалогове вікно вибору кольору
        self.color_icon.config(bg=self.color) #встановлює обраний колір та оновлює мітку color_icon

        if self.temp_color_tag:
            item, original_tags = self.temp_color_tag
            self.canvas.configure(item, tags=original_tags)
            self.temp_color_tag = None

    def set_brush_size(self, size):
        self.brush_size = int(size) #оновлює значення brush_size відповідно до значення повзунка

    def clear_canvas(self):
        self.canvas.delete("all") #очищує полотно

    def paint(self, event):
        x, y = event.x, event.y #отримує координати курсора миші x та y

        #Перевіряє обраний інструмент
        if self.selected_tool == "pencil": #
            if self.prev_x and self.prev_y: #перевіряє наявність попередніх координат prev_x та prev_y
                drawn_item = self.canvas.create_line(self.prev_x, self.prev_y, x, y, fill=self.color, width=self.brush_size, capstyle=tk.ROUND, smooth=tk.TRUE, tags=("color", self.color)) #якщо є попередні координати, створює лінію на полотні за допомогою canvas.create_line з обраним кольором, розміром кисті, округлену шапку та згладжування
            self.prev_x = x
            self.prev_y = y #задає нові знячення для x, y в залежності від того де зупинилося малювання лінії
            self.undo_list.append(drawn_item) #додає створений прямокутник до списку останніх дій undo_list
        elif self.selected_tool == "eraser":
            x1, y1 = (event.x - self.brush_size), (event.y - self.brush_size)
            x2, y2 = (event.x + self.brush_size), (event.y + self.brush_size) #Розраховує координати прямокутника гумки навколо курсора миші
            drawn_item = self.canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="white", tags=("eraser",)) #Створює білий непрозорий прямокутник на полотні за допомогою canvas.create_rectangle
            self.undo_list.append(drawn_item) #додає створений прямокутник до списку останніх дій undo_list
        elif self.selected_tool == "fill":
            drawn_item = self.canvas.create_rectangle(0, 0, self.canvas_width, self.canvas_height, fill=self.color, tags=("color", self.color)) #заповнює все полотно обраним кольором за допомогою canvas.create_rectangle
            self.undo_list.append(drawn_item) #додає створений прямокутник до списку останніх дій undo_list
        elif self.selected_tool == "pipette":
            self.add_color_tag(event) #викликає метод add_color_tag для отримання кольору з полотна

    def add_color_tag(self, event):
        item = self.canvas.find_closest(event.x, event.y) #знаходить найближчий об'єкт на полотні до курсора миші за допомогою canvas.find_closest
        tags = self.canvas.gettags(item) #отримує теги об'єкта за допомогою canvas.gettags

        self.color = tags[tags.index("color") + 1]
        self.color_icon.config(bg=self.color)

    def select_pencil(self):
        self.selected_tool = "pencil" #встановлює значення змінної selected_tool відповідно до обраного інструменту

    def select_eraser(self):
        self.selected_tool = "eraser" #встановлює значення змінної selected_tool відповідно до обраного інструменту
    
    def select_pipette(self):
        self.selected_tool = "pipette" #встановлює значення змінної selected_tool відповідно до обраного інструменту

    def select_fill(self):
        self.selected_tool = "fill" #встановлює значення змінної selected_tool відповідно до обраного інструменту

    def undo_continuous(self, event, continuous):
        if continuous:
            item = self.undo_list.pop() #видаляє останній елемент зі списку
            self.canvas.delete(item) #видаляє його з полотна за допомогою canvas.delete
            self.root.after_id = self.root.after(90, lambda: self.undo_continuous(event, True)) #Запускає таймер на 60 мілісекунд, який повторно викличе себе, якщо кнопка відміни все ще утримується. Чим менше мілісекунд, тим швидше йде відміна
        else:
            if self.root.after_id:
                self.root.after_cancel(self.root.after_id) #при відпусканні кнопки відміни зупиняє таймер, якщо він був запущений

    def reset(self, event):
        self.prev_x = None
        self.prev_y = None #скидає попередні координати малювання prev_x та prev_y, використовується в create_canvas
        
    def close_app(self):
        self.root.destroy() #закриває головне вікно програми з допомогою destroy
    
    def save_canvas_as_image(self):
        filename = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", ".png"), ("All files", "*")]) #відкриває діалогове вікно "Зберегти як" за допомогою filedialog.asksaveasfilename
        if filename:
            x = self.root.winfo_rootx() + self.canvas.winfo_x()
            y = self.root.winfo_rooty() + self.canvas.winfo_y() #якщо користувач вибрав назву файлу отримує координати вікна та полотна
            x1 = x + self.canvas.winfo_width()
            y1 = y + self.canvas.winfo_height() #розраховує координати області захоплення зображення
            ImageGrab.grab((x, y, x1, y1)).save(filename) #використовує ImageGrab.grab для захоплення зображення з екрану та зберігає обрізане зображення за допомогою save

    def run(self):
        self.root.mainloop() #запускає головний цикл обробки подій root.mainloop
