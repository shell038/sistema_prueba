import streamlit as st
from supabase import create_client, Client
from streamlit_js_eval import get_geolocation

# 1. Configuración
st.set_page_config(page_title="Laboratorio v2", page_icon="📡")
st.title("📡 Enviar Datos a la Nube")

# 2. Conexión
try:
    url = st.secrets["SUPABASE"]["URL"]
    key = st.secrets["SUPABASE"]["KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error("Error de conexión. Revisa tus secrets.toml")
    st.stop()

# 3. Captura de Datos
st.write("---")
st.subheader("1. Obtener Datos del Sitio")

nota_usuario = st.text_input("Escribe una nota de prueba:", "Probando desde mi Mac")

# GPS
loc = get_geolocation()
lat, lon = 0.0, 0.0

if loc:
    lat = loc['coords']['latitude']
    lon = loc['coords']['longitude']
    st.success(f"📍 Ubicación detectada: {lat}, {lon}")
else:
    st.warning("⚠️ Esperando GPS... (Asegúrate de dar permiso en el navegador)")

# 4. Botón de Guardar (La Magia)
st.write("---")
if st.button("💾 GUARDAR EN SUPABASE", type="primary"):
    if lat != 0.0:
        try:
            # Aquí ocurre el envío a la nube
            datos = {
                "latitud": lat,
                "longitud": lon,
                "nota": nota_usuario
            }
            
            # Insertar en la tabla 'pruebas'
            respuesta = supabase.table("pruebas").insert(datos).execute()
            
            st.balloons() # ¡Festejo!
            st.success("✅ ¡Datos guardados en la nube exitosamente!")
            
        except Exception as e:
            st.error(f"Ocurrió un error al guardar: {e}")
    else:
        st.error("❌ No puedo guardar sin coordenadas GPS. Espera a que carguen.")

# 5. Ver lo que hay en la base de datos (Para comprobar)
st.write("---")
st.subheader("👀 Historial en Vivo (Desde Supabase)")
try:
    response = supabase.table("pruebas").select("*").order("created_at", desc=True).execute()
    st.dataframe(response.data)
except:
    pass