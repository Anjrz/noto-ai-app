from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.lang import Builder
from kivy.core.clipboard import Clipboard
from kivy.animation import Animation
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.properties import NumericProperty, StringProperty, ListProperty, BooleanProperty, OptionProperty
from kivy.clock import mainthread, Clock
from kivy.core.window import Window

from csv_database import CSVDatabase
from ocr_service import OCRService
from ai_service import AISummarizer

Window.title = "Noto.ai"

import threading
import tkinter as tk
from tkinter import filedialog

class SplashScreen(Screen): pass
class MainAppScreen(Screen): pass
class LoginScreen(Screen): pass
class SignUpScreen(Screen): pass

class Animated3DButton(Button):
    scale = NumericProperty(1.0)
    shadow_offset = NumericProperty(12)
    shadow_blur = NumericProperty(36)
    shadow_alpha = NumericProperty(0.28)
    hovered = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouse_pos)

    def on_mouse_pos(self, window, pos):
        inside = self.collide_point(*self.to_widget(*pos))
        if inside and not self.hovered:
            self.hovered = True
            app = App.get_running_app()
            if hasattr(app.root, 'get_screen'):
                try:
                    app.root.get_screen('main').ids.main_content.animate_button_hover(self)
                except Exception:
                    pass
        elif not inside and self.hovered:
            self.hovered = False
            app = App.get_running_app()
            if hasattr(app.root, 'get_screen'):
                try:
                    app.root.get_screen('main').ids.main_content.animate_button_release(self)
                except Exception:
                    pass

    def on_scale(self, instance, value):
        self.transform = (self.center_x, self.center_y, value)

class Animated3DDropdownButton(Animated3DButton):
    selected_option = StringProperty("Choose Action")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.options = [
            "OCR Text Extraction",
            "AI Notes Generation",
            "AI Question Generation",
            "AI Flashcard Generation",
            "AI Keyword Extraction"
        ]
        self.dropdown = DropDown(auto_width=False)
        self.dropdown.size_hint = (None, None)
        self.dropdown.width = 260
        self.dropdown.height = 0
        self.dropdown.opacity = 0
        for option in self.options:
            btn = Animated3DButton(
                text=option,
                size_hint_y=None,
                height=48,
                font_size=22
            )
            btn.is_dropdown_option = True
            btn.bind(on_release=lambda btn: self.select_option(btn.text))
            self.dropdown.add_widget(btn)
        self.dropdown.bind(on_select=self._on_dropdown_select)

    def on_press(self):
        self.animate_button()
        if self.dropdown.parent:
            self.animate_dropdown_close()
        else:
            self.open_dropdown()

    def open_dropdown(self):
        self.dropdown.width = self.width
        self.dropdown.height = 0
        self.dropdown.opacity = 0
        x, y = self.to_window(self.x, self.y)
        y = y - (48 * len(self.options))
        self.dropdown.pos = (x, y)
        self.dropdown.open(self)
        Animation(height=48*len(self.options), opacity=1, d=0.7, t='out_cubic').start(self.dropdown)

    def animate_dropdown_close(self):
        anim = Animation(height=0, opacity=0, d=0.18, t='in_cubic')
        anim.bind(on_complete=lambda *a: self.dropdown.dismiss())
        anim.start(self.dropdown)

    def select_option(self, option):
        self.selected_option = option
        self.animate_dropdown_close()
        self.dropdown.select(option)

    def _on_dropdown_select(self, instance, value):
        self.selected_option = value

    def animate_button(self):
        anim_down = Animation(scale=0.93, shadow_offset=2, shadow_blur=8, shadow_alpha=0.13, duration=0.08, t='out_quad')
        anim_up = Animation(scale=1.0, shadow_offset=12, shadow_blur=36, shadow_alpha=0.28, duration=0.14, t='out_bounce')
        def restore(*args): anim_up.start(self)
        anim_down.bind(on_complete=restore)
        anim_down.start(self)

