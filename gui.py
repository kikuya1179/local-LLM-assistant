import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class RoundedFrame(tk.Canvas):
    def __init__(self, parent, bg="#ffffff", width=200, height=28, corner_radius=32, padding=3, **kwargs):
        super().__init__(parent, bg=parent["bg"], highlightthickness=0, **kwargs)

        self._corner_radius = corner_radius
        self._padding = padding
        self._bg = bg

        self.bind("<Configure>", self._on_configure)

    def _on_configure(self, event):
        self.delete("all")
        w, h = event.width, event.height
        self._draw_rounded_rect(w, h)

    def _draw_rounded_rect(self, width, height):
        x1, y1 = self._padding, self._padding
        x2, y2 = width - self._padding, height - self._padding
        self.create_rounded_rect(x1, y1, x2, y2, fill=self._bg)

    def create_rounded_rect(self, x1, y1, x2, y2, **kwargs):
        radius = self._corner_radius
        points = [
            x1+radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1
        ]
        return self.create_polygon(points, **kwargs, smooth=True)

class RoundedMessageApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Rounded Message App")
        self.geometry("400x600")
        self.resizable(False, False)
        self.configure(bg="#F0F4F9")

        self.create_widgets()

    def create_widgets(self):
        # 入力エリア
        input_frame = tk.Frame(self, bg="#F0F4F9")
        input_frame.pack(fill=tk.X, padx=10, pady=10)

        entry_frame = RoundedFrame(input_frame, bg="white", corner_radius=32, height=64)
        entry_frame.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.message_entry = tk.Entry(entry_frame, font=("Helvetica", 12), bd=0, relief=tk.FLAT, bg="white")
        self.message_entry.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=(20, 5), pady=15)
        self.message_entry.bind("<Return>", self.send_message)

        # テキストボックス内のボタン1（右寄せ）
        self.icon1 = self.load_and_resize_image("photo_image.png", (30, 30), bg_color="white")
        icon1_button = tk.Button(entry_frame, image=self.icon1, bg="white", activebackground="white", 
                                 bd=0, relief=tk.FLAT, command=self.icon1_action)
        icon1_button.pack(side=tk.RIGHT, padx=(5, 5))

        # テキストボックス内のボタン2
        self.icon2 = self.load_and_resize_image("image.png", (30, 30), bg_color="white")
        icon2_button = tk.Button(entry_frame, image=self.icon2, bg="white", activebackground="white", 
                                 bd=0, relief=tk.FLAT, command=self.icon2_action)
        icon2_button.pack(side=tk.RIGHT, padx=(5, 10))

        button_frame = RoundedFrame(input_frame, bg="#008ffc", corner_radius=32, width=80, height=64)
        button_frame.pack(side=tk.RIGHT, padx=(10, 0))

        # 送信ボタンのPNG画像
        self.send_icon = self.load_and_resize_image("send_image.png", (28, 28), bg_color="#008ffc")
        send_button = tk.Button(button_frame, image=self.send_icon, command=self.send_message,
                                bg="#008ffc", activebackground="#008ffc", bd=0, relief=tk.FLAT)
        send_button.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

    def load_and_resize_image(self, path, size, bg_color):
        with Image.open(path) as img:
            img = img.convert("RGBA")
            new_img = Image.new("RGBA", img.size, bg_color)
            new_img.paste(img, (0, 0), img)
            new_img = new_img.resize(size, Image.LANCZOS)
            return ImageTk.PhotoImage(new_img)

    def send_message(self, event=None):
        message = self.message_entry.get()
        if message:
            self.message_entry.delete(0, tk.END)
            print(f"送信されたメッセージ: {message}")  # 実際の送信ロジックに置き換えてください

    def icon1_action(self):
        print("アイコン1がクリックされました")  # 実際のアクション処理に置き換えてください

    def icon2_action(self):
        print("アイコン2がクリックされました")  # 実際のアクション処理に置き換えてください

    def on_closing(self):
        self.quit()

if __name__ == "__main__":
    app = RoundedMessageApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()