import sys
import os
import threading
import yt_dlp
import time
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QProgressBar,
    QFileDialog,
    QFrame,
)
from PySide6.QtCore import Qt, Signal, QObject, QTimer

# --- DESIGN SYSTEM (MINIMALISTA) ---
STYLE = """
    QWidget { background-color: #0A0A0A; color: #F5F5F5; font-family: 'Inter', 'Segoe UI'; }
    QFrame#Main { border: 1px solid #1A1A1A; border-radius: 12px; background-color: #0A0A0A; }
    
    QLabel#Title { font-size: 22px; font-weight: 800; letter-spacing: -1px; color: #FFFFFF; }
    QLabel#Badge { color: #666; font-size: 10px; font-weight: bold; text-transform: uppercase; letter-spacing: 1.5px; }
    
    QLineEdit { 
        background-color: #111; border: 1px solid #1A1A1A; border-radius: 8px; 
        padding: 0px 12px; color: #EEE; font-size: 13px; height: 48px;
    }
    QLineEdit:focus { border: 1px solid #444; }

    QPushButton#ActionBtn { 
        background-color: #FFFFFF; color: #000; border-radius: 8px; 
        font-weight: bold; font-size: 12px; height: 48px; text-transform: uppercase;
    }
    QPushButton#ActionBtn:hover { background-color: #DDD; }
    QPushButton#ActionBtn:disabled { background-color: #222; color: #444; }

    QPushButton#SecondaryBtn { 
        background-color: transparent; border: 1px solid #1A1A1A; 
        border-radius: 8px; color: #888; font-size: 11px; padding: 5px 15px;
    }
    QPushButton#SecondaryBtn:hover { border-color: #444; color: #FFF; }

    QProgressBar { background-color: #111; border: none; height: 3px; border-radius: 1px; }
    QProgressBar::chunk { background-color: #FFFFFF; }
"""


class WorkerSignals(QObject):
    progress = Signal(float)
    status = Signal(str, str)  # Mensagem, Cor (hex)
    finished = Signal()


