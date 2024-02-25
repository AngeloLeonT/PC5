import pandas as pd
import requests

def limpiar_columnas(df):
    # Renombrar columnas eliminando espacios, tildes y convirtiendo a minúsculas
    df.columns = df.columns.str.lower().str.replace(' ', '').str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')

    # Cambiar nombres de columna si es necesario
    # df.rename(columns={'columna_original': 'nuevo_nombre'}, inplace=True)

    # Eliminar columnas duplicadas
    df = df.loc[:, ~df.columns.duplicated()]

    # Eliminar caracteres ',' de la columna "DISPOSITIVOLEGAL"
    df['dispositivolegal'] = df['dispositivolegal'].replace({',': ''}, regex=True)

    return df

def obtener_tipo_cambio():
    # Utilice el API de sunat o cualquier otro recurso para obtener el valor actual del dólar
    # Ejemplo con el API de sunat (reemplace con la URL correcta)
    url_sunat = 'https://api.sunat.com/tipo_cambio'
    response = requests.get(url_sunat)
    tipo_cambio = response.json()['dolar']['compra']  # Asegúrese de verificar la estructura de la respuesta

    return tipo_cambio

def dolarizar_montos(df):
    tipo_cambio = obtener_tipo_cambio()

    # Dolarizar montos de inversión y transferencia
    df['monto_inversion_dolares'] = df['montodeinversion'] * tipo_cambio
    df['monto_transferencia_dolares'] = df['montodetransferencia'] * tipo_cambio

    return df

def mapear_estado(df):
    # Mapear valores de la columna "Estado"
    df['estado'] = df['estado'].map({'Actos Previos': 1, 'Resuelto': 0, 'Ejecucion': 2, 'Concluido': 3})

    return df

if __name__ == "__main__":
    # Cargar el archivo Excel
    archivo_excel = 'reactiva.xlsx'
    df = pd.read_excel(archivo_excel)

    # Aplicar la limpieza de columnas
    df = limpiar_columnas(df)

    # Eliminar las columnas "ID" y "TipoMoneda" duplicadas
    df = df.drop(['id', 'tipomoneda'], axis=1, errors='ignore')

    # Dolarizar montos de inversión y transferencia
    df = dolarizar_montos(df)

    # Mapear valores de la columna "Estado"
    df = mapear_estado(df)

    # Guardar el DataFrame procesado en un nuevo archivo Excel
    df.to_excel('reactiva_procesado.xlsx', index=False)


# GENERANDO REPORTES USANDO DE EJ SQLLITE
    import sqlite3

# ... (código anterior)

def guardar_en_base_de_datos(df):
    # Crear o conectar a la base de datos SQLite
    conexion = sqlite3.connect('ubigeos.db')

    # Guardar la tabla de ubigeos en la base de datos
    df[['ubigeo', 'region', 'provincia', 'distrito']].drop_duplicates().to_sql('ubigeos', conexion, index=False, if_exists='replace')

    # Cerrar la conexión a la base de datos
    conexion.close()

def generar_reportes_por_region(df):
    # Agrupar por región y tipo de obra
    grupos = df.groupby(['region', 'tipoobra', 'estado'])

    for (region, tipo_obra, estado), grupo in grupos:
        if tipo_obra == 'Urbano':
            # Filtrar por las 5 mayores inversiones
            top5 = grupo.nlargest(5, 'montodeinversion')

            # Verificar si hay datos en el top5
            if not top5.empty:
                # Generar el nombre del archivo Excel
                nombre_archivo = f'{region}_top5_{tipo_obra}_estado_{estado}.xlsx'

                # Guardar el top5 en un archivo Excel
                top5.to_excel(nombre_archivo, index=False)

if __name__ == "__main__":
    # ... (código anterior)

    # Guardar en la base de datos
    guardar_en_base_de_datos(df)

    # Generar reportes por región y tipo de obra
    generar_reportes_por_region(df)

    # GENERACIÓN DE ENVÍO DE CORREO
    import os 



smtp_server = 'smtp.gmail.com'  # Cambia esto al servidor SMTP que estés utilizando
smtp_port = 587  # Cambia esto al puerto adecuado
sender_email = 'leonleonel035@gmail.com'
sender_password = open('token.txt').read().strip()

# Detalles del correo electrónico
receiver_email = 'carolinaccorisapra002@gmail.com'
subject = 'Envio Reporte reactiva'
body = 'Adjunto lo solicitado'

# Crear el objeto MIMEMultipart
msg = MIMEMultipart()
msg['From'] = sender_email
msg['To'] = receiver_email
msg['Subject'] = subject
msg.attach(MIMEText(body, 'plain'))


# Adjuntar archivo
file_path = './data/reactiva.xlsx'  # Cambia la ruta al archivo que quieras adjuntar
with open(file_path, 'rb') as file:
    attachment = MIMEApplication(file.read(), _subtype="xlsx")
    attachment.add_header('Content-Disposition', 'attachment', filename=file_path)
    msg.attach(attachment)
    
# Iniciar la conexión con el servidor SMTP
with smtplib.SMTP(smtp_server, smtp_port) as server:
    server.starttls()  # Iniciar el modo seguro
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, receiver_email, msg.as_string())

print('Correo enviado exitosamente')