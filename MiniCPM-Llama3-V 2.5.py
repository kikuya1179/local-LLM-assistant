import torch
import os
from PIL import Image
from transformers import AutoModel, AutoTokenizer

# モデルの保存先ディレクトリを指定
save_directory = r"C:\Users\Sophie\Documents\llm"

# ディレクトリが存在しない場合は作成
os.makedirs(save_directory, exist_ok=True)

# モデルとトークナイザーをダウンロードして初期化
model = AutoModel.from_pretrained('openbmb/MiniCPM-Llama3-V-2_5', trust_remote_code=True, torch_dtype=torch.float16)
tokenizer = AutoTokenizer.from_pretrained('openbmb/MiniCPM-Llama3-V-2_5', trust_remote_code=True)

# モデルとトークナイザーをローカルに保存
model.save_pretrained(save_directory)
tokenizer.save_pretrained(save_directory)

print(f"Model and tokenizer saved to {save_directory}")

# ローカルから保存したモデルとトークナイザーを読み込む
model = AutoModel.from_pretrained(save_directory, trust_remote_code=True, torch_dtype=torch.float16)
tokenizer = AutoTokenizer.from_pretrained(save_directory, trust_remote_code=True)

# GPUに移動（利用可能な場合）
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model = model.to(device=device)

model.eval()

# 画像を読み込む
image = Image.open('031858.png').convert('RGB')
question = 'What is in the image?'
msgs = [{'role': 'user', 'content': question}]

# チャット応答を生成（サンプリング使用）
res = model.chat(
    image=image,
    msgs=msgs,
    tokenizer=tokenizer,
    sampling=True,
    temperature=0.7,
)
print("Response:", res)

# ストリーミングを使用した応答生成
res = model.chat(
    image=image,
    msgs=msgs,
    tokenizer=tokenizer,
    sampling=True,
    temperature=0.7,
    stream=True
)

print("Streaming response:")
generated_text = ""
for new_text in res:
    generated_text += new_text
    print(new_text, flush=True, end='')

print("\n\nFull generated text:", generated_text)