class AudioDownloaderPro(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(400, 550)
        self.setStyleSheet(STYLE)

        self.download_path = os.path.join(os.path.expanduser("~"), "Music")
        self.signals = WorkerSignals()

        # Conectar Sinais
        self.signals.progress.connect(self.update_pb)
        self.signals.status.connect(self.update_status)
        self.signals.finished.connect(self.on_finished)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.main_frame = QFrame()
        self.main_frame.setObjectName("Main")

        content = QVBoxLayout(self.main_frame)
        content.setContentsMargins(35, 20, 35, 40)
        content.setSpacing(20)

        # Barra de Fechar
        close_bar = QHBoxLayout()
        btn_close = QPushButton("✕")
        btn_close.setFixedSize(30, 30)
        btn_close.setStyleSheet("border:none; color: #444; font-size: 16px;")
        btn_close.clicked.connect(self.close)
        close_bar.addStretch()
        close_bar.addWidget(btn_close)
        content.addLayout(close_bar)

        # Header
        content.addWidget(QLabel("AUDIO", objectName="Badge"))
        content.addWidget(QLabel("Downloader Pro", objectName="Title"))
        content.addSpacing(10)

        # URL
        content.addWidget(QLabel("Link da URL", objectName="Badge"))
        self.txt_url = QLineEdit()
        self.txt_url.setPlaceholderText("Cole o link aqui...")
        content.addWidget(self.txt_url)

        # Pasta
        content.addWidget(QLabel("Destino", objectName="Badge"))
        path_row = QHBoxLayout()
        self.lbl_path = QLabel(self.shorten_path(self.download_path))
        self.lbl_path.setStyleSheet("color: #555; font-size: 11px;")
        btn_path = QPushButton("Alterar")
        btn_path.setObjectName("SecondaryBtn")
        btn_path.clicked.connect(self.pick_folder)
        path_row.addWidget(self.lbl_path)
        path_row.addStretch()
        path_row.addWidget(btn_path)
        content.addLayout(path_row)

        # Qualidade
        content.addWidget(QLabel("Qualidade (Kbps)", objectName="Badge"))
        self.combo_quality = QComboBox()
        self.combo_quality.addItems(["128", "192", "320"])
        self.combo_quality.setCurrentText("320")
        self.combo_quality.setStyleSheet(
            "background:#111; border:1px solid #1A1A1A; padding:8px; border-radius:5px;"
        )
        content.addWidget(self.combo_quality)

        content.addStretch()

        # Feedback e Botão
        self.status_label = QLabel("Pronto para iniciar")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet(
            "color: #444; font-size: 11px; font-weight: bold; text-transform: uppercase;"
        )
        content.addWidget(self.status_label)

        self.pb = QProgressBar()
        self.pb.setValue(0)
        self.pb.hide()
        content.addWidget(self.pb)

        self.btn_run = QPushButton("Baixar Áudio")
        self.btn_run.setObjectName("ActionBtn")
        self.btn_run.clicked.connect(self.start_thread)
        content.addWidget(self.btn_run)

        layout.addWidget(self.main_frame)

    # --- LÓGICA DE DRAG (ARRASTAR JANELA) ---
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_pos)
            event.accept()

    # --- FUNÇÕES AUXILIARES ---
    def shorten_path(self, path):
        if len(path) > 30:
            return "..." + path[-27:]
        return path

    def pick_folder(self):
        path = QFileDialog.getExistingDirectory(
            self, "Selecionar Pasta", self.download_path
        )
        if path:
            self.download_path = path
            self.lbl_path.setText(self.shorten_path(path))

    def update_pb(self, val):
        self.pb.show()
        self.pb.setValue(int(val))

    def update_status(self, text, color):
        self.status_label.setText(text)
        self.status_label.setStyleSheet(
            f"color: {color}; font-size: 11px; font-weight: bold; text-transform: uppercase;"
        )

    # --- CORE DOWNLOAD (LÓGICA IGUAL AO SEU FLET) ---
    def progress_hook(self, d):
        if d["status"] == "downloading":
            try:
                p_str = d.get("_percent_str", "0%").replace("%", "").strip()
                p_float = float(p_str)
                self.signals.progress.emit(p_float)
                self.signals.status.emit(f"Baixando: {p_str}%", "#3498db")
            except:
                pass
        elif d["status"] == "finished":
            self.signals.progress.emit(100)
            self.signals.status.emit("Convertendo para MP3...", "#f1c40f")

    def run_download(self, url, quality):
        try:
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": os.path.join(self.download_path, "%(title)s.%(ext)s"),
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": quality,
                    }
                ],
                "progress_hooks": [self.progress_hook],
                "noplaylist": True,
                "quiet": True,
                "no_warnings": True,
                # --- NOVAS OPÇÕES PARA EVITAR O ERRO 403 ---
                "nocheckcertificate": True,
                "geo_bypass": True,
                "http_headers": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                    "Accept": "*/*",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Sec-Fetch-Mode": "navigate",
                },
            }

            # Limpa o cache do yt-dlp antes de começar (ajuda com erros 403)
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.cache.remove()
                ydl.download([url])

            self.signals.status.emit("Concluído com Sucesso!", "#2ecc71")
        except Exception as e:
            error_msg = str(e)
            if "403" in error_msg:
                self.signals.status.emit(
                    "Erro 403: YouTube bloqueou o acesso.", "#e74c3c"
                )
            else:
                self.signals.status.emit(f"Erro no Download", "#e74c3c")

        self.signals.finished.emit()
        try:
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": os.path.join(self.download_path, "%(title)s.%(ext)s"),
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": quality,
                    }
                ],
                "progress_hooks": [self.progress_hook],
                "noplaylist": True,
                "quiet": True,
                "no_warnings": True,
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            self.signals.status.emit("Concluído com Sucesso!", "#2ecc71")
        except Exception as e:
            self.signals.status.emit(f"Erro: {str(e)[:20]}...", "#e74c3c")

        self.signals.finished.emit()

    def start_thread(self):
        url = self.txt_url.text().strip()
        if not url:
            return

        self.btn_run.setEnabled(False)
        self.btn_run.setText("Processando...")
        threading.Thread(
            target=self.run_download,
            args=(url, self.combo_quality.currentText()),
            daemon=True,
        ).start()

    def on_finished(self):
        QTimer.singleShot(4000, self.reset_ui)

    def reset_ui(self):
        self.btn_run.setEnabled(True)
        self.btn_run.setText("Baixar Áudio")
        self.pb.hide()
        self.pb.setValue(0)
        self.status_label.setText("Pronto para iniciar")
        self.status_label.setStyleSheet(
            "color: #444; font-size: 11px; font-weight: bold; text-transform: uppercase;"
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AudioDownloaderPro()
    window.show()
    sys.exit(app.exec())