class MainContent(BoxLayout):
    file_path = StringProperty("")
    action_selected = BooleanProperty(False)
    summary_length = OptionProperty("Medium", options=["Short", "Medium", "Long"])
    ask_box_visible = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ocr_service = OCRService()
        self.ai_summarizer = AISummarizer()

    def toggle_dark_mode(self):
        app = App.get_running_app()
        from kivy.animation import Animation
        if app.bg_color == [0.96, 0.98, 1, 1]:
            Animation(
                bg_color=[0.13, 0.15, 0.18, 1],
                text_color=[1, 1, 1, 1],
                accent_color=[0.10, 0.45, 0.80, 1],
                d=0.5
            ).start(app)
        else:
            Animation(
                bg_color=[0.96, 0.98, 1, 1],
                text_color=[0.08, 0.10, 0.20, 1],
                accent_color=[0.10, 0.45, 0.80, 1],
                d=0.5
            ).start(app)

    def on_upload_button_press(self, button):
        self.animate_button(button)
        Clock.schedule_once(lambda dt: self.open_filechooser(), 0.1)

    def open_filechooser(self):
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        file_path = filedialog.askopenfilename(
            filetypes=[("Image, PDF, or Word files", "*.png *.jpg *.jpeg *.pdf *.docx")]
        )
        root.destroy()
        if file_path:
            self.file_path = file_path
            self.ids.mode_dropdown.disabled = False
            self.ids.execute_btn.disabled = True
            self.ids.copy_btn.opacity = 0
            self.ids.copy_btn.disabled = True
            self.ids.notes_label.text = ""
            self.action_selected = False
            self.update_ask_box_visibility()

    def on_file_path(self, instance, value):
        self.update_ask_box_visibility()

    def on_mode_selected(self, dropdown, text):
        self.action_selected = True
        self.ids.execute_btn.disabled = False
        self.update_ask_box_visibility()
        if text == "AI Notes Generation":
            self.ids.summary_length_box.opacity = 1
            self.ids.summary_length_box.disabled = False
        else:
            self.ids.summary_length_box.opacity = 0
            self.ids.summary_length_box.disabled = True

    def update_ask_box_visibility(self):
        self.ask_box_visible = bool(self.file_path) and self.ids.mode_dropdown.selected_option == "AI Notes Generation"

    def set_summary_length(self, length):
        self.summary_length = length

    def on_execute_button_press(self, button):
        self.animate_button(button)
        if not self.file_path:
            self.update_label("Please upload a file first.")
            return
        if not self.action_selected:
            self.update_label("Please select an action.")
            return
        self.process_file(self.file_path)

    def process_file(self, file_path):
        self.show_loading(True)
        self.ids.notes_label.text = ""
        self.ids.upload_btn.disabled = True
        self.ids.execute_btn.disabled = True
        self.ids.copy_btn.opacity = 0
        self.ids.copy_btn.disabled = True
        threading.Thread(target=self._process_file_bg, args=(file_path,)).start()

    def _process_file_bg(self, file_path):
        selected_mode = self.ids.mode_dropdown.selected_option
        text = self._extract_text(file_path)
        if not text or not text.strip():
            self.show_result("Could not extract any text from this file. The PDF may be image-based, encrypted, or too complex for current extraction methods.")
            self.show_loading(False)
            self.enable_buttons()
            return
        if selected_mode == "OCR Text Extraction":
            self.show_result(text)
        elif selected_mode == "AI Notes Generation":
            if text and text.strip():
                prompt = self.get_summary_prompt(self.summary_length, text)
                try:
                    summary = self.ai_summarizer.summarize(prompt)
                    self.show_result_live(summary)  # <-- Use live typing effect
                except Exception as e:
                    self.show_result(f"AI Error: {e}")
            else:
                self.show_result("Could not extract text from file.")
        elif selected_mode == "AI Question Generation":
            if text and text.strip():
                prompt = f"Generate 5 quiz questions for a student based on these notes:\n{text}\nQuestions:"
                try:
                    questions = self.ai_summarizer.summarize(prompt)
                    self.show_result_live(questions)  # <-- Use live typing effect
                except Exception as e:
                    self.show_result(f"AI Error: {e}")
            else:
                self.show_result("Could not extract text from file.")
        elif selected_mode == "AI Flashcard Generation":
            if text and text.strip():
                prompt = (
                    "From the following notes, generate 5 flashcards in the format:\n"
                    "Q: <question>\nA: <answer>\n\nNotes:\n"
                    f"{text}\nFlashcards:"
                )
                try:
                    flashcards = self.ai_summarizer.summarize(prompt)
                    self.show_result_live(flashcards)  # <-- Use live typing effect
                except Exception as e:
                    self.show_result(f"AI Error: {e}")
            else:
                self.show_result("Could not extract text from file.")
        elif selected_mode == "AI Keyword Extraction":
            if text and text.strip():
                prompt = (
                    "Extract the most relevant keywords and key phrases from the following text. "
                    "List both single and multi-word keywords, ordered by importance. "
                    "Output as a comma-separated list:\n"
                    f"{text}\nKeywords:"
                )
                try:
                    keywords = self.ai_summarizer.summarize(prompt)
                    self.show_result_live("Extracted Keywords:\n" + keywords)  # <-- Use live typing effect
                except Exception as e:
                    self.show_result(f"AI Error: {e}")
            else:
                self.show_result("Could not extract text from file.")
        else:
            self.show_result("Please select an action from the dropdown.")
        self.show_loading(False)
        self.enable_buttons()

    def _extract_text(self, file_path):
        if file_path.lower().endswith('.pdf'):
            return self.ocr_service.pdf_to_text(file_path)
        elif file_path.lower().endswith('.docx'):
            return self.ocr_service.word_to_text(file_path)
        else:
            return self.ocr_service.image_to_text(file_path)

    def get_summary_prompt(self, length, text):
        if length == "Short":
            return f"Summarize the following text in 3-5 sentences:\n{text}"
        elif length == "Medium":
            return f"Summarize the following text in 8-10 sentences:\n{text}"
        elif length == "Long":
            return f"Summarize the following text in detail, covering all main points:\n{text}"
        return f"Summarize the following text:\n{text}"

    @mainthread
    def show_result(self, text):
        self.ids.notes_label.opacity = 0
        if text is None:
            text = ""
        self.ids.notes_label.text = text
        Animation(opacity=1, d=0.6, t='out_quad').start(self.ids.notes_label)
        self.ids.copy_btn.opacity = 1
        self.ids.copy_btn.disabled = False

    # --- LIVE TYPEWRITER EFFECT FOR NOTES ---
    @mainthread
    def show_result_live(self, text, speed=0.01):
        self.ids.notes_label.opacity = 1
        self._full_text = text or ""
        self._current_index = 0
        self.ids.notes_label.text = ""
        self.ids.copy_btn.opacity = 0
        self.ids.copy_btn.disabled = True
        if hasattr(self, '_typing_event') and self._typing_event:
            self._typing_event.cancel()
        self._typing_event = Clock.schedule_interval(lambda dt: self._typewriter_step(), speed)

    def _typewriter_step(self):
        if self._current_index < len(self._full_text):
            self.ids.notes_label.text += self._full_text[self._current_index]
            self._current_index += 1
        else:
            if hasattr(self, '_typing_event') and self._typing_event:
                self._typing_event.cancel()
            # Enable copy button after typing is done
            self.ids.copy_btn.opacity = 1
            self.ids.copy_btn.disabled = False
            return False  # Stop the Clock

    @mainthread
    def show_loading(self, show):
        self.ids.loading_spinner.opacity = 1 if show else 0

    @mainthread
    def enable_buttons(self):
        self.ids.upload_btn.disabled = False
        self.ids.execute_btn.disabled = False

    def copy_notes_to_clipboard(self):
        Clipboard.copy(self.ids.notes_label.text)

    def copy_to_clipboard(self, text):
        Clipboard.copy(text)

    def animate_button(self, button):
        Animation(
            scale=0.93,
            shadow_offset=2,
            shadow_blur=8,
            shadow_alpha=0.13,
            duration=0.08, t='out_quad'
        ).start(button)

    def animate_button_release(self, button):
        Animation(
            scale=1.0,
            shadow_offset=12,
            shadow_blur=36,
            shadow_alpha=0.28,
            duration=0.14, t='out_bounce'
        ).start(button)

    def animate_button_hover(self, button):
        Animation(
            scale=1.08,
            shadow_offset=16,
            shadow_blur=40,
            shadow_alpha=0.33,
            duration=0.18, t='out_quad'
        ).start(button)

    @mainthread
    def update_label(self, text):
        self.ids.notes_label.text = text

    def on_ask_question(self):
        question = self.ids.chat_input.text.strip()
        notes = self.ids.notes_label.text.strip()
        if not notes:
            self.ids.chat_answer.text = "Please generate or extract notes first."
            return
        if not question:
            self.ids.chat_answer.text = "Please type a question."
            return
        self.ids.chat_answer.text = "Thinking..."
        self.ids.ask_btn.disabled = True
        threading.Thread(target=self._ask_question_bg, args=(question, notes)).start()

    def _ask_question_bg(self, question, notes):
        prompt = (
            f"Answer the following question based only on the context below.\n\n"
            f"Context:\n{notes}\n\n"
            f"Question: {question}\nAnswer:"
        )
        try:
            answer = self.ai_summarizer.summarize(prompt)
        except Exception as e:
            answer = f"AI Error: {e}"
        self._show_chat_answer(answer)

    @mainthread
    def _show_chat_answer(self, answer):
        self.ids.chat_answer.text = answer
        self.ids.ask_btn.disabled = False

