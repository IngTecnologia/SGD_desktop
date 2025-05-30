import tkinter as tk
from tkinter import messagebox, filedialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from document_register import GoogleDriveManager
from googleapiclient.http import MediaIoBaseDownload
from datetime import datetime
import os 
import asyncio
import fitz
from PIL import Image, ImageTk

class DocumentSearch:
    def __init__(self, parent=None, drive_manager=None):
        """
        Inicializa la ventana de búsqueda de documentos.
        
        Args:
            parent: Ventana padre (menú principal). Si no se proporciona,
                el módulo funciona como aplicación independiente.
            drive_manager: Instancia de GoogleDriveManager ya inicializada
        """
        # Guardar referencia a la ventana padre y drive_manager
        self.parent = parent
        self.drive_manager = drive_manager
        
        # Crear la ventana principal de búsqueda
        self.window = ttk.Toplevel(parent) if parent else ttk.Window()
        self.window.title("Búsqueda de Documentos")
        
        # Configurar tamaño y posición de la ventana principal
        window_width = 1000
        window_height = 600
        
        # Establecer tamaño mínimo
        self.window.minsize(1000, 600)
        
        # Centrar la ventana principal
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.window.geometry(f'{window_width}x{window_height}+{x}+{y}')
        
        # Si hay padre, hacer la ventana modal
        if parent:
            self.window.transient(parent)
            self.window.grab_set()
        
        # Configurar la interfaz principal
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la interfaz de usuario del buscador"""
        main_frame = ttk.Frame(self.window, padding=20)
        main_frame.pack(fill=BOTH, expand=YES)
        
        # Título
        title_label = ttk.Label(
            main_frame,
            text="Búsqueda de Documentos",
            font=("Segoe UI", 24),
            bootstyle="primary"
        )
        title_label.pack(pady=(0, 30))
        
        # Frame de búsqueda
        search_frame = ttk.LabelFrame(
            main_frame,
            text="Criterios de Búsqueda",
            padding=15
        )
        search_frame.pack(fill=X, pady=(0, 20))
        
        input_frame = ttk.Frame(search_frame)
        input_frame.pack(fill=X)
        
        # Radio buttons para tipo de búsqueda
        self.search_type = tk.StringVar(value="cedula")
        type_frame = ttk.LabelFrame(
            input_frame,
            text="Buscar por",
            padding=10
        )
        type_frame.pack(side=LEFT, padx=(0, 15))
        
        ttk.Radiobutton(
            type_frame,
            text="Identificador",
            value="cedula",
            variable=self.search_type,
            command=self.on_search_type_change,
            padding=5
        ).pack(side=LEFT, padx=5)
        
        ttk.Radiobutton(
            type_frame,
            text="Nombre",
            value="nombre",
            variable=self.search_type,
            command=self.on_search_type_change,
            padding=5
        ).pack(side=LEFT, padx=5)
        
        # Campo de búsqueda
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(
            input_frame,
            textvariable=self.search_var,
            font=("Segoe UI", 12),
            width=40
        )
        self.search_entry.pack(side=LEFT, fill=X, expand=YES)
        self.search_entry.bind('<Return>', lambda event: self.perform_search())
        
        # Botón buscar
        search_button = ttk.Button(
            input_frame,
            text="Buscar",
            command=self.perform_search,
            bootstyle="primary",
            width=15
        )
        search_button.pack(side=LEFT, padx=10)
        
        # Frame de resultados
        results_frame = ttk.LabelFrame(
            main_frame,
            text="Documentos Encontrados",
            padding=15
        )
        results_frame.pack(fill=BOTH, expand=YES)
        
        # Treeview para resultados
        self.results_tree = ttk.Treeview(
            results_frame,
            columns=("Selección", "Fecha", "Nombre", "Cédula", "Vista Previa"),
            show="headings",
            selectmode="browse"
        )
        
        # Configurar columnas
        self.results_tree.heading("Selección", text="✓")
        self.results_tree.heading("Fecha", text="Fecha de Registro")
        self.results_tree.heading("Nombre", text="Nombre del Documento")
        self.results_tree.heading("Cédula", text="Cédula")
        self.results_tree.heading("Vista Previa", text="Vista Previa")
        
        self.results_tree.column("Selección", width=30, anchor="center")
        self.results_tree.column("Fecha", width=150)
        self.results_tree.column("Nombre", width=200)
        self.results_tree.column("Cédula", width=150)
        self.results_tree.column("Vista Previa", width=100, anchor="center")
        
        # Panel de acciones para los resultados
        action_frame = ttk.Frame(results_frame)
        action_frame.pack(fill=X, pady=(10, 0))
        
        ttk.Button(
            action_frame,
            text="Seleccionar Todo",
            command=self.select_all_documents,
            width=15
        ).pack(side=LEFT, padx=5)
        
        ttk.Button(
            action_frame,
            text="Deseleccionar Todo", 
            command=self.deselect_all_documents,
            width=17
        ).pack(side=LEFT, padx=5)
        
        ttk.Button(
            action_frame,
            text="Descargar Seleccionados",
            command=self.download_selected_documents,
            bootstyle="primary",
            width=22
        ).pack(side=RIGHT, padx=5)
        
        # Scrollbar para el Treeview
        tree_scroll = ttk.Scrollbar(
            results_frame,
            orient="vertical", 
            command=self.results_tree.yview
        )
        self.results_tree.configure(yscrollcommand=tree_scroll.set)
        
        self.results_tree.pack(side=LEFT, fill=BOTH, expand=YES)
        tree_scroll.pack(side=RIGHT, fill=Y)
        
        # Binding para clicks en el Treeview
        self.results_tree.bind('<Button-1>', self.on_tree_click)

    def perform_search(self):
        """
        Ejecuta la búsqueda cuando se presiona el botón o se da Enter.
        """
        search_term = self.search_var.get().strip()
        
        if not search_term:
            messagebox.showwarning(
                "Advertencia",
                "Por favor ingrese un término de búsqueda."
            )
            return
            
        # Realizar la búsqueda
        results = self.search_documents(
            search_term,
            self.search_type.get()
        )
        
        # Mostrar los resultados
        self.display_results(results)
            
    def on_search_type_change(self):
        """
        Maneja el cambio en el tipo de búsqueda.
        Ajusta el placeholder y el comportamiento del campo de búsqueda.
        """
        search_type = self.search_type.get()
        if search_type == "cedula":
            # Configurar para búsqueda por cédula
            self.search_entry.delete(0, tk.END)
            # Aquí se implementará la validación para solo números
        else:
            # Configurar para búsqueda por nombre
            self.search_entry.delete(0, tk.END)
            # Aquí se implementará el autocompletado
    
    def search_documents(self, search_term, search_type='cedula'):
        """
        Busca documentos en el spreadsheet basado en el término de búsqueda y el tipo.
        
        Este método lee el spreadsheet de Google y busca coincidencias, ya sea por cédula
        o por nombre (cuando implementemos la base de datos de nombres).
        
        Args:
            search_term (str): El término a buscar (cédula o nombre)
            search_type (str): Tipo de búsqueda ('cedula' o 'nombre')
            
        Returns:
            list: Lista de documentos encontrados, cada uno con su información
        """
        if not self.drive_manager:
            messagebox.showerror(
                "Error",
                "No hay conexión con Google Drive."
            )
            return []
            
        try:
            # Obtener todos los registros del spreadsheet
            sheet_range = 'Registros!A:D'  # Ajusta esto según tu estructura
            result = self.drive_manager.sheets_service.spreadsheets().values().get(
                spreadsheetId=self.drive_manager.spreadsheet_id,
                range=sheet_range
            ).execute()
            
            # Obtener los valores
            values = result.get('values', [])
            
            if not values:
                print("No se encontraron registros")
                return []
                
            # Filtrar los resultados según el criterio de búsqueda
            # Por ahora solo implementamos búsqueda por cédula
            matches = []
            
            # Omitir la primera fila (encabezados)
            for row in values[1:]:
                if len(row) >= 4:  # Asegurarnos de que la fila tiene todos los datos
                    qr_code, cedula, file_path, fecha = row
                    
                    # Por ahora solo búsqueda por cédula exacta
                    if search_type == 'cedula' and cedula == search_term:
                        matches.append({
                            'qr_code': qr_code,
                            'cedula': cedula,
                            'file_path': file_path,
                            'fecha': fecha
                        })
            
            return matches
            
        except Exception as e:
            print(f"Error al buscar documentos: {str(e)}")
            messagebox.showerror(
                "Error",
                f"Error al buscar documentos: {str(e)}"
            )
            return []
    
    def display_results(self, results):
        """Muestra los resultados de la búsqueda en el Treeview"""
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        if not results:
            messagebox.showinfo(
                "Búsqueda",
                "No se encontraron documentos que coincidan con la búsqueda."
            )
            return
                
        for doc in results:
            try:
                fecha = doc['fecha']
                file_url = doc['file_path']
                file_id = file_url.split('/d/')[1].split('/')[0]
                
                # Obtener el nombre real del archivo
                file_metadata = self.drive_manager.drive_service.files().get(
                    fileId=file_id,
                    fields='name'
                ).execute()
                
                file_name = file_metadata.get('name', f"Documento_{doc['cedula']}")
                
                self.results_tree.insert(
                    '',
                    'end',
                    values=(
                        "",  # Checkbox
                        fecha,
                        file_name,  # Ahora usamos el nombre real
                        doc['cedula'],
                        "👁️"  # Icono para vista previa
                    )
                )
            except Exception as e:
                print(f"Error al mostrar resultado: {str(e)}")
                continue
                    
        self.last_search_results = results
    
    def on_tree_click(self, event):
        """
        Maneja los clics en el TreeView para seleccionar/deseleccionar items
        """
        region = self.results_tree.identify_region(event.x, event.y)
        if region == "cell":
            item = self.results_tree.identify_row(event.y)
            if item:
                current_values = self.results_tree.item(item)['values']
                new_values = list(current_values)
                new_values[0] = "✓" if current_values[0] != "✓" else ""
                self.results_tree.item(item, values=new_values)

    def select_all_documents(self):
        """
        Marca todos los documentos en el TreeView como seleccionados.
        """
        for item in self.results_tree.get_children():
            current_values = list(self.results_tree.item(item)['values'])
            current_values[0] = "✓"
            self.results_tree.item(item, values=current_values)

    def deselect_all_documents(self):
        """
        Desmarca todos los documentos en el TreeView.
        """
        for item in self.results_tree.get_children():
            current_values = list(self.results_tree.item(item)['values'])
            current_values[0] = ""
            self.results_tree.item(item, values=current_values)


    def download_selected_documents(self):

        if not self.drive_manager:
            messagebox.showerror("Error", "No hay conexión con Google Drive.")
            return

        selected_docs = []
        print("\nBuscando documentos seleccionados...")
        
        for item in self.results_tree.get_children():
            values = self.results_tree.item(item)['values']
            if values[0] == "✓":
                cedula = str(values[3])
                fecha = values[1]
                print(f"Documento seleccionado - Cédula: {cedula}, Fecha: {fecha}")
                
                for doc in self.last_search_results:
                    if (str(doc['cedula']) == cedula and 
                        doc['fecha'] == fecha):
                        file_url = doc['file_path']
                        file_id = file_url.split('/d/')[1].split('/')[0]
                        selected_docs.append(file_id)
                        print(f"Coincidencia encontrada - ID: {file_id}")
                        break

        print(f"\nDocumentos seleccionados: {len(selected_docs)}")

        if not selected_docs:
            messagebox.showwarning("Advertencia", "Seleccione documentos para descargar.")
            return

        download_dir = filedialog.askdirectory(title="Seleccione carpeta de descarga")
        if not download_dir:
            return

        try:
            progress_window = ttk.Toplevel(self.window)
            progress_window.title("Descargando")
            progress_window.geometry("300x150")
            progress_frame = ttk.Frame(progress_window, padding=20)
            progress_frame.pack(fill=BOTH, expand=YES)

            progress_label = ttk.Label(
                progress_frame,
                text="Descargando documentos...",
                wraplength=250
            )
            progress_label.pack(pady=(0, 10))

            progress_bar = ttk.Progressbar(
                progress_frame,
                length=200,
                mode='determinate'
            )
            progress_bar.pack()

            total = len(selected_docs)
            successful_downloads = 0

            for i, file_id in enumerate(selected_docs, 1):
                progress = (i / total) * 100
                progress_bar['value'] = progress
                progress_label.config(text=f"Descargando documento {i} de {total}")
                progress_window.update()

                try:
                    if self.drive_manager.download_file(file_id, download_dir):
                        successful_downloads += 1
                        print(f"Descarga {i} completada")
                    else:
                        print(f"Error en descarga {i}")
                except Exception as e:
                    print(f"Error al descargar archivo {i}: {str(e)}")
                    continue

            progress_window.destroy()
            messagebox.showinfo(
                "Éxito",
                f"Se descargaron {successful_downloads} de {total} documentos en {download_dir}"
            )

        except Exception as e:
            if 'progress_window' in locals():
                progress_window.destroy()
            print(f"Error general: {str(e)}")
            messagebox.showerror(
                "Error",
                f"Error al descargar documentos: {str(e)}"
            )

    def download_file(self, file_id, destination_folder):
        """Descarga un archivo de Google Drive"""
        try:
            # Obtener metadata del archivo
            file_metadata = self.drive_service.files().get(
                fileId=file_id,
                fields='name'
            ).execute()
            
            # Usar directamente el nombre del archivo de Drive
            file_name = file_metadata['name']
            destination_path = os.path.join(destination_folder, file_name)
            print(f"Descargando archivo como: {file_name}")
            
            # Descargar archivo
            request = self.drive_service.files().get_media(fileId=file_id)
            with open(destination_path, 'wb') as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while not done:
                    _, done = downloader.next_chunk()
            
            if os.path.exists(destination_path):
                print(f"Archivo guardado exitosamente: {file_name}")
                return True
            else:
                print(f"Error: No se encontró el archivo en la ruta: {destination_path}")
                return False
                
        except Exception as e:
            print(f"Error al descargar archivo {file_id}: {str(e)}")
            raise
    
    def on_tree_click(self, event):
        """
        Maneja los clics en el TreeView:
        - Click en columna 1: Selecciona/deselecciona el documento
        - Click en columna 5: Abre vista previa del documento
        """
        region = self.results_tree.identify_region(event.x, event.y)
        column = self.results_tree.identify_column(event.x)
        
        if region == "cell":
            item = self.results_tree.identify_row(event.y)
            if item:
                if column == "#1":  # Columna de selección
                    current_values = self.results_tree.item(item)['values']
                    new_values = list(current_values)
                    new_values[0] = "✓" if current_values[0] != "✓" else ""
                    self.results_tree.item(item, values=new_values)
                
                elif column == "#5":  # Columna de vista previa
                    values = self.results_tree.item(item)['values']
                    cedula = str(values[3])
                    fecha = values[1]
                    
                    # Buscar el documento en los resultados
                    for doc in self.last_search_results:
                        if (str(doc['cedula']) == cedula and doc['fecha'] == fecha):
                            file_url = doc['file_path']
                            file_id = file_url.split('/d/')[1].split('/')[0]
                            
                            # Abrir ventana de vista previa
                            self.open_preview_window(file_id, doc)
                            break
    
    def open_preview_window(self, file_id, doc_info):
        """Abre una nueva ventana con la vista previa del documento"""
        try:
            # Crear la ventana de vista previa
            preview_window = ttk.Toplevel(self.window)
            preview_window.title(f"Vista Previa - Documento {doc_info.get('cedula', 'Sin ID')}")
            
            # Configurar tamaño y posición
            window_width = 1000
            window_height = 700
            preview_window.minsize(800, 600)
            
            # Centrar ventana
            screen_width = preview_window.winfo_screenwidth()
            screen_height = preview_window.winfo_screenheight()
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
            preview_window.geometry(f'{window_width}x{window_height}+{x}+{y}')
            
            # Hacer ventana modal
            preview_window.transient(self.window)
            preview_window.grab_set()
            
            # Frame principal con padding
            main_frame = ttk.Frame(preview_window, padding=15)
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Panel superior con información y botón de descarga
            top_frame = ttk.Frame(main_frame)
            top_frame.pack(fill=tk.X, pady=(0, 10))
            
            # Información del documento
            info_frame = ttk.LabelFrame(top_frame, text="Información del Documento", padding=10)
            info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            ttk.Label(info_frame, text=f"Cédula: {doc_info.get('cedula', 'N/A')}").pack(anchor=tk.W)
            ttk.Label(info_frame, text=f"Fecha: {doc_info.get('fecha', 'N/A')}").pack(anchor=tk.W)
            
            # Botón de descarga
            download_frame = ttk.Frame(top_frame)
            download_frame.pack(side=tk.RIGHT, padx=10)
            
            download_btn = ttk.Button(
                download_frame,
                text="Descargar Documento",
                command=lambda: self.download_single_document(file_id, preview_window),
                bootstyle="primary"
            )
            download_btn.pack()
            
            # Frame para la vista previa
            preview_frame = ttk.LabelFrame(main_frame, text="Vista Previa", padding=10)
            preview_frame.pack(fill=tk.BOTH, expand=True)
            
            # Canvas y scrollbars para la vista previa
            preview_container = ttk.Frame(preview_frame)
            preview_container.pack(fill=tk.BOTH, expand=True)
            
            h_scrollbar = ttk.Scrollbar(preview_container, orient=tk.HORIZONTAL)
            v_scrollbar = ttk.Scrollbar(preview_container, orient=tk.VERTICAL)
            
            preview_canvas = tk.Canvas(
                preview_container,
                bg='white',
                relief='solid',
                borderwidth=1,
                xscrollcommand=h_scrollbar.set,
                yscrollcommand=v_scrollbar.set
            )
            
            self.zoom_factor = 1.0
            self.pan_start_x = None
            self.pan_start_y = None
            self.current_image = None
            self.original_image_size = None
            
            # Bindings para zoom y pan
            preview_canvas.bind('<ButtonPress-1>', lambda e: self.start_pan(e, preview_canvas))
            preview_canvas.bind('<B1-Motion>', lambda e: self.pan_image(e, preview_canvas))
            preview_canvas.bind('<ButtonRelease-1>', lambda e: self.stop_pan(e, preview_canvas))
            preview_canvas.bind('<MouseWheel>', lambda e: self.zoom(e, preview_canvas))
            preview_canvas.bind('<Configure>', lambda e: self.on_canvas_configure(e, preview_canvas))
            
                
            h_scrollbar.config(command=preview_canvas.xview)
            v_scrollbar.config(command=preview_canvas.yview)
            
            h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
            v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            preview_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            # Cargar y mostrar el documento
            self.load_preview(preview_canvas, file_id)
            
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Error al abrir vista previa: {str(e)}"
            )
        
    def download_single_document(self, file_id, parent_window):
        """Descarga un documento individual"""
        try:
            download_dir = filedialog.askdirectory(
                title="Seleccione carpeta de descarga",
                parent=parent_window
            )
            
            if download_dir:
                result = self.drive_manager.download_file(file_id, download_dir)
                if result:
                    messagebox.showinfo(
                        "Éxito",
                        "Documento descargado correctamente",
                        parent=parent_window
                    )
                
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Error al descargar el documento: {str(e)}",
                parent=parent_window
            )
    
    def load_preview(self, canvas, file_id):
        """Carga la vista previa del documento en el canvas"""
        try:
            # Mostrar mensaje de carga
            canvas.delete("all")
            canvas.create_text(
                canvas.winfo_width() // 2,
                canvas.winfo_height() // 2,
                text="Cargando vista previa...",
                font=("Segoe UI", 12)
            )
            canvas.update()
            
            # Crear directorio temporal usando una ruta absoluta
            import tempfile
            temp_dir = tempfile.gettempdir()
            
            # Descargar archivo temporalmente
            try:
                success = self.drive_manager.download_file(file_id, temp_dir)
                if not success:
                    raise Exception("No se pudo descargar el archivo")
                    
                # Obtener el nombre del archivo descargado
                file_metadata = self.drive_manager.drive_service.files().get(
                    fileId=file_id,
                    fields='name'
                ).execute()
                temp_file = os.path.join(temp_dir, file_metadata['name'])
                
                # Verificar que el archivo existe
                if not os.path.exists(temp_file):
                    raise Exception("No se encuentra el archivo descargado")
                
                # Cargar la vista previa según el tipo de archivo
                if temp_file.lower().endswith('.pdf'):
                    doc = fitz.open(temp_file)
                    page = doc[0]
                    zoom_matrix = fitz.Matrix(2, 2)
                    pix = page.get_pixmap(matrix=zoom_matrix)
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    doc.close()
                else:
                    img = Image.open(temp_file)
                
                # Guardar imagen original
                self.current_image = img
                self.original_image_size = img.size
                
                # Ajustar tamaño al canvas
                canvas_width = canvas.winfo_width()
                canvas_height = canvas.winfo_height()
                
                img_copy = img.copy()
                img_copy.thumbnail((canvas_width, canvas_height))
                
                # Mostrar imagen
                photo = ImageTk.PhotoImage(img_copy)
                canvas.delete("all")
                canvas.create_image(
                    canvas_width//2,
                    canvas_height//2,
                    image=photo,
                    anchor="center"
                )
                canvas.image = photo
                
                # Limpiar archivo temporal
                try:
                    os.remove(temp_file)
                except:
                    print(f"No se pudo eliminar el archivo temporal: {temp_file}")
                    
            except Exception as e:
                raise Exception(f"Error al descargar archivo: {str(e)}")

        except Exception as e:
            canvas.delete("all")
            canvas.create_text(
                canvas.winfo_width() // 2,
                canvas.winfo_height() // 2,
                text=f"Error al cargar vista previa: {str(e)}",
                font=("Segoe UI", 12),
                fill="red"
            )
    
    def start_pan(self, event, canvas):
        """Iniciar el arrastre"""
        self.pan_start_x = event.x
        self.pan_start_y = event.y
        canvas.scan_mark(event.x, event.y)

    def pan_image(self, event, canvas):
        """Realizar el arrastre"""
        if hasattr(self, 'pan_start_x') and self.pan_start_x is not None:
            canvas.scan_dragto(event.x, event.y, gain=1)

    def stop_pan(self, event, canvas):
        """Detener el arrastre"""
        self.pan_start_x = None
        self.pan_start_y = None

    def zoom(self, event, canvas):
        """Aplicar zoom a la imagen"""
        if not hasattr(self, 'current_image') or not self.current_image:
            return
            
        # Determinar dirección del zoom
        if event.delta > 0:
            self.zoom_factor = min(5.0, self.zoom_factor * 1.1)
        else:
            self.zoom_factor = max(0.1, self.zoom_factor * 0.9)
            
        # Calcular nuevas dimensiones
        new_width = int(self.original_image_size[0] * self.zoom_factor)
        new_height = int(self.original_image_size[1] * self.zoom_factor)
        
        # Redimensionar y mostrar
        img_resized = self.current_image.resize(
            (new_width, new_height),
            Image.Resampling.LANCZOS
        )
        
        # Actualizar la imagen en el canvas
        photo = ImageTk.PhotoImage(img_resized)
        canvas.delete("all")
        canvas.create_image(
            canvas.winfo_width()//2,
            canvas.winfo_height()//2,
            image=photo,
            anchor="center"
        )
        canvas.image = photo

    def on_canvas_configure(self, event, canvas):
        """Manejar redimensionamiento del canvas"""
        if hasattr(self, 'current_image') and self.current_image:
            # Recalcular el tamaño de la imagen al redimensionar
            canvas_width = canvas.winfo_width()
            canvas_height = canvas.winfo_height()
            
            img_copy = self.current_image.copy()
            img_copy.thumbnail((canvas_width, canvas_height))
            
            photo = ImageTk.PhotoImage(img_copy)
            canvas.delete("all")
            canvas.create_image(
                canvas_width//2,
                canvas_height//2,
                image=photo,
                anchor="center"
            )
            canvas.image = photo