import customtkinter as ctk
import yt_dlp

def baixar_audio():
    url_video = entry_url.get()
    if url_video:
        ydl_opts = {
            'format': 'bestaudio/best',
            'extractaudio': True,
            'audioquality': 1,
            'outtmpl': '%(title)s.%(ext)s',
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url_video])
                status_label.config(text="Download concluído!")
        except Exception as e:
            status_label.config(text=f"Erro: {e}")
    else:
        status_label.config(text="Por favor, insira uma URL válida!")


window = ctk.CTk()
window.title("Download Audio")
window.resizable(False, False)
window.attributes('-alpha', 0.95)
window.geometry("350x150")

entry_url = ctk.CTkEntry(
    window, width=290, placeholder_text="Cole a URL do vídeo",fg_color="#303030",font=("Inter", 12))
entry_url.pack(pady=20)

btn_baixar = ctk.CTkButton(window, text="Download", command=baixar_audio, fg_color="#010101", hover_color="#101010",font=("Inter", 12))
btn_baixar.pack(pady=10)

status_label = ctk.CTkLabel(window, text="")
status_label.pack(pady=20)

window.mainloop()
