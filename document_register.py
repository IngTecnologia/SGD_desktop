# Importaciones para la interfaz gráfica
import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# Importaciones para manejo de archivos y rutas
import os
import shutil  # Para copiar archivos

# Importaciones para procesamiento de imágenes y PDFs
from PIL import Image, ImageTk  # Para manejo de imágenes en la interfaz
import fitz  # PyMuPDF para manejo de PDFs
import cv2  # Para procesamiento de imágenes
import numpy as np  # Para operaciones con arrays (necesario para CV2)
from pyzbar.pyzbar import decode  # Para leer códigos QR

# Importaciones para manejo de datos y tiempo
import pandas as pd  # Para manejar el archivo Excel
from datetime import datetime  # Para registrar fechas y crear nombres únicos

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseDownload 

class DocumentRegisterSystem:
# Métodos de inicialización 
    def __init__(self, parent=None, drive_manager=None):
        """
        Inicializa el sistema de registro de documentos.
        
        Args:
            parent: Ventana padre (menú principal).
            drive_manager: Instancia de GoogleDriveManager ya inicializada
        """
        # Guardar referencia a la ventana padre y drive_manager
        self.parent = parent
        self.drive_manager = drive_manager
        
        # Tipos de archivos soportados
        self.supported_types = {
            'Archivos PDF': '.pdf',
            'Archivos de Imagen': ('.png', '.jpg', '.jpeg')
        }
        
        # Lista para rastrear archivos subidos
        self.uploaded_files = []
        
        # Crear la ventana principal
        self.root = ttk.Toplevel(parent) if parent else ttk.Window()
        self.root.title("Registro de Documentos Escaneados")
        
        # Configurar tamaño y posición
        window_width = 800
        window_height = 600
        
        # Centrar en pantalla
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # Establecer geometría
        self.root.geometry(f'{window_width}x{window_height}+{x}+{y}')
        self.root.minsize(800, 640)
        
        if parent:
            self.root.transient(parent)
            self.root.grab_set()
        
        # Variable para control de procesamiento
        self.is_processing = False
        
        # Configurar la interfaz principal
        self.setup_main_window()
    
    def setup_main_window(self): 
        """Configurar la ventana principal"""
        # Crear frame principal con padding
        main_frame = ttk.Frame(self.root, padding=15)
        main_frame.pack(fill=BOTH, expand=YES)
        
        # Título
        title_label = ttk.Label(
            main_frame,
            text="Registro de Documentos Escaneados",
            font=("Segoe UI", 20),
            bootstyle="primary"
        )
        title_label.pack(anchor=W, pady=(0, 20))
        
        # Marco de selección de documentos
        selection_frame = ttk.LabelFrame(
            main_frame,
            text="Seleccionar Documentos",
            padding=10
        )
        selection_frame.pack(fill=X, pady=(0, 15))
        
        # Contenedor de botones
        button_frame = ttk.Frame(selection_frame)
        button_frame.pack(fill=X, expand=YES, pady=5)
        
        # Botón seleccionar archivos
        select_files_btn = ttk.Button(
            button_frame,
            text="Seleccionar Archivos",
            command=self.select_files,
            bootstyle="secondary", # Gris 
            width=18 # Ancho ajustado
        )
        select_files_btn.pack(side=LEFT, padx=5)
        
        # Botón seleccionar carpeta
        select_folder_btn = ttk.Button(
            button_frame,
            text="Seleccionar Carpeta",
            command=self.select_folder,
            bootstyle="info",
            width=18
        )
        select_folder_btn.pack(side=LEFT, padx=5)
        
        # Botón limpiar
        clear_btn = ttk.Button(
            button_frame,
            text="Limpiar Todo",
            command=self.clear_files,
            bootstyle="danger-outline",
            width=18
        )
        clear_btn.pack(side=RIGHT, padx=5)
        
        # Etiqueta de lista de archivos
        list_label = ttk.Label(
            main_frame,
            text="Documentos Seleccionados",
            font=("Segoe UI", 10),
            foreground="gray"
        )
        list_label.pack(anchor=W, pady=(15, 5))
        
        # Marco para la lista de archivos
        list_frame = ttk.Frame(main_frame, relief="solid", borderwidth=1)
        list_frame.pack(fill=BOTH, expand=YES)
        
        # Lista con columnas
        self.file_listbox = ttk.Treeview(
            list_frame,
            columns=("Nombre", "Tipo", "Tamaño"),
            show="headings",
            selectmode="extended",
            height=12
        )
        
        # Configurar columnas
        self.file_listbox.heading("Nombre", text="Nombre del Archivo")
        self.file_listbox.heading("Tipo", text="Tipo")
        self.file_listbox.heading("Tamaño", text="Tamaño")
        
        # Ajustar anchos de columna
        self.file_listbox.column("Nombre", width=350)
        self.file_listbox.column("Tipo", width=100)
        self.file_listbox.column("Tamaño", width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(
            list_frame, 
            orient=VERTICAL, 
            command=self.file_listbox.yview
        )
        self.file_listbox.configure(yscrollcommand=scrollbar.set)
        
        # Empaquetar lista y scrollbar
        self.file_listbox.pack(side=LEFT, fill=BOTH, expand=YES)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Frame para el botón registrar
        register_frame = ttk.Frame(main_frame)
        register_frame.pack(fill=X, pady=15)
        
        # Botón Registrar
        self.register_btn = ttk.Button(
            register_frame,
            text="Registrar Documentos",
            command=self.open_register_window,
            bootstyle="success",
            width=20,
            state="disabled"
        )
        self.register_btn.pack(pady=10)
        
        # Barra de estado
        self.status_var = tk.StringVar(value="Listo")
        status_bar = ttk.Label(
            main_frame,
            textvariable=self.status_var,
            foreground="gray"
        )
        status_bar.pack(anchor=W, pady=(5, 0))
    
    def setup_register_window(self, window): 
        """Configurar la ventana de registro"""
        window.title("Registro de Documento")
        window.geometry("1200x700")
        window.minsize(1000, 600)  # Establecer tamaño mínimo
        
        # Crear frame principal con padding
        main_frame = ttk.Frame(window, padding=15)
        main_frame.pack(fill=BOTH, expand=YES)
        
        # Frame izquierdo para la vista previa (ocupando 70% del espacio)
        preview_frame = ttk.LabelFrame(
            main_frame,
            text="Vista Previa del Documento",
            padding=10
        )
        preview_frame.pack(side=LEFT, fill=BOTH, expand=YES, padx=(0, 10))
        
        # Contenedor para el canvas y scrollbars
        preview_container = ttk.Frame(preview_frame)
        preview_container.pack(fill=BOTH, expand=YES, padx=5, pady=5)
        
        # Scrollbars
        h_scrollbar = ttk.Scrollbar(preview_container, orient=HORIZONTAL)
        v_scrollbar = ttk.Scrollbar(preview_container, orient=VERTICAL)
        
        # Canvas con scrollbars
        self.preview_canvas = tk.Canvas(
            preview_container,
            bg='white',
            relief='solid',
            borderwidth=1,
            width=800,
            height=600,
            xscrollcommand=h_scrollbar.set,
            yscrollcommand=v_scrollbar.set
        )
        
        # Configurar scrollbars
        h_scrollbar.configure(command=self.preview_canvas.xview)
        v_scrollbar.configure(command=self.preview_canvas.yview)
        
        # Empaquetar elementos
        h_scrollbar.pack(side=BOTTOM, fill=X)
        v_scrollbar.pack(side=RIGHT, fill=Y)
        self.preview_canvas.pack(side=LEFT, fill=BOTH, expand=YES)
        
        # Variables para el zoom y pan
        self.zoom_factor = 1.0
        self.pan_start_x = None
        self.pan_start_y = None
        
        # Bindings para zoom y pan
        self.preview_canvas.bind('<ButtonPress-1>', self.start_pan)
        self.preview_canvas.bind('<B1-Motion>', self.pan_image)
        self.preview_canvas.bind('<ButtonRelease-1>', self.stop_pan)
        self.preview_canvas.bind('<MouseWheel>', self.zoom)
        self.preview_canvas.bind('<Button-4>', self.zoom)
        self.preview_canvas.bind('<Button-5>', self.zoom)
        
        # Frame derecho para datos
        input_frame = ttk.LabelFrame(
            main_frame,
            text="Datos del Documento",
            padding=10
        )
        input_frame.pack(side=RIGHT, fill=Y)
        
        # Etiqueta e instrucción
        instruction_label = ttk.Label(
            input_frame,
            text="Digite el identficador del documento en pantalla:",
            wraplength=250,
            justify="left"
        )
        instruction_label.pack(pady=(0, 10))
        
        # Frame para selección de formato
        format_frame = ttk.LabelFrame(
            input_frame,
            text="Formato del Documento",
            padding=10
        )
        format_frame.pack(pady=(0, 20))

        # ComboBox para formatos
        self.format_var = tk.StringVar(value="GCO-REG-099")
        self.format_combo = ttk.Combobox(
            format_frame,
            textvariable=self.format_var,
            values=["GCO-REG-099", "Otro"],
            state="readonly",
            width=20
        )
        self.format_combo.pack(pady=(0, 5))

        # Entry para formato manual (inicialmente deshabilitado)
        self.custom_format_var = tk.StringVar()
        self.custom_format_entry = ttk.Entry(
            format_frame,
            textvariable=self.custom_format_var,
            state="disabled",
            width=20
        )
        self.custom_format_entry.pack()

        # Vincular evento de cambio en el combobox
        self.format_combo.bind('<<ComboboxSelected>>', self.on_format_change)
        
        # Campo de entrada para la cédula
        self.cedula_var = tk.StringVar()
        cedula_entry = ttk.Entry(
            input_frame,
            textvariable=self.cedula_var,
            font=("Segoe UI", 12)
        )
        cedula_entry.pack(pady=(0, 20))

        cedula_entry.bind('<Return>', lambda event: self.relacionar_documento())
        
        # Botones
        relacionar_btn = ttk.Button(
            input_frame,
            text="Relacionar",
            command=self.relacionar_documento,
            bootstyle="success"
        )
        relacionar_btn.pack(pady=(0, 5), fill=X)
        
        cancelar_btn = ttk.Button(
            input_frame,
            text="Cancelar",
            command=lambda: window.destroy(),
            bootstyle="danger-outline"
        )
        cancelar_btn.pack(pady=5, fill=X)

        
        # Información del progreso
        self.progress_label = ttk.Label(
            input_frame,
            text="Documento 1 de 1",
            font=("Segoe UI", 10),
            foreground="gray"
        )
        self.progress_label.pack(pady=10)
        
        # Configurar evento para cuando el canvas esté listo
        self.preview_canvas.bind('<Configure>', self.on_canvas_configure)
        
        # Inicializar variables y cargar primer documento
        self.current_doc_index = 0
        self.canvas_configured = False
        self.preview_canvas.configure(scrollregion=(0, 0, 800, 600))
        window.after(500, self.load_document_preview)
        
    def on_format_change(self, event=None):
        """Maneja el cambio en el combobox de formato"""
        if self.format_var.get() == "Otro":
            self.custom_format_entry.configure(state="normal")
            self.custom_format_entry.focus()
        else:
            self.custom_format_entry.configure(state="disabled")
            self.custom_format_var.set("")

# Métodos para selección de archivos 
    def select_files(self, event=None): 
        """Manejar selección manual de archivos"""
        file_types = [
            ("Todos los archivos soportados", "*.pdf *.png *.jpg *.jpeg"),
            ("Archivos PDF", "*.pdf"),
            ("Archivos de Imagen", "*.png *.jpg *.jpeg")
        ]
        
        # Abrir diálogo de selección de archivos
        files = filedialog.askopenfilenames(
            title="Seleccionar Archivos",
            filetypes=file_types
        )
        
        # Si se seleccionaron archivos, procesarlos
        if files:
            self.process_files(files)
    
    def select_folder(self): 
        """Manejar selección de carpeta"""
        # Abrir diálogo de selección de carpeta
        folder = filedialog.askdirectory(
            title="Seleccionar Carpeta"
        )
        
        if folder:
            # Lista para almacenar los archivos encontrados
            files = []
            
            # Definir extensiones soportadas
            supported_extensions = ('.pdf', '.png', '.jpg', '.jpeg')
            
            # Buscar archivos en la carpeta y subcarpetas
            for root, _, filenames in os.walk(folder):
                for filename in filenames:
                    if filename.lower().endswith(supported_extensions):
                        # Construir ruta completa del archivo
                        file_path = os.path.join(root, filename)
                        files.append(file_path)
            
            # Si se encontraron archivos, procesarlos
            if files:
                self.process_files(files)
            else:
                self.status_var.set("No se encontraron archivos soportados en la carpeta seleccionada")
                messagebox.showinfo(
                    "Información",
                    "No se encontraron archivos soportados en la carpeta seleccionada."
                )
    
    def process_files(self, files): 
        """Procesar y validar archivos subidos"""
        added_count = 0
        
        for file_path in files:
            # Verificar que el archivo existe
            if not os.path.exists(file_path):
                print(f"Archivo no existe: {file_path}")
                continue
                    
            # Obtener información del archivo
            file_name = os.path.basename(file_path)
            file_ext = os.path.splitext(file_name)[1].lower()
            file_size = os.path.getsize(file_path)
            
            print(f"\nProcesando archivo: {file_name}")
            print(f"Extensión: {file_ext}")
            print(f"Tamaño: {file_size} bytes")
            
            # Validar tipo de archivo
            if not any(file_ext in exts for exts in self.supported_types.values()):
                messagebox.showerror(
                    "Error",
                    f"Tipo de archivo no soportado: {file_name}"
                )
                continue
            
            # Intentar leer el QR - Esta es la nueva sección
            print("Intentando leer código QR...")
            qr_content = self.read_qr_code(file_path)
            if qr_content is None:
                messagebox.showerror(
                    "Error",
                    f"No se pudo leer el código QR del archivo: {file_name}"
                )
                continue
            
            # Agregar a la lista si no está presente y si se pudo leer el QR
            if file_path not in self.uploaded_files:
                print(f"Agregando archivo a la lista: {file_path}")
                self.uploaded_files.append(file_path)
                added_count += 1
                
                # Formatear tamaño del archivo
                size_str = self.format_size(file_size)
                
                # Agregar a la tabla
                self.file_listbox.insert(
                    "",
                    END,
                    values=(file_name, file_ext[1:].upper(), size_str)
                )
                
                # Guardar el contenido del QR para uso posterior - Nueva sección
                if not hasattr(self, 'qr_contents'):
                    self.qr_contents = {}
                self.qr_contents[file_path] = qr_content
        
            # Actualizar estado y botón de registro
            if added_count > 0:
                self.status_var.set(
                    f"Se {'agregó' if added_count == 1 else 'agregaron'} "
                    f"{added_count} {'archivo nuevo' if added_count == 1 else 'archivos nuevos'}"
                )
                self.register_btn.configure(state="normal")
                print(f"Total de archivos agregados: {added_count}")
            else:
                self.status_var.set("No se agregaron archivos nuevos")
                print("No se agregaron nuevos archivos")
    
    def clear_files(self): 
        """Limpiar todos los archivos"""
        if self.uploaded_files:
            # Limpiar la lista de archivos
            self.uploaded_files.clear()
            
            # Limpiar la tabla de archivos
            self.file_listbox.delete(*self.file_listbox.get_children())
            
            # Actualizar mensaje de estado
            self.status_var.set("Se eliminaron todos los archivos")
            
            # Deshabilitar botón de registro
            self.register_btn.configure(state="disabled")
            
            # Cerrar la ventana de registro si está abierta
            for widget in self.root.winfo_children():
                if isinstance(widget, tk.Toplevel):
                    widget.destroy()
            
            # Cerrar cualquier documento PDF abierto
            if hasattr(self, 'pdf_document') and self.pdf_document:
                self.pdf_document.close()
                self.pdf_document = None

    def format_size(self, size): 
        """Convertir tamaño de archivo a formato legible por humanos"""
        # Lista de unidades de tamaño
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        
        # Comenzar con bytes
        index = 0
        size_float = float(size)
        
        # Ir dividiendo por 1024 hasta llegar a la unidad apropiada
        while size_float >= 1024 and index < len(units) - 1:
            size_float /= 1024
            index += 1
        
        # Redondear a un decimal y devolver con la unidad correspondiente
        return f"{size_float:.1f} {units[index]}"

#Métodos de vista previa 

    def load_document_preview(self): 
        """Cargar la vista previa del documento actual"""
        print("\n=== Iniciando carga de documento ===")
        
        # Verificar si hay archivos cargados
        if not hasattr(self, 'uploaded_files') or not self.uploaded_files:
            print("No hay archivos cargados")
            return
            
        # Verificar si el canvas está inicializado
        if not hasattr(self, 'preview_canvas'):
            print("Canvas no inicializado")
            return
            
        # Obtener dimensiones del canvas
        canvas_width = self.preview_canvas.winfo_width()
        canvas_height = self.preview_canvas.winfo_height()
        
        # Verificar dimensiones del canvas
        if canvas_width <= 1 or canvas_height <= 1:
            print(f"Canvas no tiene dimensiones válidas aún: {canvas_width}x{canvas_height}")
            # Establecer dimensiones mínimas
            self.preview_canvas.configure(width=800, height=600)
            canvas_width, canvas_height = 800, 600
        
        print(f"Dimensiones del canvas: {canvas_width}x{canvas_height}")
        
        # Cargar el documento actual si existe
        if self.current_doc_index < len(self.uploaded_files):
            file_path = self.uploaded_files[self.current_doc_index]
            
            # Verificar que el archivo existe
            if not os.path.exists(file_path):
                print(f"Error: El archivo no existe en la ruta: {file_path}")
                messagebox.showerror(
                    "Error",
                    f"No se puede encontrar el archivo: {os.path.basename(file_path)}"
                )
                return
                
            file_ext = os.path.splitext(file_path)[1].lower()
            print(f"Procesando archivo: {file_path}")
            print(f"Extensión: {file_ext}")
            
            try:
                # Cargar según el tipo de archivo
                if file_ext == '.pdf':
                    self.load_pdf_preview(file_path)
                elif file_ext in ['.png', '.jpg', '.jpeg']:
                    self.load_image_preview(file_path)
                else:
                    print(f"Extensión no soportada: {file_ext}")
                    messagebox.showerror(
                        "Error",
                        f"Tipo de archivo no soportado: {file_ext}"
                    )
                    return
                    
                # Actualizar etiqueta de progreso
                total_docs = len(self.uploaded_files)
                self.progress_label.configure(
                    text=f"Documento {self.current_doc_index + 1} de {total_docs}"
                )
                
                # Configurar región de scroll del canvas
                self.preview_canvas.configure(scrollregion=self.preview_canvas.bbox("all"))
                
            except Exception as e:
                print(f"Error al cargar vista previa: {str(e)}")
                import traceback
                traceback.print_exc()
                messagebox.showerror(
                    "Error",
                    f"Error al cargar la vista previa: {str(e)}"
                )
        
    def load_pdf_preview(self, file_path): 
        """Cargar vista previa de PDF"""
        try:
            # Abrir el documento PDF
            doc = fitz.open(file_path)
            print(f"PDF abierto: {file_path}")
            print(f"Número de páginas: {len(doc)}")
            
            # Obtener primera página
            page = doc[0]
            
            # Usar una matriz de transformación para mejor calidad
            zoom_matrix = fitz.Matrix(2, 2)  # Factor de zoom 2x
            pix = page.get_pixmap(matrix=zoom_matrix)
            
            # Convertir a formato PIL
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # Guardar imagen original y sus dimensiones
            self.current_image = img
            self.original_image_size = img.size
            
            # Obtener dimensiones del canvas
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()
            
            print(f"Dimensiones del canvas: {canvas_width}x{canvas_height}")
            print(f"Dimensiones originales de la imagen: {img.size}")
            
            # Crear una copia para el redimensionamiento
            img_display = img.copy()
            
            # Ajustar tamaño manteniendo proporción
            img_display.thumbnail((canvas_width, canvas_height))
            
            print(f"Dimensiones después del ajuste: {img_display.size}")
            
            # Convertir a PhotoImage
            photo = ImageTk.PhotoImage(img_display)
            
            # Limpiar canvas y mostrar nueva imagen
            self.preview_canvas.delete("all")
            
            # Calcular posición centrada
            x = canvas_width // 2
            y = canvas_height // 2
            
            # Crear imagen en el canvas
            self.preview_canvas.create_image(
                x, y,
                image=photo,
                anchor="center",
                tags="preview"
            )
            
            # Mantener referencia a la imagen
            self.preview_canvas.image = photo
            
            # Actualizar región de scroll
            self.preview_canvas.configure(scrollregion=self.preview_canvas.bbox("all"))
            
            # Resetear factor de zoom
            self.zoom_factor = 1.0
            
            # Cerrar el documento PDF
            doc.close()
            
            print("Vista previa de PDF cargada exitosamente")
            
        except Exception as e:
            print(f"Error al cargar PDF: {str(e)}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Error al cargar PDF: {str(e)}")
    
    def load_image_preview(self, file_path): 
        """Cargar vista previa de imagen"""
        try:
            print(f"Cargando imagen: {file_path}")
            
            # Abrir la imagen
            img = Image.open(file_path)
            
            # Guardar imagen original y sus dimensiones
            self.current_image = img
            self.original_image_size = img.size
            
            print(f"Dimensiones originales de la imagen: {img.size}")
            
            # Obtener dimensiones del canvas
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()
            
            print(f"Dimensiones del canvas: {canvas_width}x{canvas_height}")
            
            # Crear una copia para el redimensionamiento
            img_display = img.copy()
            
            # Ajustar tamaño manteniendo proporción
            img_display.thumbnail((canvas_width, canvas_height))
            
            print(f"Dimensiones después del ajuste: {img_display.size}")
            
            # Convertir a PhotoImage
            photo = ImageTk.PhotoImage(img_display)
            
            # Limpiar canvas
            self.preview_canvas.delete("all")
            
            # Calcular posición centrada
            x = canvas_width // 2
            y = canvas_height // 2
            
            # Crear imagen en el canvas
            self.preview_canvas.create_image(
                x, y,
                image=photo,
                anchor="center",
                tags="preview"
            )
            
            # Mantener referencia a la imagen
            self.preview_canvas.image = photo
            
            # Actualizar región de scroll
            self.preview_canvas.configure(scrollregion=self.preview_canvas.bbox("all"))
            
            # Resetear factor de zoom
            self.zoom_factor = 1.0
            
            print("Vista previa de imagen cargada exitosamente")
            
        except Exception as e:
            print(f"Error al cargar imagen: {str(e)}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Error al cargar imagen: {str(e)}")
    
    def on_canvas_configure(self, event): 
        """Evento que se dispara cuando el canvas está listo o se redimensiona"""
        # Si el canvas no se ha configurado antes
        if not hasattr(self, 'canvas_configured'):
            self.canvas_configured = True
            print("Primera configuración del canvas")
            
            # Obtener dimensiones actuales
            width = self.preview_canvas.winfo_width()
            height = self.preview_canvas.winfo_height()
            print(f"Dimensiones del canvas: {width}x{height}")
            
            # Si las dimensiones son válidas, cargar la vista previa
            if width > 1 and height > 1:
                print("Iniciando carga inicial del documento")
                # Usar after para dar tiempo a que la interfaz se actualice
                self.preview_canvas.after(100, self.load_document_preview)
            else:
                print("Dimensiones del canvas no válidas, esperando...")
                # Intentar de nuevo después de un momento
                self.preview_canvas.after(100, lambda: self.on_canvas_configure(event))
        
        # Si hay una imagen cargada y el canvas se redimensiona
        elif hasattr(self, 'current_image') and hasattr(self, 'original_image_size'):
            # Recargar la imagen con las nuevas dimensiones
            self.load_document_preview()
    

#Métodos para zoom y paneo 

    def start_pan(self, event): 
        """Iniciar el arrastre de la imagen"""
        # Verificar si hay una imagen cargada
        if not hasattr(self, 'current_image'):
            return
            
        # Guardar la posición inicial del cursor
        self.pan_start_x = event.x
        self.pan_start_y = event.y
        
        # Marcar el punto de inicio para el escaneo
        self.preview_canvas.scan_mark(event.x, event.y)
    
    def pan_image(self, event): 
        """Arrastrar la imagen en el canvas"""
        # Verificar si el arrastre se ha iniciado
        if not hasattr(self, 'pan_start_x') or self.pan_start_x is None:
            return
            
        # Verificar si hay una imagen cargada
        if not hasattr(self, 'current_image'):
            return
            
        # Calcular el desplazamiento desde el punto inicial
        # El parámetro gain=1 mantiene una relación 1:1 entre el movimiento del mouse y la imagen
        self.preview_canvas.scan_dragto(event.x, event.y, gain=1)
    
    def stop_pan(self, event): 
        """Detener el arrastre de la imagen"""
        # Limpiar las coordenadas de inicio del arrastre
        self.pan_start_x = None
        self.pan_start_y = None
    
    def zoom(self, event): 
        """Aplicar zoom a la imagen"""
        # Verificar si hay una imagen cargada
        if not hasattr(self, 'current_image'):
            return

        # Obtener el factor de zoom actual
        if not hasattr(self, 'zoom_factor'):
            self.zoom_factor = 1.0
        
        # Determinar la dirección del zoom basado en el evento
        if event.num == 5 or event.delta < 0:  # Zoom out
            self.zoom_factor = max(0.1, self.zoom_factor * 0.9)
        else:  # Zoom in
            self.zoom_factor = min(5.0, self.zoom_factor * 1.1)
        
        # Obtener dimensiones actuales del canvas
        canvas_width = self.preview_canvas.winfo_width()
        canvas_height = self.preview_canvas.winfo_height()
        
        # Calcular nuevas dimensiones
        new_width = int(self.original_image_size[0] * self.zoom_factor)
        new_height = int(self.original_image_size[1] * self.zoom_factor)
        
        try:
            # Redimensionar imagen manteniendo calidad
            img_resized = self.current_image.resize(
                (new_width, new_height), 
                Image.Resampling.LANCZOS
            )
            
            # Convertir a formato PhotoImage
            photo = ImageTk.PhotoImage(img_resized)
            
            # Limpiar canvas
            self.preview_canvas.delete("all")
            
            # Crear nueva imagen centrada
            self.preview_canvas.create_image(
                canvas_width//2,
                canvas_height//2,
                image=photo,
                anchor="center",
                tags="preview"
            )
            
            # Mantener referencia
            self.preview_canvas.image = photo
            
            # Actualizar región de scroll
            self.preview_canvas.configure(scrollregion=self.preview_canvas.bbox("all"))
            
        except Exception as e:
            print(f"Error al aplicar zoom: {str(e)}")
            import traceback
            traceback.print_exc()
    

#Métodos para el registro de documentos 

    def open_register_window(self): 
        """Abrir ventana de registro de documentos"""
        # Verificar si hay archivos para registrar
        if not self.uploaded_files:
            messagebox.showwarning(
                "Advertencia",
                "Por favor, seleccione al menos un documento para registrar."
            )
            return

        # Crear nueva ventana
        register_window = tk.Toplevel(self.root)
        register_window.title("Registro de Documento")
        register_window.geometry("1200x700")
        
        # Hacer que la ventana principal no sea interactuable mientras está abierta la de registro
        register_window.transient(self.root)
        register_window.grab_set()
        
        # Configurar que al cerrar la ventana se limpie apropiadamente
        register_window.protocol(
            "WM_DELETE_WINDOW",
            lambda: self.close_register_window(register_window)
        )
        
        # Establecer tamaño mínimo
        register_window.minsize(1000, 600)
        
        # Configurar la ventana de registro
        self.setup_register_window(register_window)
        
        # Centrar la ventana en la pantalla
        self.center_window(register_window)
        
    def center_window(self, window):
        """Centrar una ventana en la pantalla"""
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')

    def close_register_window(self, window):
        """Cerrar la ventana de registro apropiadamente"""
        # Liberar el grab
        window.grab_release()
        
        # Cerrar la ventana
        window.destroy()
        
        # Limpiar variables si es necesario
        if hasattr(self, 'current_image'):
            del self.current_image
        if hasattr(self, 'original_image_size'):
            del self.original_image_size
        if hasattr(self, 'zoom_factor'):
            del self.zoom_factor
        
        # Devolver el foco a la ventana principal
        self.root.focus_set()
    
    def relacionar_documento(self): 
        """Procesar la relación del documento con la cédula"""
        # Evitar múltiples ejecuciones simultáneas
        if self.is_processing:
            return
                
        try:
            self.is_processing = True
            cedula = self.cedula_var.get().strip()
            
            if not cedula:
                messagebox.showwarning(
                    "Advertencia",
                    "Por favor, digite el número de cédula."
                )
                return
                    
            if not cedula.isdigit():
                messagebox.showwarning(
                    "Advertencia",
                    "La cédula debe contener solo números."
                )
                return

            # Obtener el formato seleccionado
            formato = self.format_var.get()
            if formato == "Otro":
                formato = self.custom_format_var.get().strip()
                if not formato:
                    messagebox.showwarning(
                        "Advertencia",
                        "Por favor, ingrese un formato válido."
                    )
                    return

            # Encontrar la ventana de registro
            register_window = None
            for widget in self.root.winfo_children():
                if isinstance(widget, tk.Toplevel):
                    register_window = widget
                    break

            if register_window:
                # Crear ventana de bloqueo modal
                blocker = tk.Toplevel(register_window)
                blocker.transient(register_window)
                blocker.grab_set()
                blocker.withdraw()
                register_window.config(cursor="wait")

            try:
                current_file = self.uploaded_files[self.current_doc_index]
                qr_content = self.qr_contents[current_file]
                new_filepath = self.store_document(current_file, cedula, qr_content, formato)
                
                if register_window:
                    register_window.config(cursor="")
                    blocker.destroy()
                
                messagebox.showinfo(
                    "Éxito",
                    f"Documento relacionado exitosamente con la cédula: {cedula} y formato: {formato}"
                )
                
                self.cedula_var.set("")
                self.current_doc_index += 1
                
                if self.current_doc_index < len(self.uploaded_files):
                    self.load_document_preview()
                else:
                    messagebox.showinfo(
                        "Completado",
                        "Todos los documentos han sido procesados."
                    )
                    
                    if register_window:
                        self.clear_files()
                        register_window.destroy()
                        
            except Exception as e:
                if register_window:
                    register_window.config(cursor="")
                    blocker.destroy()
                raise e
                    
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Error al procesar el documento: {str(e)}"
            )
        finally:
            # Asegurarnos de que el flag se desactive incluso si hay errores
            self.is_processing = False
