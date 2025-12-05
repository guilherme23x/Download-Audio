import flet as ft
import yt_dlp
import os
import threading
import time


def main(page: ft.Page):
    # --- Configurações da Janela ---
    page.title = "Universal Audio Converter"
    page.window.width = 400
    page.window.height = 600
    page.window_resizable = False
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 30
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # Variáveis globais de estado
    download_path = os.path.join(os.path.expanduser("~"), "Music")

    # --- Funções de Lógica ---

    def pick_folder_result(e: ft.FilePickerResultEvent):
        nonlocal download_path
        if e.path:
            download_path = e.path
            txt_path.value = download_path
            txt_path.update()

    def progress_hook(d):
        if d["status"] == "downloading":
            try:
                p = d.get("_percent_str", "0%").replace("%", "")
                progress_val = float(p) / 100
                pb.value = progress_val
                lbl_status.value = f"Baixando: {d.get('_percent_str')}..."
                # CORREÇÃO: ft.Colors (Maiúsculo)
                lbl_status.color = ft.Colors.BLUE_200
                page.update()
            except:
                pass
        elif d["status"] == "finished":
            lbl_status.value = "Convertendo WebM para MP3... (Isso usa o FFmpeg)"
            # CORREÇÃO: ft.Colors (Maiúsculo)
            lbl_status.color = ft.Colors.AMBER
            page.update()

    def run_download(url, quality):
        try:
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": os.path.join(download_path, "%(title)s.%(ext)s"),
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": quality,
                    }
                ],
                "progress_hooks": [progress_hook],
                "noplaylist": True,
                "quiet": True,
                "no_warnings": True,
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            # Sucesso
            lbl_status.value = "Download e Conversão Concluídos!"
            # CORREÇÃO: ft.Colors (Maiúsculo)
            lbl_status.color = ft.Colors.GREEN
            pb.value = 1

            page.update()
            time.sleep(3)
            reset_ui()

        except Exception as e:
            lbl_status.value = f"Erro: {e}"
            # CORREÇÃO: ft.Colors (Maiúsculo)
            lbl_status.color = ft.Colors.RED
            page.update()
            time.sleep(3)
            reset_ui()

    def start_download(e):
        url = txt_url.value
        if not url:
            txt_url.error_text = "Por favor, insira um link."
            txt_url.update()
            return

        txt_url.error_text = None
        btn_download.disabled = True
        btn_download.text = "Processando..."
        pb.visible = True
        page.update()

        threading.Thread(target=run_download, args=(url, dd_quality.value)).start()

    def reset_ui():
        btn_download.disabled = False
        btn_download.text = "BAIXAR ÁUDIO"
        pb.value = 0
        pb.visible = False
        lbl_status.value = "Pronto para iniciar"
        # CORREÇÃO: ft.Colors (Maiúsculo)
        lbl_status.color = ft.Colors.GREY
        page.update()

    # --- Componentes da Interface (UI) ---

    # 1. Título e Ícone
    header = ft.Column(
        [
            # CORREÇÃO: ft.Icons e ft.Colors (Maiúsculos)
            ft.Icon(ft.Icons.MUSIC_NOTE_ROUNDED, size=50, color=ft.Colors.BLUE),
            ft.Text("Music Downloader", size=26, weight=ft.FontWeight.BOLD),
            ft.Text("YouTube, Instagram, TikTok & Mais", size=12, color=ft.Colors.GREY),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=5,
    )

    # 2. Entrada de Texto
    txt_url = ft.TextField(
        label="Link do Vídeo/Áudio",
        hint_text="Cole a URL aqui...",
        width=450,
        border_radius=15,
        # CORREÇÃO: ft.Icons e ft.Colors (Maiúsculos)
        prefix_icon=ft.Icons.LINK,
        bgcolor=ft.Colors.GREY_800,  # Usando GREY_800 fixo para evitar erro de variante
    )

    # 3. Seletor de Pasta e Qualidade
    file_picker = ft.FilePicker(on_result=pick_folder_result)
    page.overlay.append(file_picker)

    # NOVO: Campo de texto visual para a pasta (Ícone na frente)
    txt_path = ft.TextField(
        label="Salvar na Pasta",
        value=download_path,
        read_only=True,  # Usuário não digita, apenas vê
        expand=True,  # Ocupa o espaço sobrando
        height=50,
        text_size=12,
        border_radius=15,
        prefix_icon=ft.Icons.FOLDER_OPEN,  # <--- ÍCONE AGORA FICA NA FRENTE
        bgcolor=ft.Colors.GREY_800,
        # Botão discreto no final para alterar
        suffix=ft.IconButton(
            icon=ft.Icons.EDIT,
            tooltip="Alterar Pasta",
            on_click=lambda _: file_picker.get_directory_path(),
        ),
    )

    dd_quality = ft.Dropdown(
        width=110,
        label="Kbps",
        value="320",
        options=[
            ft.dropdown.Option("128", "128"),
            ft.dropdown.Option("192", "192"),
            ft.dropdown.Option("320", "320"),
        ],
        border_radius=15,
        content_padding=10,
    )

    # ALTERADO: Linha que junta a Pasta e a Qualidade
    row_options = ft.Row(
        [txt_path, dd_quality],
        width=450,
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        spacing=10,
    )

    # 4. Botão de Ação e Status
    btn_download = ft.ElevatedButton(
        text="BAIXAR ÁUDIO",
        # CORREÇÃO: ft.Icons (Maiúsculo)
        icon=ft.Icons.DOWNLOAD_ROUNDED,
        width=250,
        height=50,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10),
            # CORREÇÃO: ft.Colors (Maiúsculo)
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.BLUE_700,
        ),
        on_click=start_download,
    )

    # CORREÇÃO: ft.Colors (Maiúsculo)
    pb = ft.ProgressBar(
        width=400, color=ft.Colors.BLUE, bgcolor=ft.Colors.GREY_800, visible=False
    )
    lbl_status = ft.Text("Pronto para iniciar", size=12, color=ft.Colors.GREY)

    # --- Montagem do Layout ---
    page.add(
        ft.Container(height=20),
        header,
        ft.Container(height=30),
        txt_url,
        ft.Container(height=10),
        row_options,
        ft.Container(height=30),
        btn_download,
        ft.Container(height=20),
        pb,
        lbl_status,
    )


if __name__ == "__main__":
    ft.app(target=main)
