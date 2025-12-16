import streamlit as st
from supabase import create_client, Client
from streamlit_js_eval import get_geolocation
from datetime import datetime

# 1. Configuración
st.set_page_config(page_title="Sistema de Prueba", page_icon="🧪")
st.title("🧪 Prueba de Campo: Foto y GPS")

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

# Solo pedimos la NOTA (porque es la única columna de texto que tienes)
nota_usuario = st.text_input("Escribe una nota:", "Prueba de campo con foto")

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
        with st.spinner("Subiendo foto y datos..."):
            try:
                # A. Subir Foto
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                nombre_archivo = f"img_{timestamp}.png"
                
                archivo_bytes = archivo_foto.getbuffer()
                
                # Subir al bucket 'fotos_probetas' (Asegúrate que el bucket exista y sea público)
                supabase.storage.from_("fotos_probetas").upload(
                    path=nombre_archivo,
                    file=archivo_bytes,
                    file_options={"content-type": "image/png"}
                )
                
                # B. Obtener Link
                url_publica = supabase.storage.from_("fotos_probetas").get_public_url(nombre_archivo)
                
                # C. Guardar en Base de Datos (Solo tus columnas)
                datos = {
                    "latitud": lat,
                    "longitud": lon,
                    "nota": nota_usuario,
                    "foto_url": url_publica
                }
                
                supabase.table("pruebas").insert(datos).execute()
                
                st.balloons()
                st.success("✅ ¡Registro guardado exitosamente!")
                
            except Exception as e:
                st.error(f"Ocurrió un error: {e}")
                
    elif not archivo_foto:
        st.error("⚠️ Falta la foto.")
    elif lat == 0:
        st.error("⚠️ Falta el GPS.")

# 6. Ver datos recientes
st.write("---")
st.subheader("📂 Registros en Base de Datos")
try:
    registros = supabase.table("pruebas").select("*").order("created_at", desc=True).limit(3).execute()
    
    for row in registros.data:
        with st.container(border=True):
            # Mostrar foto si existe
            if row.get('foto_url'):
                st.image(row['foto_url'], width=200)
            
            # Mostrar datos
            st.write(f"📝 **Nota:** {row['nota']}")
            st.caption(f"📍 {row['latitud']}, {row['longitud']} | 📅 {row['created_at']}")
except:
    pass