# Métodos para lectura de QR's 
    def read_qr_from_image(self, image_path):
        """Leer código QR de una imagen"""
        try:
            # Leer la imagen
            image = cv2.imread(image_path)
            if image is None:
                print("No se pudo cargar la imagen")
                return None
                
            # Decodificar QR
            decoded_objects = decode(image)
            
            # Verificar si se encontró algún QR
            if not decoded_objects:
                print("No se encontró código QR en la imagen")
                return None
                
            # Retornar el contenido del primer QR encontrado
            qr_data = decoded_objects[0].data.decode('utf-8')
            print(f"QR leído exitosamente: {qr_data}")
            return qr_data
            
        except Exception as e:
            print(f"Error al leer QR de imagen: {str(e)}")
            return None
        
    def read_qr_from_pdf(self, pdf_path):
        """Leer código QR de un PDF"""
        try:
            # Abrir el documento PDF
            doc = fitz.open(pdf_path)
            print(f"PDF abierto: {pdf_path}")
            
            # Obtener primera página
            page = doc[0]
            
            # Crear una imagen de la página
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # Factor de zoom 2x para mejor detección
            
            # Convertir a formato que OpenCV pueda leer
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            img_array = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            
            # Decodificar QR
            decoded_objects = decode(img_array)
            
            # Cerrar el documento
            doc.close()
            
            # Verificar si se encontró algún QR
            if not decoded_objects:
                print("No se encontró código QR en el PDF")
                return None
                
            # Retornar el contenido del primer QR encontrado
            qr_data = decoded_objects[0].data.decode('utf-8')
            print(f"QR leído exitosamente del PDF: {qr_data}")
            return qr_data
            
        except Exception as e:
            print(f"Error al leer QR del PDF: {str(e)}")
            return None
        
    

    def read_qr_code(self, file_path):
        """Leer código QR de un archivo (imagen o PDF)
    
        Este método determina el tipo de archivo y utiliza el método 
        apropiado para leer el código QR. Actúa como un punto de entrada
        unificado para la lectura de QR independientemente del tipo de archivo.
        """
        try:
            # Determinamos el tipo de archivo por su extensión
            file_ext = os.path.splitext(file_path)[1].lower()
            print(f"Procesando archivo: {file_path}")
            print(f"Tipo de archivo detectado: {file_ext}")
            
            # Seleccionamos el método apropiado según la extensión
            if file_ext == '.pdf':
                print("Iniciando lectura de QR desde PDF...")
                qr_content = self.read_qr_from_pdf(file_path)
            elif file_ext in ['.png', '.jpg', '.jpeg']:
                print("Iniciando lectura de QR desde imagen...")
                qr_content = self.read_qr_from_image(file_path)
            else:
                print(f"Tipo de archivo no soportado para lectura de QR: {file_ext}")
                return None
                
            # Verificamos si se pudo leer el QR
            if qr_content is None:
                print(f"No se pudo leer el código QR del archivo: {file_path}")
            else:
                print(f"QR leído exitosamente: {qr_content}")
                
            return qr_content
            
        except Exception as e:
            print(f"Error al procesar el archivo para lectura de QR: {str(e)}")
            return None

    def run(self):
        """Iniciar la aplicación"""
        self.root.mainloop()

