#Response by local LLM
import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import torch
import os
from transformers import AutoModel, AutoTokenizer

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
            x1+radius, y1, x2-radius, y1, x2, y1, x2, y1+radius,
            x2, y2-radius, x2, y2, x2-radius, y2, x1+radius, y2,
            x1, y2, x1, y2-radius, x1, y1+radius, x1, y1
        ]
        return self.create_polygon(points, **kwargs, smooth=True)

class IntegratedLLMApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Integrated LLM App")
        self.geometry("400x600")
        self.configure(bg="#F0F4F9")

        self.image_path = None
        self.model = None
        self.tokenizer = None

        self.create_widgets()
        self.load_model()

    def create_widgets(self):
        # 画像表示エリア
        self.image_frame = tk.Frame(self, bg="#F0F4F9")
        self.image_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.image_label = tk.Label(self.image_frame, bg="#F0F4F9")
        self.image_label.pack(fill=tk.BOTH, expand=True)

        # 入力エリア
        input_frame = tk.Frame(self, bg="#F0F4F9")
        input_frame.pack(fill=tk.X, padx=10, pady=10)

        entry_frame = RoundedFrame(input_frame, bg="white", corner_radius=32, height=64)
        entry_frame.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.message_entry = tk.Entry(entry_frame, font=("Helvetica", 12), bd=0, relief=tk.FLAT, bg="white")
        self.message_entry.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=(20, 5), pady=15)
        self.message_entry.bind("<Return>", self.send_message)

        # 画像アップロードボタン
        self.upload_icon = self.load_and_resize_image("photo_image.png", (30, 30), bg_color="white")
        upload_button = tk.Button(entry_frame, image=self.upload_icon, bg="white", activebackground="white", 
                                  bd=0, relief=tk.FLAT, command=self.upload_image)
        upload_button.pack(side=tk.RIGHT, padx=(5, 10))

        # 送信ボタン
        button_frame = RoundedFrame(input_frame, bg="#008ffc", corner_radius=32, width=80, height=64)
        button_frame.pack(side=tk.RIGHT, padx=(10, 0))

        self.send_icon = self.load_and_resize_image("send_image.png", (28, 28), bg_color="#008ffc")
        send_button = tk.Button(button_frame, image=self.send_icon, command=self.send_message,
                                bg="#008ffc", activebackground="#008ffc", bd=0, relief=tk.FLAT)
        send_button.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # 応答表示エリア
        self.response_text = tk.Text(self, font=("Helvetica", 12), bg="white", wrap=tk.WORD)
        self.response_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def load_and_resize_image(self, path, size, bg_color):
        with Image.open(path) as img:
            img = img.convert("RGBA")
            new_img = Image.new("RGBA", img.size, bg_color)
            new_img.paste(img, (0, 0), img)
            new_img = new_img.resize(size, Image.LANCZOS)
            return ImageTk.PhotoImage(new_img)

    def upload_image(self):
        self.image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")])
        if self.image_path:
            image = Image.open(self.image_path)
            image.thumbnail((400, 400))  # リサイズ
            photo = ImageTk.PhotoImage(image)
            self.image_label.config(image=photo)
            self.image_label.image = photo

    def send_message(self, event=None):
        question = self.message_entry.get()
        self.message_entry.delete(0, tk.END)
        if question:
            if self.image_path:
                self.process_image_and_question(self.image_path, question)
            else:
                self.process_question(question)

    def load_model(self):
        save_directory = r"C:\Users\Sophie\Documents\llm"
        os.makedirs(save_directory, exist_ok=True)

        # モデルとトークナイザーをダウンロードして初期化
        self.model = AutoModel.from_pretrained('openbmb/MiniCPM-Llama3-V-2_5', trust_remote_code=True, torch_dtype=torch.float16)
        self.tokenizer = AutoTokenizer.from_pretrained('openbmb/MiniCPM-Llama3-V-2_5', trust_remote_code=True)

        # モデルとトークナイザーをローカルに保存
        self.model.save_pretrained(save_directory)
        self.tokenizer.save_pretrained(save_directory)

        # GPUに移動（利用可能な場合）
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = self.model.to(device=device)
        self.model.eval()

    def process_image_and_question(self, image_path, question):
        image = Image.open(image_path).convert('RGB')
        msgs = [{'role': 'user', 'content': question}]

        # チャット応答を生成（サンプリング使用）
        res = self.model.chat(
            image=image,
            msgs=msgs,
            tokenizer=self.tokenizer,
            sampling=True,
            temperature=0.7,
            stream=True
        )

        self.response_text.delete('1.0', tk.END)
        for new_text in res:
            self.response_text.insert(tk.END, new_text)
            self.response_text.see(tk.END)
            self.response_text.update()

    def process_question(self, question):
        msgs = [{'role': 'user', 'content': question}]

        # チャット応答を生成（サンプリング使用）
        res = self.model.chat(
            image=None,
            msgs=msgs,
            tokenizer=self.tokenizer,
            sampling=True,
            temperature=0.7,
            stream=True
        )

        self.response_text.delete('1.0', tk.END)
        for new_text in res:
            self.response_text.insert(tk.END, new_text)
            self.response_text.see(tk.END)
            self.response_text.update()

if __name__ == "__main__":
    app = IntegratedLLMApp()
    app.mainloop()
