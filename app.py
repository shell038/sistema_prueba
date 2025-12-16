import streamlit as st
from supabase import create_client, Client
from streamlit_js_eval import get_geolocation
from datetime import datetime

# 1. Configuración
st.set_page_config(page_title="Sistema de Prueba", page_icon="📲")
st.title("📲 Registro de Campo: Foto y GPS")

# 2. Conexión a Supabase
try:
    url = st.secrets["SUPABASE"]["URL"]
    key = st.secrets["SUPABASE"]["KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error("Error de conexión. Revisa los secrets.")
    st.stop()

# 3. Interfaz de Usuario
st.write("---")
st.subheader("1. Datos Generales")

nota_usuario = st.text_input("Escribe una nota:", "Prueba de sistema")

# GPS
loc = get_geolocation()
lat, lon = 0.0, 0.0
if loc:
    lat = loc['coords']['latitude']
    lon = loc['coords']['longitude']
    st.success(f"📍 Ubicación: {lat}, {lon}")
else:
    st.warning("📡 Esperando GPS...")

# 4. Cámara
st.write("---")
st.subheader("2. Evidencia")
archivo_foto = st.camera_input("Tomar foto")

# 5. Guardar
if st.button("💾 GUARDAR REGISTRO", type="primary"):
    if archivo_foto and lat != 0:
        with st.spinner("Subiendo datos..."):
            try:
                # A. Generar nombre de archivo
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                nombre_archivo = f"foto_{timestamp}.png"
                
                # B. Preparar la imagen (Corrección aplicada: getvalue)
                archivo_bytes = archivo_foto.getvalue()
                
                # C. Subir al bucket 'fotos' (Nombre genérico)
                supabase.storage.from_("fotos").upload(
                    path=nombre_archivo,
                    file=archivo_bytes,
                    file_options={"content-type": "image/png"}
                )
                
                # D. Obtener Link Público
                url_publica = supabase.storage.from_("fotos").get_public_url(nombre_archivo)
                
                # E. Guardar en Base de Datos
                datos = {
                    "latitud": lat,
                    "longitud": lon,
                    "nota": nota_usuario,
                    "foto_url": url_publica
                }
                
                supabase.table("pruebas").insert(datos).execute()
                
                st.balloons()
                st.success("✅ ¡Guardado con éxito!")
                
            except Exception as e:
                st.error(f"Error: {e}")
                
    elif not archivo_foto:
        st.error("⚠️ Falta la foto.")
    elif lat == 0:
        st.error("⚠️ Falta el GPS.")

# 6. Ver historial
st.write("---")
st.subheader("📂 Registros Recientes")
try:
    registros = supabase.table("pruebas").select("*").order("created_at", desc=True).limit(3).execute()
    
    for row in registros.data:
        with st.container(border=True):
            if row.get('foto_url'):
                st.image(row['foto_url'], width=200)
            st.write(f"📝 {row['nota']}")
            st.caption(f"📍 {row['latitud']}, {row['longitud']}")
except:
    pass