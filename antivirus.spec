# coding: utf-8

block_cipher = None

a = Analysis(['main.py'],
             pathex=['.'],
             binaries=[
                ('C:\\Users\\Jesus.Cortes\\AppData\\Local\\Programs\\Python\\Python313\\Lib\\pyzbar\\libiconv.dll', '.'),
                ('C:\\Users\\Jesus.Cortes\\AppData\\Local\\Programs\\Python\\Python313\\Lib\\pyzbar\\libzbar-64.dll', '.')
             ],
             datas=[('plantilla.docx', '.'), 
                    ('credentials.json', '.'),
                    ('document_search.py', '.'),
                    ('document_register.py', '.'),
                    ('document_generator.py', '.'),
                    ('Logo.jpg','.')],
             hiddenimports=['PIL', 'pyzbar', 'cv2', 'fitz', 'google.oauth2', 'googleapiclient', 'ttkbootstrap'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='SGD_INEMEC v1.2.0',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None,
          uac_admin=False)