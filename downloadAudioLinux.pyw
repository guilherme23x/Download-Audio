import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
import yt_dlp

def baixar_audio(button):
    url_video = entry_url.get_text()
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
                status_label.set_text("Download concluído!")
        except Exception as e:
            status_label.set_text(f"Erro: {str(e)}")
    else:
        status_label.set_text("Por favor, insira uma URL válida!")

# Create the main window
window = Gtk.Window(title="Download Audio")
window.set_resizable(False)
window.set_default_size(350, 150)
window.set_opacity(0.95)  # Set window transparency
window.connect("destroy", Gtk.main_quit)

# Create a vertical box layout
box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
box.set_margin_top(20)
box.set_margin_bottom(20)
box.set_margin_start(20)
box.set_margin_end(20)
window.add(box)

# Create the URL entry field
entry_url = Gtk.Entry()
entry_url.set_placeholder_text("Cole a URL do vídeo")
entry_url.set_width_chars(30)
entry_url.set_name("entry-dark")
box.pack_start(entry_url, False, False, 0)

# Create the download button
btn_baixar = Gtk.Button(label="Download")
btn_baixar.set_name("button-dark")
btn_baixar.connect("clicked", baixar_audio)
box.pack_start(btn_baixar, False, False, 0)

# Create the status label
status_label = Gtk.Label(label="")
status_label.set_name("label-dark")
box.pack_start(status_label, False, False, 0)

# Apply dark theme CSS with specific button styling
css_provider = Gtk.CssProvider()
css_data = """
#entry-dark {
    background-color: #202020;
    color: #FFFFFF;
    font-family: Inter, sans-serif;
    font-size: 12px;
    padding: 5px;
}
button#button-dark {
    background-color: #202020;
    background-image: none; /* Disable theme background */
    color: #FFFFFF;
    font-family: Inter, sans-serif;
    font-size: 12px;
    padding: 5px 10px;
}
button#button-dark:hover {
    background-color: #101010;
}
#label-dark {
    color: #FFFFFF;
    font-family: Inter, sans-serif;
    font-size: 12px;
}
window {
    background-color: #101010;
}
"""
css_provider.load_from_data(css_data.encode())
Gtk.StyleContext.add_provider_for_screen(
    Gdk.Screen.get_default(),
    css_provider,
    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
)

# Show all widgets
window.show_all()

# Start the GTK main loop
Gtk.main()