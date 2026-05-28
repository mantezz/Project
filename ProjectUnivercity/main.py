# main_gui.py
import os
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from datetime import datetime
from typing import List, Optional
import hashlib
import threading
from PIL import Image, ImageTk

class Message:
    """Класс для хранения сообщения в чате"""

    def __init__(self, role: str, content: str, timestamp: datetime = None,
                 file_path: str = None, image_path: str = None):
        self.role = role
        self.content = content
        self.timestamp = timestamp or datetime.now()
        self.file_path = file_path
        self.image_path = image_path

    def to_dict(self) -> dict:
        return {
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'file_path': self.file_path,
            'image_path': self.image_path
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            role=data['role'],
            content=data['content'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            file_path=data.get('file_path'),
            image_path=data.get('image_path')
        )


class Chat:
    """Класс для управления отдельным чатом"""

    def __init__(self, chat_id: str, name: str, subject: str, created_at: datetime = None):
        self.chat_id = chat_id
        self.name = name
        self.subject = subject
        self.created_at = created_at or datetime.now()
        self.messages: List[Message] = []

    def add_message(self, message: Message):
        self.messages.append(message)

    def get_messages(self) -> List[Message]:
        return self.messages

    def to_dict(self) -> dict:
        return {
            'chat_id': self.chat_id,
            'name': self.name,
            'subject': self.subject,
            'created_at': self.created_at.isoformat(),
            'messages': [msg.to_dict() for msg in self.messages]
        }

    @classmethod
    def from_dict(cls, data: dict):
        chat = cls(
            chat_id=data['chat_id'],
            name=data['name'],
            subject=data['subject'],
            created_at=datetime.fromisoformat(data['created_at'])
        )
        for msg_data in data.get('messages', []):
            chat.add_message(Message.from_dict(msg_data))
        return chat


class AIAssistant:
    """Класс для AI помощника"""

    @staticmethod
    def get_response(message: str, context: List[Message] = None) -> str:
        """
        Заглушка для ответа AI.
        Здесь можно подключить DeepSeek API
        """
        import time
        time.sleep(1)  # Имитация задержки ответа

        if "привет" in message.lower():
            return "Привет! Я твой помощник по математическому анализу. Чем могу помочь?"
        elif "производная" in message.lower():
            return "Производная функции показывает скорость её изменения.\n\n📌 Пример: производная x² = 2x\n📌 Правила: (u+v)' = u' + v'\n📌 (uv)' = u'v + uv'"
        elif "интеграл" in message.lower():
            return "Интеграл — это площадь под кривой.\n\n📌 Неопределённый интеграл: ∫xⁿ dx = xⁿ⁺¹/(n+1) + C\n📌 Определённый интеграл: ∫ₐᵇ f(x)dx = F(b) - F(a)"
        elif "предел" in message.lower():
            return "Предел функции — это значение, к которому стремится функция.\n\n📌 Пример: lim(x→0) sin(x)/x = 1"
        else:
            return f"📚 По вопросу '{message}':\n\nРекомендую обратиться к учебнику или задать более конкретный вопрос. Я помогу с примерами и объяснениями!"

    @staticmethod
    def process_file(file_path: str) -> str:
        """Обработка загруженного файла"""
        file_ext = os.path.splitext(file_path)[1].lower()

        if file_ext == '.txt':
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()[:500]  # Читаем первые 500 символов
                return f"📄 Прочитан файл {os.path.basename(file_path)}:\n\n{content}\n\n... (файл обработан, можно задать вопросы по содержимому)"
            except:
                return f"❌ Не удалось прочитать файл {os.path.basename(file_path)}"
        else:
            return f"📎 Файл {os.path.basename(file_path)} получен. В разработке: анализ PDF, DOCX и других форматов."


class Storage:
    """Класс для хранения данных"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.chats_dir = os.path.join(data_dir, "chats")
        os.makedirs(self.chats_dir, exist_ok=True)

    def save_chat(self, chat: Chat):
        """Сохранить чат в файл"""
        chat_file = os.path.join(self.chats_dir, f"{chat.chat_id}.json")
        with open(chat_file, 'w', encoding='utf-8') as f:
            json.dump(chat.to_dict(), f, ensure_ascii=False, indent=2)

    def load_chat(self, chat_id: str) -> Optional[Chat]:
        """Загрузить чат из файла"""
        chat_file = os.path.join(self.chats_dir, f"{chat_id}.json")
        if os.path.exists(chat_file):
            with open(chat_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return Chat.from_dict(data)
        return None

    def load_all_chats(self, subject: str) -> List[Chat]:
        """Загрузить все чаты по предмету"""
        chats = []
        for filename in os.listdir(self.chats_dir):
            if filename.endswith('.json'):
                chat = self.load_chat(filename[:-5])
                if chat and chat.subject == subject:
                    chats.append(chat)
        return sorted(chats, key=lambda x: x.created_at, reverse=True)

    def delete_chat(self, chat_id: str):
        """Удалить чат"""
        chat_file = os.path.join(self.chats_dir, f"{chat_id}.json")
        if os.path.exists(chat_file):
            os.remove(chat_file)


class ChatBubble(tk.Frame):
    """Виджет для отображения сообщения в виде пузырька"""

    def __init__(self, parent, message: Message, **kwargs):
        super().__init__(parent, **kwargs)

        self.configure(bg=parent.cget('bg'))

        # Цвета в стиле DeepSeek
        if message.role == "user":
            bubble_color = "#E8F2FF"  # Светло-синий для пользователя
            align = "e"
        else:
            bubble_color = "#FFFFFF"  # Белый для AI
            align = "w"

        # Контейнер для сообщения (с закруглениями)
        self.bubble = tk.Frame(self, bg=bubble_color, bd=0, relief=tk.FLAT)
        self.bubble.pack(fill=tk.X, padx=10, pady=5, anchor=align)

        # Создаём canvas для закруглённых углов
        self.canvas = tk.Canvas(self.bubble, bg=bubble_color, highlightthickness=0, height=1)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Внутренний контент
        content_frame = tk.Frame(self.canvas, bg=bubble_color)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)

        # Верхняя строка: время и иконка
        top_frame = tk.Frame(content_frame, bg=bubble_color)
        top_frame.pack(fill=tk.X, pady=(0, 5))

        # Иконка роли
        role_icon = "👤" if message.role == "user" else "🤖"
        tk.Label(top_frame, text=f"{role_icon} {message.role.upper()}",
                 font=("Arial", 9, "bold"), bg=bubble_color, fg="#4A5B6E").pack(side=tk.LEFT)

        # Время сообщения
        time_str = message.timestamp.strftime("%H:%M")
        tk.Label(top_frame, text=time_str, font=("Arial", 8),
                 bg=bubble_color, fg="#8A99B0").pack(side=tk.RIGHT)

        # Текст сообщения
        text_widget = tk.Text(content_frame, wrap=tk.WORD, bg=bubble_color,
                              font=("Arial", 10), height=1, padx=0, pady=0,
                              relief=tk.FLAT, borderwidth=0, fg="#1F2A3E")
        text_widget.insert("1.0", message.content)
        text_widget.configure(state="disabled")
        text_widget.pack(fill=tk.X, pady=(0, 5))

        # Если есть файл или изображение
        if message.file_path:
            file_frame = tk.Frame(content_frame, bg=bubble_color)
            file_frame.pack(fill=tk.X)
            tk.Label(file_frame, text=f"📎 {os.path.basename(message.file_path)}",
                     bg=bubble_color, font=("Arial", 9), fg="#0066CC").pack(side=tk.LEFT)

        if message.image_path:
            image_frame = tk.Frame(content_frame, bg=bubble_color)
            image_frame.pack(fill=tk.X)
            tk.Label(image_frame, text=f"🖼️ {os.path.basename(message.image_path)}",
                     bg=bubble_color, font=("Arial", 9), fg="#0066CC").pack(side=tk.LEFT)

        # Обновляем высоту
        self.update_text_height(text_widget)

        # Применяем закругления
        self.bubble.after(10, self.apply_rounded_corners)

    def apply_rounded_corners(self):
        """Применяет закругления к пузырьку"""
        width = self.bubble.winfo_width()
        height = self.bubble.winfo_height()
        if width > 10 and height > 10:
            self.canvas.delete("rounded")
            self.canvas.config(width=width, height=height)
            r = 12
            points = []
            for x, y in [(r, 0), (width - r, 0), (width, 0), (width, r),
                         (width, height - r), (width, height), (width - r, height),
                         (r, height), (0, height), (0, height - r),
                         (0, r), (0, 0)]:
                points.extend([x, y])
            self.canvas.create_polygon(points, fill=self.bubble.cget('bg'),
                                       outline="", tags="rounded")
            self.canvas.lower("rounded")

    def update_text_height(self, text_widget):
        """Обновление высоты текстового поля"""
        lines = int(text_widget.index('end-1c').split('.')[0])
        if lines < 1:
            lines = 1
        elif lines > 15:
            lines = 15
        text_widget.configure(height=lines)

class ChatApplication:
    """Главное приложение с GUI"""

    def __init__(self, root):
        self.root = root
        self.root.title("AI Учебный Помощник")
        self.root.geometry("1200x700")

        # Настройка стилей
        self.setup_styles()

        # Инициализация
        self.storage = Storage()
        self.ai = AIAssistant()
        self.current_subject = None
        self.current_chat = None

        # Словарь для виджетов чатов
        self.chat_buttons = {}

        # Создаем интерфейс
        self.setup_ui()

        # Показываем главное меню
        self.show_subjects()

    def setup_styles(self):
        """Настройка цветовой схемы (светлая тема как у DeepSeek)"""
        self.colors = {
            'bg': "#F7F8FA",  # Светлый фон как у DeepSeek
            'sidebar': "#FFFFFF",  # Белая боковая панель
            'card': "#FFFFFF",  # Белый цвет карточек (добавлено!)
            'accent': "#0066CC",  # Синий акцент как у DeepSeek
            'accent_hover': "#0052A3",  # Тёмно-синий при наведении
            'hover': "#F0F2F5",  # Светло-серый при наведении
            'text': "#1F2A3E",  # Тёмно-синий текст
            'text_light': "#5C6B7E",  # Серый текст
            'text_muted': "#8A99B0",  # Светло-серый текст
            'border': "#E4E7EB",  # Цвет границ
            'divider': "#E4E7EB",  # Цвет разделителей
            'input_bg': "#FFFFFF",  # Белый фон поля ввода
            'input_text': "#1F2A3E",  # Цвет текста в поле ввода
            'card_border': "#D1D5DB"  # Цвет границы карточек
        }
        self.root.configure(bg=self.colors['bg'])

    def setup_ui(self):
        """Настройка основного интерфейса"""
        # Основной контейнер
        self.main_container = tk.Frame(self.root, bg=self.colors['bg'])
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Боковая панель для чатов с рамкой
        self.sidebar = tk.Frame(self.main_container, bg=self.colors['sidebar'], width=280,
                                highlightthickness=1, highlightbackground=self.colors['divider'])
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 0))
        self.sidebar.pack_propagate(False)

        # Вертикальный разделитель (линия между сайдбаром и чатом)
        self.divider = tk.Frame(self.main_container, bg=self.colors['divider'], width=1)
        self.divider.pack(side=tk.LEFT, fill=tk.Y, padx=0)

        # Заголовок боковой панели с нижней границей
        sidebar_header = tk.Frame(self.sidebar, bg=self.colors['sidebar'])
        sidebar_header.pack(fill=tk.X)

        self.sidebar_title = tk.Label(sidebar_header, text="Список чатов",
                                      bg=self.colors['sidebar'], fg=self.colors['text'],
                                      font=("Arial", 14, "bold"), pady=15)
        self.sidebar_title.pack()

        # Нижняя граница под заголовком
        tk.Frame(sidebar_header, bg=self.colors['divider'], height=1).pack(fill=tk.X, padx=0)

        # Кнопка создания нового чата с рамкой
        self.new_chat_btn = tk.Button(self.sidebar, text="+ Создать новый чат",
                                      bg=self.colors['accent'], fg="white",
                                      font=("Arial", 10, "bold"), pady=8,
                                      command=self.create_new_chat,
                                      relief=tk.FLAT, cursor="hand2",
                                      activebackground=self.colors['accent_hover'],
                                      bd=0)
        self.new_chat_btn.pack(fill=tk.X, padx=15, pady=(15, 15))

        # Контейнер для списка чатов
        self.chats_frame = tk.Frame(self.sidebar, bg=self.colors['sidebar'])
        self.chats_frame.pack(fill=tk.BOTH, expand=True)

        # Canvas для скроллинга чатов
        self.chats_canvas = tk.Canvas(self.chats_frame, bg=self.colors['sidebar'], highlightthickness=0)
        self.chats_scrollbar = tk.Scrollbar(self.chats_frame, orient="vertical", command=self.chats_canvas.yview)
        self.chats_scrollable_frame = tk.Frame(self.chats_canvas, bg=self.colors['sidebar'])

        self.chats_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.chats_canvas.configure(scrollregion=self.chats_canvas.bbox("all"))
        )

        self.chats_canvas.create_window((0, 0), window=self.chats_scrollable_frame, anchor="nw")
        self.chats_canvas.configure(yscrollcommand=self.chats_scrollbar.set)

        self.chats_canvas.pack(side="left", fill="both", expand=True)
        self.chats_scrollbar.pack(side="right", fill="y")

        # Основная область чата с рамкой
        self.chat_area = tk.Frame(self.main_container, bg=self.colors['bg'],
                                  highlightthickness=0)
        self.chat_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Верхняя панель чата с нижней границей
        self.chat_header = tk.Frame(self.chat_area, bg=self.colors['sidebar'], height=60)
        self.chat_header.pack(fill=tk.X)

        # Нижняя граница хедера
        tk.Frame(self.chat_header, bg=self.colors['divider'], height=1).pack(side=tk.BOTTOM, fill=tk.X)

        self.chat_title = tk.Label(self.chat_header, text="Добро пожаловать!",
                                   bg=self.colors['sidebar'], fg=self.colors['text'],
                                   font=("Arial", 16, "bold"))
        self.chat_title.pack(side=tk.LEFT, padx=20, pady=15)

        # Кнопки управления чатом
        btn_style = {"bg": self.colors['sidebar'], "fg": self.colors['text_light'],
                     "font": ("Arial", 9), "relief": tk.FLAT, "cursor": "hand2",
                     "activebackground": self.colors['hover']}

        self.rename_chat_btn = tk.Button(self.chat_header, text="✏️ Переименовать",
                                         **btn_style, command=self.rename_chat)
        self.rename_chat_btn.pack(side=tk.RIGHT, padx=5, pady=15)

        self.delete_chat_btn = tk.Button(self.chat_header, text="🗑️ Удалить чат",
                                         **btn_style, command=self.delete_chat)
        self.delete_chat_btn.pack(side=tk.RIGHT, padx=5, pady=15)

        self.back_btn = tk.Button(self.chat_header, text="← Назад к предметам",
                                  **btn_style, command=self.back_to_subjects)
        self.back_btn.pack(side=tk.RIGHT, padx=5, pady=15)

        # Область сообщений
        self.messages_container = tk.Frame(self.chat_area, bg=self.colors['bg'])
        self.messages_container.pack(fill=tk.BOTH, expand=True)

        self.messages_canvas = tk.Canvas(self.messages_container, bg=self.colors['bg'], highlightthickness=0)
        self.messages_scrollbar = tk.Scrollbar(self.messages_container, orient="vertical",
                                               command=self.messages_canvas.yview)
        self.messages_frame = tk.Frame(self.messages_canvas, bg=self.colors['bg'])

        self.messages_frame.bind(
            "<Configure>",
            lambda e: self.messages_canvas.configure(scrollregion=self.messages_canvas.bbox("all"))
        )

        self.messages_canvas.create_window((0, 0), window=self.messages_frame, anchor="nw")
        self.messages_canvas.configure(yscrollcommand=self.messages_scrollbar.set)

        self.messages_canvas.pack(side="left", fill="both", expand=True)
        self.messages_scrollbar.pack(side="right", fill="y")

        # Область ввода с верхней границей
        self.input_frame = tk.Frame(self.chat_area, bg=self.colors['sidebar'])

        # Верхняя граница области ввода
        tk.Frame(self.input_frame, bg=self.colors['divider'], height=1).pack(side=tk.TOP, fill=tk.X)

        # Кнопки для файлов
        self.buttons_frame = tk.Frame(self.input_frame, bg=self.colors['sidebar'])
        self.buttons_frame.pack(fill=tk.X, padx=15, pady=(10, 5))

        file_btn_style = {"bg": self.colors['accent'], "fg": "white",
                          "font": ("Arial", 9), "relief": tk.FLAT, "cursor": "hand2",
                          "activebackground": self.colors['accent_hover']}

        self.file_btn = tk.Button(self.buttons_frame, text="📎 Прикрепить файл",
                                  command=self.attach_file, **file_btn_style)
        self.file_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.image_btn = tk.Button(self.buttons_frame, text="🖼️ Добавить изображение",
                                   command=self.attach_image, **file_btn_style)
        self.image_btn.pack(side=tk.LEFT)

        # Поле ввода текста с рамкой
        input_container = tk.Frame(self.input_frame, bg=self.colors['input_bg'],
                                   bd=1, relief=tk.SOLID)
        input_container.pack(fill=tk.X, padx=15, pady=(5, 10))
        input_container.config(highlightbackground=self.colors['card_border'],
                               highlightcolor=self.colors['accent'],
                               highlightthickness=1)

        self.input_text = tk.Text(input_container, height=3, font=("Arial", 10),
                                  bg=self.colors['input_bg'], fg=self.colors['text'],
                                  insertbackground=self.colors['text'],
                                  relief=tk.FLAT, bd=0, padx=10, pady=8)
        self.input_text.pack(fill=tk.BOTH, expand=True)

        # Кнопка отправки
        self.send_btn = tk.Button(self.input_frame, text="Отправить",
                                  bg=self.colors['accent'], fg="white",
                                  font=("Arial", 10, "bold"), command=self.send_message,
                                  relief=tk.FLAT, cursor="hand2",
                                  activebackground=self.colors['accent_hover'])
        self.send_btn.pack(pady=(0, 15), padx=15, fill=tk.X)

        # Привязываем Enter к отправке
        self.input_text.bind("<Control-Return>", lambda e: self.send_message())

        # Скрываем элементы управления чатом, пока чат не выбран
        self.toggle_chat_controls(False)
        # Изначально скрываем панель ввода
        self.input_frame.pack_forget()

    def toggle_chat_controls(self, show):
        """Показать/скрыть элементы управления чатом"""
        state = "normal" if show else "disabled"
        self.rename_chat_btn.configure(state=state)
        self.delete_chat_btn.configure(state=state)
        self.file_btn.configure(state=state)
        self.image_btn.configure(state=state)
        self.send_btn.configure(state=state)

        if show:
            # Показываем панель ввода
            self.input_frame.pack(fill=tk.X, side=tk.BOTTOM)
            self.input_text.configure(state="normal", bg=self.colors['input_bg'])
        else:
            # Скрываем панель ввода
            self.input_frame.pack_forget()
            self.input_text.configure(state="disabled", bg="#F0F2F5")

    def show_subjects(self):
        """Показать выбор предметов"""
        # Очищаем основную область
        for widget in self.messages_frame.winfo_children():
            widget.destroy()

        # Скрываем панель ввода
        self.input_frame.pack_forget()

        # Создаём плашки предметов
        subjects_frame = tk.Frame(self.messages_frame, bg=self.colors['bg'])
        subjects_frame.pack(expand=True)

        # Заголовок
        title = tk.Label(subjects_frame, text="Выберите предмет",
                         bg=self.colors['bg'], fg=self.colors['text'],
                         font=("Arial", 24, "bold"))
        title.pack(pady=50)

        # Плашки предметов
        subjects = [
            ("📐 Математический анализ", "matan", True),
            ("📊 Линейная алгебра", "algebra", False),
            ("💻 Программирование", "programming", False),
            ("⚛️ Физика", "physics", False)
        ]

        for name, subject_id, available in subjects:
            # Карточка с рамкой и тенью
            card_frame = tk.Frame(subjects_frame, bg=self.colors['bg'])
            card_frame.pack(pady=8, padx=20, fill=tk.X)

            # Основная рамка карточки
            frame = tk.Frame(card_frame, bg=self.colors['card'],
                             relief=tk.RAISED, bd=0,
                             highlightthickness=1,
                             highlightbackground=self.colors['card_border'],
                             highlightcolor=self.colors['accent'])
            frame.pack(fill=tk.X)

            btn_text = name
            if not available:
                btn_text += " (В разработке)"

            btn = tk.Button(frame, text=btn_text,
                            bg=self.colors['card'], fg=self.colors['text'],
                            font=("Arial", 13), pady=18,
                            relief=tk.FLAT, cursor="hand2",
                            activebackground=self.colors['hover'],
                            command=lambda s=subject_id, a=available: self.select_subject(s, a),
                            bd=0)
            btn.pack(fill=tk.X, padx=20)

        # Очищаем боковую панель
        for widget in self.chats_scrollable_frame.winfo_children():
            widget.destroy()
        self.chat_buttons.clear()

        # Скрываем элементы управления
        self.toggle_chat_controls(False)
        self.chat_title.configure(text="Добро пожаловать!")

    def select_subject(self, subject_id, available):
        """Выбор предмета"""
        if not available:
            messagebox.showinfo("В разработке", "Этот предмет пока в разработке!")
            return

        subject_names = {
            "matan": "Математический анализ",
            "algebra": "Линейная алгебра",
            "programming": "Программирование",
            "physics": "Физика"
        }

        self.current_subject = subject_names.get(subject_id, subject_id)
        self.load_chats_list()

    def load_chats_list(self):
        """Загрузить список чатов для текущего предмета"""
        # Очищаем текущий список
        for widget in self.chats_scrollable_frame.winfo_children():
            widget.destroy()
        self.chat_buttons.clear()

        # Скрываем панель ввода
        self.input_frame.pack_forget()

        # Загружаем чаты
        chats = self.storage.load_all_chats(self.current_subject)

        for chat in chats:
            self.add_chat_button(chat)

        # Показываем приветственное сообщение, если чатов нет
        if not chats:
            for widget in self.messages_frame.winfo_children():
                widget.destroy()

            welcome_icon = tk.Label(self.messages_frame, text="💬",
                                    bg=self.colors['bg'], fg=self.colors['accent'],
                                    font=("Arial", 48))
            welcome_icon.pack(expand=True, pady=(100, 10))

            welcome_label = tk.Label(self.messages_frame,
                                     text=f"Добро пожаловать в {self.current_subject}!\n\nСоздайте новый чат, чтобы начать обучение с AI помощником.",
                                     bg=self.colors['bg'], fg=self.colors['text_light'],
                                     font=("Arial", 12), justify=tk.CENTER)
            welcome_label.pack()

        self.chat_title.configure(text=self.current_subject)

    def add_chat_button(self, chat: Chat):
        """Добавить кнопку чата в боковую панель"""
        btn_frame = tk.Frame(self.chats_scrollable_frame, bg=self.colors['sidebar'])
        btn_frame.pack(fill=tk.X, padx=10, pady=2)

        # Рамка вокруг кнопки чата
        btn_container = tk.Frame(btn_frame, bg=self.colors['sidebar'],
                                 highlightthickness=1,
                                 highlightbackground=self.colors['border'],
                                 highlightcolor=self.colors['accent'])
        btn_container.pack(fill=tk.X, pady=2)

        btn = tk.Button(btn_container, text=f"💬 {chat.name}\n📝 {len(chat.messages)} сообщ.",
                        bg=self.colors['sidebar'], fg=self.colors['text'],
                        font=("Arial", 9), anchor="w", justify=tk.LEFT,
                        relief=tk.FLAT, cursor="hand2",
                        activebackground=self.colors['hover'],
                        command=lambda c=chat: self.open_chat(c),
                        bd=0, padx=10, pady=8)
        btn.pack(fill=tk.X)

        self.chat_buttons[chat.chat_id] = (btn_container, btn)

    def create_new_chat(self):
        """Создание нового чата"""
        if not self.current_subject:
            messagebox.showwarning("Ошибка", "Сначала выберите предмет!")
            return

        name = simpledialog.askstring("Новый чат", "Введите название чата:",
                                      parent=self.root)

        if name is None:
            return

        if not name.strip():
            name = f"Чат {datetime.now().strftime('%d.%m %H:%M')}"

        chat_id = hashlib.md5(f"{self.current_subject}{datetime.now()}".encode()).hexdigest()[:8]
        chat = Chat(chat_id, name.strip(), self.current_subject)
        self.storage.save_chat(chat)

        self.add_chat_button(chat)
        self.open_chat(chat)

    def open_chat(self, chat: Chat):
        """Открыть чат"""
        self.current_chat = chat

        # Загружаем сообщения
        self.load_messages()

        # Показываем элементы управления
        self.toggle_chat_controls(True)
        self.chat_title.configure(text=chat.name)

        # Обновляем активную кнопку в боковой панели
        for chat_id, (container, btn) in self.chat_buttons.items():
            if chat_id == chat.chat_id:
                container.config(highlightbackground=self.colors['accent'])
                btn.configure(bg=self.colors['hover'])
            else:
                container.config(highlightbackground=self.colors['border'])
                btn.configure(bg=self.colors['sidebar'])

    def load_messages(self):
        """Загрузить сообщения в чат"""
        # Очищаем область сообщений
        for widget in self.messages_frame.winfo_children():
            widget.destroy()

        if not self.current_chat:
            return

        # Добавляем все сообщения
        for msg in self.current_chat.get_messages():
            bubble = ChatBubble(self.messages_frame, msg)
            bubble.pack(fill=tk.X, pady=2)

        # Прокручиваем вниз
        self.root.update_idletasks()
        self.messages_canvas.yview_moveto(1.0)

    def send_message(self):
        """Отправка сообщения"""
        if not self.current_chat:
            messagebox.showwarning("Ошибка", "Сначала выберите или создайте чат!")
            return

        message = self.input_text.get("1.0", tk.END).strip()
        if not message:
            return

        # Очищаем поле ввода
        self.input_text.delete("1.0", tk.END)

        # Добавляем сообщение пользователя
        user_msg = Message("user", message)
        self.current_chat.add_message(user_msg)
        self.storage.save_chat(self.current_chat)

        # Обновляем отображение
        self.load_messages()

        # Блокируем интерфейс на время ответа AI
        self.send_btn.configure(state="disabled", text="AI думает...")
        self.root.update()

        # Получаем ответ AI в отдельном потоке
        def get_ai_response():
            response = self.ai.get_response(message)

            # Добавляем ответ AI
            ai_msg = Message("assistant", response)
            self.current_chat.add_message(ai_msg)
            self.storage.save_chat(self.current_chat)

            # Обновляем UI в основном потоке
            self.root.after(0, self.on_ai_response)

        threading.Thread(target=get_ai_response, daemon=True).start()

    def on_ai_response(self):
        """Обработка ответа AI"""
        self.load_messages()
        self.send_btn.configure(state="normal", text="Отправить")

        # Обновляем кнопку чата в боковой панели
        if self.current_chat and self.current_chat.chat_id in self.chat_buttons:
            frame, btn = self.chat_buttons[self.current_chat.chat_id]
            btn.configure(text=f"💬 {self.current_chat.name}\n({len(self.current_chat.messages)} сообщ.)")

    def attach_file(self):
        """Прикрепить файл"""
        if not self.current_chat:
            messagebox.showwarning("Ошибка", "Сначала выберите или создайте чат!")
            return

        file_path = filedialog.askopenfilename(title="Выберите файл")
        if file_path:
            # Добавляем сообщение о файле
            user_msg = Message("user", f"📎 Отправлен файл: {os.path.basename(file_path)}",
                               file_path=file_path)
            self.current_chat.add_message(user_msg)

            # Обрабатываем файл
            response = self.ai.process_file(file_path)
            ai_msg = Message("assistant", response)
            self.current_chat.add_message(ai_msg)

            self.storage.save_chat(self.current_chat)
            self.load_messages()

    def attach_image(self):
        """Прикрепить изображение"""
        if not self.current_chat:
            messagebox.showwarning("Ошибка", "Сначала выберите или создайте чат!")
            return

        image_path = filedialog.askopenfilename(title="Выберите изображение",
                                                filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif")])
        if image_path:
            user_msg = Message("user", f"🖼️ Отправлено изображение: {os.path.basename(image_path)}",
                               image_path=image_path)
            self.current_chat.add_message(user_msg)

            response = f"Изображение {os.path.basename(image_path)} получено. В разработке: анализ изображений через AI."
            ai_msg = Message("assistant", response)
            self.current_chat.add_message(ai_msg)

            self.storage.save_chat(self.current_chat)
            self.load_messages()

    def rename_chat(self):
        """Переименовать чат"""
        if not self.current_chat:
            return

        new_name = simpledialog.askstring("Переименовать чат", "Введите новое название:",
                                          initialvalue=self.current_chat.name,
                                          parent=self.root)

        if new_name and new_name.strip():
            self.current_chat.name = new_name.strip()
            self.storage.save_chat(self.current_chat)
            self.chat_title.configure(text=self.current_chat.name)

            # Обновляем кнопку в боковой панели
            if self.current_chat.chat_id in self.chat_buttons:
                frame, btn = self.chat_buttons[self.current_chat.chat_id]
                btn.configure(text=f"💬 {self.current_chat.name}\n({len(self.current_chat.messages)} сообщ.)")

    def delete_chat(self):
        """Удалить чат"""
        if not self.current_chat:
            return

        if messagebox.askyesno("Удалить чат", f"Вы уверены, что хотите удалить чат '{self.current_chat.name}'?"):
            # Удаляем из хранилища
            self.storage.delete_chat(self.current_chat.chat_id)

            # Удаляем кнопку из боковой панели
            if self.current_chat.chat_id in self.chat_buttons:
                frame, btn = self.chat_buttons[self.current_chat.chat_id]
                frame.destroy()
                del self.chat_buttons[self.current_chat.chat_id]

            self.current_chat = None
            self.toggle_chat_controls(False)

            # Очищаем область сообщений
            for widget in self.messages_frame.winfo_children():
                widget.destroy()

            # Скрываем панель ввода
            self.input_frame.pack_forget()

            # Показываем сообщение
            welcome_icon = tk.Label(self.messages_frame, text="🗑️",
                                    bg=self.colors['bg'], fg=self.colors['accent'],
                                    font=("Arial", 48))
            welcome_icon.pack(expand=True, pady=(100, 10))

            welcome_label = tk.Label(self.messages_frame,
                                     text="Чат удалён.\nСоздайте новый чат, чтобы продолжить.",
                                     bg=self.colors['bg'], fg=self.colors['text_light'],
                                     font=("Arial", 12), justify=tk.CENTER)
            welcome_label.pack()
            self.chat_title.configure(text=self.current_subject)

    def back_to_subjects(self):
        """Вернуться к выбору предметов"""
        self.current_subject = None
        self.current_chat = None
        self.toggle_chat_controls(False)
        self.show_subjects()


def main():
    root = tk.Tk()
    app = ChatApplication(root)
    root.mainloop()


if __name__ == "__main__":
    main()