# Métodos para archivación de relaciones 

    def setup_storage(self):
        """
        Configurar la estructura de almacenamiento para documentos y registros.
        
        Este método crea una estructura organizada de carpetas y archivos:
        - Una carpeta principal 'Documentos_Procesados'
        - Una subcarpeta 'Documentos' para almacenar los archivos escaneados
        - Un archivo Excel 'registro.xlsx' para mantener el control de las relaciones
        
        La estructura quedará así:
        Documentos_Procesados/
        ├── Documentos/
        │   └── (archivos escaneados)
        └── registro.xlsx
        """
        try:
            # Creamos la carpeta principal junto al script
            # os.path.dirname(__file__) nos da la ubicación del script actual
            self.storage_path = os.path.join(os.path.dirname(__file__), 'Documentos_Procesados')
            os.makedirs(self.storage_path, exist_ok=True)
            
            # Creamos la subcarpeta para documentos
            self.docs_path = os.path.join(self.storage_path, 'Documentos')
            os.makedirs(self.docs_path, exist_ok=True)
            
            # Definimos la ruta del archivo Excel
            self.excel_path = os.path.join(self.storage_path, 'registro.xlsx')
            
            # Creamos o cargamos el Excel
            if not os.path.exists(self.excel_path):
                # Si no existe, creamos un nuevo Excel con las columnas necesarias
                df = pd.DataFrame(columns=[
                    'Código QR',
                    'Número de Cédula',
                    'Ruta del Archivo',
                    'Fecha de Registro'
                ])
                # Guardamos el Excel sin índice numérico
                df.to_excel(self.excel_path, index=False)
                
            print(f"Almacenamiento configurado exitosamente en: {self.storage_path}")
            
        except Exception as e:
            print(f"Error al configurar el almacenamiento: {str(e)}")
            # Propagamos el error para que pueda ser manejado por el código que llama a este método
            raise
    def store_document(self, file_path, cedula, qr_content, formato):
        
        print("Drive manager:", hasattr(self, 'drive_manager'))
        print(f"Formato en store_document: {formato}")
        try:
            print("\nIniciando almacenamiento de documento...")
            print(f"Archivo: {file_path}")
            print(f"Cédula: {cedula}")
            print(f"Formato: {formato}")
            
            # Subir archivo a Google Drive
            print("Subiendo archivo a Google Drive...")
            file_id = self.drive_manager.upload_document(file_path, cedula, formato)
            
            if not file_id:
                raise Exception("Error al subir el archivo a Google Drive")

            print("Archivo subido exitosamente a Drive")
            print("Intentando registrar en spreadsheet...")

            try:
                # Registrar en el spreadsheet usando el drive manager
                new_row = {
                    'Código QR': qr_content,
                    'Número de Cédula': cedula,
                    'Ruta del Archivo': f"https://drive.google.com/file/d/{file_id}/view",
                    'Fecha de Registro': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                print("Datos a registrar:", new_row)
                result = self.drive_manager.add_record(
                    qr_code=qr_content,
                    cedula=cedula,
                    file_path=f"https://drive.google.com/file/d/{file_id}/view",
                    fecha=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
                
                if not result:
                    raise Exception("Error al registrar en el spreadsheet")
                    
                print("Registro en spreadsheet exitoso")
                
            except Exception as e:
                print(f"Error específico al registrar en spreadsheet: {str(e)}")
                raise
                
            print("Proceso completado exitosamente")
            return file_id
        
                
        except Exception as e:
            print(f"Error al almacenar documento: {str(e)}")
            raise


    def update_local_excel(self, qr_content, cedula, filepath, fecha=None):
        """
        Actualiza el Excel local como respaldo o cuando Google Drive no está disponible.
        """
        try:
            if fecha is None:
                fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
            df = pd.read_excel(self.excel_path)
            new_row = {
                'Código QR': qr_content,
                'Número de Cédula': cedula,
                'Ruta del Archivo': os.path.relpath(filepath, self.storage_path),
                'Fecha de Registro': fecha
            }
            
            df.loc[len(df)] = new_row
            df.to_excel(self.excel_path, index=False)
            print("Registro guardado en Excel local")
            
        except Exception as e:
            print(f"Error al actualizar Excel local: {str(e)}")
            raise

class GoogleDriveManager:
    """
    Clase para manejar todas las interacciones con Google Drive y Google Sheets.
    Esta clase se encarga de:
    - Mantener la conexión con Google Drive
    - Manejar la hoja de cálculo de registros
    - Gestionar las operaciones de lectura/escritura
    """
    def __init__(self, credentials_path):
        # Definimos los permisos que necesitamos
        self.SCOPES = [
            'https://www.googleapis.com/auth/drive.file',
            'https://www.googleapis.com/auth/spreadsheets'
        ]
        
        try:
            # Cargar las credenciales desde el archivo
            print(f"Buscando credentials.json en: {os.path.abspath(credentials_path)}")
            self.credentials = service_account.Credentials.from_service_account_file(
                credentials_path,
                scopes=self.SCOPES
            )
            
            # Inicializar los servicios de Google
            self.drive_service = build('drive', 'v3', credentials=self.credentials)
            self.sheets_service = build('sheets', 'v4', credentials=self.credentials)
            self.setup_spreadsheet()  # Si ya tienes esto
            self.setup_drive_folder()  # Añade esta línea
            
            # ID de la hoja de cálculo (se establecerá al crear o encontrar la hoja)
            self.spreadsheet_id = None
            
            print("Conexión con Google Drive establecida exitosamente")
            
        except Exception as e:
            print(f"Error al inicializar Google Drive: {str(e)}")
            raise

    def setup_spreadsheet(self, spreadsheet_name="Registro_Documentos"):
    
        """
        Configura la hoja de cálculo para el registro de documentos.
        Esta función busca una hoja existente o crea una nueva si no existe.
        También configura el formato inicial si es una hoja nueva.
        
        Args:
            spreadsheet_name (str): Nombre de la hoja de cálculo. Por defecto es "Registro_Documentos"
        
        Returns:
            bool: True si la operación fue exitosa, False en caso contrario
        """
        
        try:
            print("\nBuscando o creando spreadsheet...")
            results = self.drive_service.files().list(
                q=f"name='{spreadsheet_name}' and mimeType='application/vnd.google-apps.spreadsheet'",
                spaces='drive'
            ).execute()
            
            existing_files = results.get('files', [])
            
            if existing_files:
                self.spreadsheet_id = existing_files[0]['id']
                print(f"Spreadsheet encontrado. ID: {self.spreadsheet_id}")
            else:
                spreadsheet = {
                    'properties': {'title': spreadsheet_name},
                    'sheets': [
                        {'properties': {'title': 'Registros'}},
                        {'properties': {'title': 'QR_Generados'}}
                    ]
                }
                
                spreadsheet = self.sheets_service.spreadsheets().create(
                    body=spreadsheet,
                    fields='spreadsheetId'
                ).execute()
                
                self.spreadsheet_id = spreadsheet.get('spreadsheetId')
                
                # Configurar encabezados para Registros
                headers_registros = [['Código QR', 'Número de Cédula', 'Ruta del Archivo', 'Fecha de Registro']]
                self.sheets_service.spreadsheets().values().update(
                    spreadsheetId=self.spreadsheet_id,
                    range='Registros!A1:D1',
                    valueInputOption='RAW',
                    body={'values': headers_registros}
                ).execute()

                # Configurar encabezados para QR_Generados
                headers_qr = [['ID del QR', 'Código de Documento', 'Fecha de Generación']]
                self.sheets_service.spreadsheets().values().update(
                    spreadsheetId=self.spreadsheet_id,
                    range='QR_Generados!A1:C1',
                    valueInputOption='RAW',
                    body={'values': headers_qr}
                ).execute()

            # Verificar si la hoja QR_Generados existe
            spreadsheet = self.sheets_service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id
            ).execute()
            
            sheet_exists = any(sheet['properties']['title'] == 'QR_Generados' 
                                for sheet in spreadsheet['sheets'])
            
            if not sheet_exists:
                request = {
                    'addSheet': {
                        'properties': {
                            'title': 'QR_Generados',
                            'gridProperties': {
                                'rowCount': 1000,
                                'columnCount': 3
                            }
                        }
                    }
                }
                
                self.sheets_service.spreadsheets().batchUpdate(
                    spreadsheetId=self.spreadsheet_id,
                    body={'requests': [request]}
                ).execute()
                
                headers_qr = [['ID del QR', 'Código de Documento', 'Fecha de Generación']]
                self.sheets_service.spreadsheets().values().update(
                    spreadsheetId=self.spreadsheet_id,
                    range='QR_Generados!A1:C1',
                    valueInputOption='RAW',
                    body={'values': headers_qr}
                ).execute()

            # Configurar permisos
            try:
                permission = {
                    'type': 'anyone',
                    'role': 'writer',
                    'allowFileDiscovery': False
                }
                
                self.drive_service.permissions().create(
                    fileId=self.spreadsheet_id,
                    body=permission
                ).execute()
                
                print("\nInformación de acceso al spreadsheet:")
                print(f"URL: https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}")
                print("El archivo ahora debería ser accesible con el enlace")
                
            except Exception as e:
                print(f"Error al configurar permisos: {str(e)}")

            return True
            
        except Exception as e:
            print(f"Error configurando spreadsheet: {str(e)}")
            return False
                
    def share_spreadsheet(self, email):
        """Comparte el spreadsheet con un usuario específico"""
        try:
            permission = {
                'type': 'user',
                'role': 'writer',
                'emailAddress': email
            }
            
            self.drive_service.permissions().create(
                fileId=self.spreadsheet_id,
                body=permission,
                sendNotificationEmail=True
            ).execute()
            
            print(f"Spreadsheet compartido exitosamente con {email}")
            return True
        except Exception as e:
            print(f"Error al compartir spreadsheet: {str(e)}")
            return False

    def add_record(self, qr_code, cedula, file_path, fecha):
        """
        Agrega un nuevo registro a la hoja de cálculo.
        """
        try:
            values = [[qr_code, cedula, file_path, fecha]]
            
            result = self.sheets_service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range='Registros!A:D',
                valueInputOption='USER_ENTERED',
                insertDataOption='INSERT_ROWS',
                body={'values': values}
            ).execute()
            
            print(f"Registro agregado exitosamente: {result.get('updates').get('updatedRange')}")
            return True
            
        except Exception as e:
            print(f"Error al agregar registro: {str(e)}")
            return False
        

    def setup_drive_folder(self, folder_name="Documentos_Escaneados"):
        """
        Crea o encuentra la carpeta para almacenar documentos en Google Drive y configura
        sus permisos para garantizar el acceso adecuado.
        """
        try:
            print("\nConfigurando carpeta en Google Drive...")
            
            # Primero buscamos si la carpeta ya existe
            results = self.drive_service.files().list(
                q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'",
                spaces='drive'
            ).execute()
            
            existing_folders = results.get('files', [])
            
            if existing_folders:
                # Si la carpeta existe, usamos esa
                self.folder_id = existing_folders[0]['id']
                print(f"Carpeta existente encontrada. ID: {self.folder_id}")
            else:
                # Si no existe, creamos una nueva
                folder_metadata = {
                    'name': folder_name,
                    'mimeType': 'application/vnd.google-apps.folder',
                    # Configurar permisos iniciales para que sea visible
                    'permissionIds': ['anyoneWithLink'],
                    'permissions': [{
                        'type': 'anyone',
                        'role': 'writer',
                        'allowFileDiscovery': False
                    }]
                }
                
                folder = self.drive_service.files().create(
                    body=folder_metadata,
                    fields='id, webViewLink'
                ).execute()
                
                self.folder_id = folder.get('id')
                print(f"Nueva carpeta creada. ID: {self.folder_id}")

            # Asegurarnos de que los permisos estén configurados correctamente
            permission = {
                'type': 'anyone',  # Permite acceso a cualquiera con el enlace
                'role': 'writer',  # Permite modificaciones
                'allowFileDiscovery': False  # La carpeta no aparece en búsquedas
            }
            
            # Crear o actualizar los permisos
            self.drive_service.permissions().create(
                fileId=self.folder_id,
                body=permission
            ).execute()
            
            # Obtener y mostrar el enlace directo
            file = self.drive_service.files().get(
                fileId=self.folder_id,
                fields='webViewLink'
            ).execute()
            
            print("\nInformación de acceso a la carpeta:")
            print(f"URL: {file['webViewLink']}")
            print("La carpeta ahora debería ser accesible con este enlace")
            
            return True
            
        except Exception as e:
            print(f"Error al configurar carpeta en Drive: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        
    def upload_document(self, file_path, cedula, formato):
        """
        Sube un documento a Google Drive usando un formato de nombre estandarizado.
        
        El nombre del archivo sigue el patrón: {formato}_{cedula}.extension
        Por ejemplo: GCO-REG-099_123456789.pdf
        
        Args:
            file_path (str): Ruta del archivo a subir
            cedula (str): Número de cédula asociado al documento
            formato (str): Código del formato del documento. Por defecto "GCO-REG-099"
        
        Returns:
            str: ID del archivo en Google Drive si la subida fue exitosa, None en caso contrario
        """
        """Sube un documento a Google Drive usando un formato de nombre estandarizado"""
        """Sube un documento a Google Drive usando un formato estandarizado"""
        try:
            
            print(f"Formato en upload_document: {formato}")  # Añadir este print
            print(f"Tipo de dato formato: {type(formato)}")
            # Obtener la extensión del archivo original
            original_name = os.path.basename(file_path)
            file_ext = os.path.splitext(original_name)[1]
            
            # Crear el nuevo nombre siguiendo el formato establecido e incluyendo timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            new_filename = f"{formato}_{cedula}_{timestamp}{file_ext}"
            
            # Preparar metadata del archivo incluyendo información del formato
            file_metadata = {
                'name': new_filename,
                'parents': [self.folder_id],
                'properties': {
                    'cedula': cedula,
                    'formato': formato,
                    'fecha_registro': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'nombre_original': original_name
                }
            }
            
            # Preparar el archivo para subir
            media = MediaFileUpload(
                file_path,
                resumable=True
            )
            
            # Subir el archivo
            print(f"\nSubiendo archivo {new_filename}...")
            # Debug para verificar que llega el formato
            print(f"Subiendo documento con formato: {formato}")
            file = self.drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,name,webViewLink'
            ).execute()
            
            print(f"Archivo subido exitosamente:")
            print(f"- Nombre: {file.get('name')}")
            print(f"- ID: {file.get('id')}")
            
            return file.get('id')
            
        except Exception as e:
            print(f"Error al subir documento: {str(e)}")
            return None
    def download_file(self, file_id, destination_folder):
        """Descarga un archivo de Google Drive"""
        try:
            file_metadata = self.drive_service.files().get(
                fileId=file_id,
                fields='name'
            ).execute()
            
            destination_path = os.path.join(
                destination_folder,
                file_metadata['name']
            )
            
            request = self.drive_service.files().get_media(fileId=file_id)
            with open(destination_path, 'wb') as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while not done:
                    _, done = downloader.next_chunk()
            
            return True
            
        except Exception as e:
            print(f"Error al descargar archivo {file_id}: {str(e)}")
            raise
    
    def add_qr_record(self, qr_id, formato, fecha=None):
        """Registra un QR generado en el spreadsheet"""
        if fecha is None:
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        values = [[qr_id, formato, fecha]]
        
        try:
            result = self.sheets_service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range='QR_Generados!A:C',
                valueInputOption='USER_ENTERED',
                insertDataOption='INSERT_ROWS',
                body={'values': values}
            ).execute()
            return True
        except Exception as e:
            print(f"Error al registrar QR: {str(e)}")
            return False

