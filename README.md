# Sistema de Gestión Documental (SGD) - Versión Desktop

![Logo INEMEC](Logo.jpg)

## Descripción

El Sistema de Gestión Documental (SGD) es una aplicación de escritorio desarrollada para la gestión integral de documentos con códigos QR. Permite generar, registrar, buscar y administrar documentos de manera eficiente con integración completa a Google Drive y Google Sheets.

## Características Principales

### 🔧 Generación de Documentos
- Generación automática de códigos QR únicos (UUID)
- Inserción de QR en plantillas de Word (.docx)
- Registro automático en Google Sheets
- Generación masiva de documentos

### 📄 Registro de Documentos
- Escaneo de códigos QR desde archivos PDF e imágenes
- Relación de documentos con identificadores de cédula
- Almacenamiento automático en Google Drive
- Formatos soportados: PDF, PNG, JPG, JPEG
- Vista previa con zoom y navegación

### 🔍 Búsqueda de Documentos
- Búsqueda por número de cédula
- Vista previa de documentos encontrados
- Descarga individual o masiva
- Interfaz intuitiva con selección múltiple

### ☁️ Integración con Google Cloud
- Almacenamiento automático en Google Drive
- Registro de datos en Google Sheets
- Acceso desde cualquier lugar con permisos
- Respaldo automático en la nube

## Requisitos del Sistema

### Software
- Windows 10/11 (64-bit)
- Python 3.8+ (para desarrollo)
- Conexión a internet

### Dependencias Python
```
tkinter
ttkbootstrap
Pillow (PIL)
PyMuPDF (fitz)
opencv-python
pyzbar
pandas
python-docx
qrcode
google-auth
google-auth-oauthlib
google-auth-httplib2
google-api-python-client
numpy
```

### Servicios de Google
- Cuenta de Google Cloud Platform
- APIs habilitadas:
  - Google Drive API
  - Google Sheets API
- Archivo de credenciales `credentials.json`

## Instalación

### Opción 1: Ejecutable (Recomendado)
1. Descargar el archivo `SGD_INEMEC v1.2.0.exe`
2. Colocar el archivo `credentials.json` en la misma carpeta
3. Asegurar que el archivo `plantilla.docx` esté presente
4. Ejecutar el programa

### Opción 2: Desde el código fuente
1. Clonar el repositorio:
```bash
git clone [url-del-repositorio]
cd sgd-desktop
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Configurar credenciales de Google:
   - Colocar `credentials.json` en el directorio raíz
   - Verificar permisos de las APIs

4. Ejecutar la aplicación:
```bash
python main.py
```

## Configuración

### 1. Credenciales de Google
- Obtener `credentials.json` desde Google Cloud Console
- Configurar cuenta de servicio con permisos adecuados
- Habilitar Google Drive API y Google Sheets API

### 2. Plantilla de Documento
- El archivo `plantilla.docx` debe contener una tabla donde se insertará el QR
- Posición predeterminada: Tabla 1, Fila 5, Columna 0

### 3. Estructura de Archivos
```
SGD_INEMEC/
├── main.py
├── document_generator.py
├── document_register.py
├── document_search.py
├── credentials.json
├── plantilla.docx
├── Logo.jpg
└── README.md
```

## Uso

### Generación de Documentos
1. Abrir el módulo "Generación de Documentos"
2. Especificar el número de actas a generar
3. Seleccionar carpeta de destino
4. El sistema generará automáticamente:
   - Documentos Word con QR únicos
   - Registro en Google Sheets

### Registro de Documentos
1. Abrir el módulo "Registro de Documentos"
2. Seleccionar archivos o carpetas con documentos escaneados
3. El sistema verificará automáticamente los códigos QR
4. Relacionar cada documento con un número de cédula
5. Los documentos se almacenan en Google Drive

### Búsqueda de Documentos
1. Abrir el módulo "Búsqueda de Documentos"
2. Ingresar número de cédula
3. Revisar resultados encontrados
4. Usar vista previa para verificar documentos
5. Descargar documentos seleccionados

## Estructura de Datos

### Google Sheets - Hoja "Registros"
| Código QR | Número de Cédula | Ruta del Archivo | Fecha de Registro |
|-----------|------------------|------------------|-------------------|
| uuid-1234 | 123456789       | drive-link       | 2024-01-15 14:30  |

### Google Sheets - Hoja "QR_Generados"
| ID del QR | Código de Documento | Fecha de Generación |
|-----------|---------------------|---------------------|
| uuid-1234 | GCO-REG-099        | 2024-01-15 14:30    |

### Google Drive - Estructura
```
Documentos_Escaneados/
├── GCO-REG-099_123456789_20240115_143021.pdf
├── GCO-REG-099_987654321_20240115_143045.pdf
└── ...
```

## Formatos Soportados

### Documentos de Entrada
- **PDF**: Archivos PDF con códigos QR
- **Imágenes**: PNG, JPG, JPEG con códigos QR

### Documentos de Salida
- **Word**: Documentos .docx generados
- **Enlaces**: URLs directos a Google Drive

## Solución de Problemas

### Error de Conexión con Google Drive
- Verificar que `credentials.json` sea válido
- Comprobar conexión a internet
- Verificar permisos de las APIs en Google Cloud

### QR No Detectado
- Verificar calidad de la imagen/PDF
- Asegurar que el QR sea legible
- Comprobar que el documento no esté rotado

### Archivo de Plantilla No Encontrado
- Verificar que `plantilla.docx` esté en el directorio correcto
- Comprobar que la plantilla tenga la estructura de tabla requerida

### Problemas de Permisos
- Verificar permisos de escritura en carpetas de destino
- Comprobar permisos de Google Drive/Sheets

## Compilación

Para generar el ejecutable:
```bash
pyinstaller antivirus.spec
```

El archivo `antivirus.spec` incluye todas las dependencias y archivos necesarios.

## Versiones

### v1.2.0 (Actual)
- Integración completa con Google Drive/Sheets
- Vista previa mejorada con zoom y navegación
- Selección de formatos de documento
- Interfaz de usuario optimizada
- Manejo de errores robusto

### Versiones Anteriores
- v1.1.0: Funcionalidad básica de QR
- v1.0.0: Versión inicial

## Soporte Técnico

Para reportar problemas o solicitar nuevas características:
- Documentar el error con capturas de pantalla
- Incluir archivos de log si están disponibles
- Especificar sistema operativo y versión

## Licencia

Este software es propiedad de INEMEC y está destinado para uso interno exclusivamente.

---

**Desarrollado para INEMEC**  
**Versión**: 1.2.0  
**Fecha**: 2024