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