class LoadingDialog:
    """
    Diálogo que muestra una animación de carga mientras se procesa un archivo.
    Este diálogo bloquea la interacción con la ventana principal hasta que
    se complete la operación.
    """
    def __init__(self, parent):
        # Crear una ventana de diálogo modal
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Procesando")
        
        # Configurar como modal y sin botones de ventana
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)
        
        # Eliminar botones de la ventana
        self.dialog.overrideredirect(True)
        
        # Centrar en la pantalla
        window_width = 300
        window_height = 100
        screen_width = parent.winfo_screenwidth()
        screen_height = parent.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.dialog.geometry(f'{window_width}x{window_height}+{x}+{y}')
        
        # Crear y configurar widgets
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill=BOTH, expand=YES)
        
        # Mensaje
        self.message = ttk.Label(
            frame,
            text="Registrando documento...",
            font=("Segoe UI", 10)
        )
        self.message.pack(pady=(0, 10))
        
        # Barra de progreso
        self.progress = ttk.Progressbar(
            frame,
            mode='indeterminate',
            length=200
        )
        self.progress.pack()
        
        # Iniciar animación
        self.progress.start(10)
        
        # Actualizar la interfaz
        self.dialog.update()
    
    def update_message(self, message):
        """Actualiza el mensaje mostrado en el diálogo"""
        self.message.config(text=message)
        self.dialog.update()
    
    def close(self):
        """Cierra el diálogo de carga"""
        self.progress.stop()
        self.dialog.destroy()