class Manager(ScreenManager):
    pass

class NotoAIApp(App):
    bg_color = ListProperty([0.96, 0.98, 1, 1])
    text_color = ListProperty([0.08, 0.10, 0.20, 1])
    accent_color = ListProperty([0.10, 0.45, 0.80, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.icon = 'assets/icons/app_icon_72.png'
        self.db = CSVDatabase()

    def build(self):
        Builder.load_file('kv/splash.kv')
        Builder.load_file('kv/login.kv')
        Builder.load_file('kv/signup.kv')
        Builder.load_file('kv/main.kv')
        sm = Manager(transition=FadeTransition())
        sm.add_widget(SplashScreen(name='splash'))
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(SignUpScreen(name='signup'))
        sm.add_widget(MainAppScreen(name='main'))
        return sm

    def on_start(self):
        Clock.schedule_once(self.switch_to_login, 4)

    def switch_to_login(self, dt):
        self.root.current = 'login'

    def login_user(self, username, password):
        login_screen = self.root.get_screen('login')
        if self.db.authenticate_user(username, password):
            login_screen.ids.login_error.text = ""
            self.root.current = 'main'
        else:
            login_screen.ids.login_error.text = "Invalid username or password"

    def signup_user(self, username, password):
        signup_screen = self.root.get_screen('signup')
        if not username or not password:
            signup_screen.ids.signup_error.text = "Please fill all fields"
            return
        if self.db.register_user(username, password):
            signup_screen.ids.signup_error.text = ""
            self.root.current = 'main'
        else:
            signup_screen.ids.signup_error.text = "Username already exists"

if __name__ == "__main__":
    NotoAIApp().run()
