import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from document_generator import DocumentGenerator
from document_register import DocumentRegisterSystem, GoogleDriveManager
from document_search import DocumentSearch
import sys
from PIL import Image, ImageTk

class SistemaGestionDocumental:
    def __init__(self):
        """Inicializa la ventana principal del sistema"""
        # Crear ventana principal primero
        self.root = ttk.Window(themename="flatly")
        self.root.withdraw()  # Ocultarla temporalmente
        
        # Crear ventana de carga
        loading_window = ttk.Toplevel(self.root)
        loading_window.title("Conectando")
        loading_window.geometry("300x150")
        
        # Centrar ventana de carga
        screen_width = loading_window.winfo_screenwidth()
        screen_height = loading_window.winfo_screenheight()
        x = (screen_width - 300) // 2
        y = (screen_height - 150) // 2
        loading_window.geometry(f"+{x}+{y}")
        
        # Frame para carga
        loading_frame = ttk.Frame(loading_window, padding=20)
        loading_frame.pack(fill=BOTH, expand=YES)
        
        ttk.Label(
            loading_frame,
            text="Conectando con Google Drive...",
            font=("Segoe UI", 11),
            wraplength=250
        ).pack(pady=(0, 15))
        
        progress = ttk.Progressbar(
            loading_frame,
            mode='indeterminate',
            length=200
        )
        progress.pack()
        progress.start(15)
        
        loading_window.update()
        
        try:
            # Inicializar Google Drive
            self.drive_manager = GoogleDriveManager('credentials.json')
            self.drive_manager.setup_spreadsheet()
            
            # Configurar ventana principal
            self.root.title("Sistema de Gestión Documental")
            window_width = 800
            window_height = 600
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
            self.root.geometry(f'{window_width}x{window_height}+{x}+{y}')
            self.root.minsize(800, 600)
            
            # Cerrar ventana de carga
            loading_window.destroy()
            
            # Mostrar ventana principal
            self.root.deiconify()
            
            # Inicializar el menú principal
            self.setup_main_menu()
            
        except Exception as e:
            loading_window.destroy()
            self.root.destroy()
            messagebox.showerror(
                "Error de Conexión",
                f"Error al conectar con Google Drive: {str(e)}"
            )
            sys.exit(1)
            
    def setup_main_menu(self):
        """Configurar el menú principal"""
        # Frame principal con padding
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=BOTH, expand=YES)
        
        # Frame para el logo y título
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(pady=(0, 40))
        
        # Logo
        try:
            logo_img = Image.open('Logo.jpg')
            # Redimensionar el logo si es necesario
            logo_img.thumbnail((200, 200))  # Ajusta estos números según el tamaño que quieras
            logo_photo = ImageTk.PhotoImage(logo_img)
            logo_label = ttk.Label(header_frame, image=logo_photo)
            logo_label.image = logo_photo
            logo_label.pack(pady=(0, 20))
        except Exception as e:
            print(f"Error al cargar el logo: {str(e)}")
        
        # Título
        title_label = ttk.Label(
            header_frame,
            text="Sistema de Gestión Documental",
            font=("Segoe UI", 24, "bold"),
            bootstyle="primary"
        )
        title_label.pack()
        
        # Frame para los botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(expand=YES)
        
        # Botones principales
        self.create_menu_button(
            button_frame,
            "Generación de Documentos",
            "Generar nuevos documentos con códigos QR",
            self.open_generator,
            "primary"
        )
        
        self.create_menu_button(
            button_frame,
            "Registro de Documentos",
            "Registrar y escanear documentos existentes",
            self.open_register,
            "success"
        )
        
        self.create_menu_button(
            button_frame,
            "Búsqueda de Documentos",
            "Buscar documentos registrados",
            self.open_search,
            "info"
        )
        
    def create_menu_button(self, parent, text, description, command, style):
        """Crear un botón de menú con descripción"""
        # Frame para el botón y su descripción
        frame = ttk.Frame(parent)
        frame.pack(pady=10, fill=X)
        
        # Botón principal
        btn = ttk.Button(
            frame,
            text=text,
            command=command,
            bootstyle=f"{style}-outline",
            width=30
        )
        btn.pack(pady=(0, 5))
        
        # Descripción
        desc_label = ttk.Label(
            frame,
            text=description,
            font=("Segoe UI", 10),
            foreground="gray"
        )
        desc_label.pack()
        
    def run(self):
        """Iniciar la aplicación"""
        self.root.mainloop()
    
    def open_generator(self): 
        print("generador accedido")
        generator = DocumentGenerator(
            parent=self.root, 
            drive_manager=self.drive_manager
        )


    def open_register(self): 
        print("registrador accedido")
        register = DocumentRegisterSystem(  
            parent=self.root, 
            drive_manager=self.drive_manager
        )

    def open_search(self):
        print("Buscador accedido")
        search = DocumentSearch(
            parent=self.root, 
            drive_manager=self.drive_manager
        )
    
if __name__ == "__main__":
    app = SistemaGestionDocumental()
    app.run()

