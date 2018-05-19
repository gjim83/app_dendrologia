"""
Versión recontrabeta del script que analiza las actas de la Asamblea Legislativa.

No me gusta así que ya lo estoy refactoreando, pero lo subo para ir compartiendo.

¿Comentarios, sugerencias, madrazos? (no mejor madrazos no)
asambleaabiertacr[arroba]gmail[punto]com
"""

import re
import os
import sys
import difflib
import pdftotext


# ESTRUCTURA DE DATOS DE DIPUTADOS

# No me odien porque empieza en 1 y no en 0, fue culpa de MySQL :\
# Esto tiene que cambiarse para consultarlo de la DB usando una clase ORM

DIPS = {
    1: {'nombres': 'Pablo Heriberto', 'apellidos': 'Abarca Mora'},
    2: {'nombres': 'Ivonne', 'apellidos': 'Acuña Cabrera'},
    3: {'nombres': 'Luis Antonio', 'apellidos': 'Aiza Campos'},
    4: {'nombres': 'Ignacio Alberto', 'apellidos': 'Alpízar Castro'},
    5: {'nombres': 'Mileyde', 'apellidos': 'Alvarado Arias'},
    6: {'nombres': 'Carlos Luis', 'apellidos': 'Avendaño Calvo'},
    7: {'nombres': 'Marolin Raquel', 'apellidos': 'Azofeifa Trejos'},
    8: {'nombres': 'Carlos Ricardo', 'apellidos': 'Benavides Jiménez'},
    9: {'nombres': 'Luis Ramón', 'apellidos': 'Carranza Cascante'},
    10: {'nombres': 'Oscar Mauricio', 'apellidos': 'Cascante Cascante'},
    11: {'nombres': 'Mario Eduardo', 'apellidos': 'Castillo Melendez'},
    12: {'nombres': 'Nidia Lorena', 'apellidos': 'Céspedes Cisneros'},
    13: {'nombres': 'Luis Fernando', 'apellidos': 'Chacón Monge'},
    14: {'nombres': 'Carmen Irene', 'apellidos': 'Chan Mora'},
    15: {'nombres': 'María José', 'apellidos': 'Corrales Chacón'},
    16: {'nombres': 'Eduardo Newton', 'apellidos': 'Cruickshank Smith'},
    17: {'nombres': 'Ana Lucía', 'apellidos': 'Delgado Orozco'},
    18: {'nombres': 'Dragos', 'apellidos': 'Dolanescu Valenciano'},
    19: {'nombres': 'Shirley', 'apellidos': 'Díaz Mejías'},
    20: {'nombres': 'Jorge Luis', 'apellidos': 'Fonseca Fonseca'},
    21: {'nombres': 'David Hubert', 'apellidos': 'Gourzong Cerdas'},
    22: {'nombres': 'Laura', 'apellidos': 'Guido Pérez'},
    23: {'nombres': 'Giovanni Alberto', 'apellidos': 'Gómez Obando'},
    24: {'nombres': 'Silvia', 'apellidos': 'Hernández Sánchez'},
    25: {'nombres': 'Carolina', 'apellidos': 'Hidalgo Herrera'},
    26: {'nombres': 'Harllan', 'apellidos': 'Hoepelman Páez'},
    27: {'nombres': 'Wagner', 'apellidos': 'Jiménez Zúñiga'},
    28: {'nombres': 'Yorleny', 'apellidos': 'León Marchena'},
    29: {'nombres': 'Erwen Yanan', 'apellidos': 'Masís Castro'},
    30: {'nombres': 'María Vita', 'apellidos': 'Monge Granados'},
    31: {'nombres': 'Catalina', 'apellidos': 'Montero Gómez'},
    32: {'nombres': 'Aida María', 'apellidos': 'Montiel Héctor'},
    33: {'nombres': 'Víctor Manuel', 'apellidos': 'Morales Mora'},
    34: {'nombres': 'Walter', 'apellidos': 'Muñoz Céspedes'},
    35: {'nombres': 'Pedro Miguel', 'apellidos': 'Muñoz Fonseca'},
    36: {'nombres': 'Franggi', 'apellidos': 'Nicolás Solano'},
    37: {'nombres': 'Ana Karine', 'apellidos': 'Niño Gutiérrez'},
    38: {'nombres': 'Melvin Ángel', 'apellidos': 'Nuñez Piña'},
    39: {'nombres': 'Rodolfo Rodrigo', 'apellidos': 'Peña Flores'},
    40: {'nombres': 'Jonathan', 'apellidos': 'Prendas Rodríguez'},
    41: {'nombres': 'Nielsen', 'apellidos': 'Pérez Pérez'},
    42: {'nombres': 'Welmer', 'apellidos': 'Ramos González'},
    43: {'nombres': 'Xiomara Priscilla', 'apellidos': 'Rodríguez Hernández'},
    44: {'nombres': 'Erick', 'apellidos': 'Rodríguez Steller'},
    45: {'nombres': 'Aracelly', 'apellidos': 'Salas Eduarte'},
    46: {'nombres': 'Floria', 'apellidos': 'Segreda Sagot'},
    47: {'nombres': 'María Inés', 'apellidos': 'Solís Quirós'},
    48: {'nombres': 'Enrique', 'apellidos': 'Sánchez Carballo'},
    49: {'nombres': 'Roberto Hernán', 'apellidos': 'Thompson Chacón'},
    50: {'nombres': 'Daniel Isaac', 'apellidos': 'Ulate Valenciano'},
    51: {'nombres': 'Paola', 'apellidos': 'Valladares Rosado'},
    52: {'nombres': 'Otto Roberto', 'apellidos': 'Vargas Víquez'},
    53: {'nombres': 'Paola Viviana', 'apellidos': 'Vega Rodríguez'},
    54: {'nombres': 'Gustavo Alonso', 'apellidos': 'Viales Villegas'},
    55: {'nombres': 'José María', 'apellidos': 'Villalta Flórez-Estrada'},
    56: {'nombres': 'Sylvia Patricia', 'apellidos': 'Villegas Álvarez'},
    57: {'nombres': 'Zoila Rosa', 'apellidos': 'Volio Pacheco'}
}


# REGEXES ----

IGNORAR_LINEA = [
    re.compile(r'ACTA ORDINARIA N'),
    re.compile(r'^[0-9]{1,2}$'),
    re.compile('^$'),
    re.compile(r'(^[\sA-ZÑÁÉÍÓÚ°0-9\.\(\),º\-]+$)'),
    re.compile(r'^\n$')
]

HABLA_DIP = re.compile(r'Diputad. (?P<dip>[\w\s\-]*):')
HABLA_PRES = re.compile(r'President. (a\.? í\.?)?[\w\s]*:')

NOMBRE_ASIST = '\w+(\s+[\-\w]+)?,\s+\w+(\s{1,2}\w+)?(\s\(cc \w+\))?'
RE_TABLA_ASISTENCIA = r'\s*(?P<dip1>{0})\s*(?P<dip2>{0})?'.format(NOMBRE_ASIST)
LINEA_NOMBRES_DIP = re.compile(RE_TABLA_ASISTENCIA, re.I)

NOMBRE_CC = re.compile(r'(?P<apellidos>[\w\s\-]+?), (?P<nombres>[\s\w]+?) (?P<nombre_cc>\(cc \w+?\))')

LEVANTA_SESION = re.compile(r'se (levanta|tiene por terminada) la sesi[oó]n')

# ----------

db = os.environ['AA_db']

# ----------

def sacar_indice(nombre):
    """
    Devuelve el índice de ``DIPS`` al que corresponde el ``nombre``. Busca ya sea que los nombres
    y apellidos correspondan exactamente a un conjunto de ``DIPS``, o que haya diferencias leves
    (p.ej. faltas de ortografía, o solamente se usó uno de los nombres de pila).

    Esta función se debería reemplazar por algo más eficiente, tal vez usando word2vec.

    :param str nombre: nombre por analizar

    :returns i: "índice" (realmente es el 'key') de ``DIPS``
    :rtype: int
    """
    if ',' in nombre:
        apd, nmb = nombre.split(', ')
        nombre = ' '.join((nmb, apd))

    for i, info in DIPS.items():
        if nombre == ' '.join((info['nombres'], info['apellidos'])):
            # Si corresponde exactamente, devolver el índice-llave...
            return i

    # Si no, se da otra pasada haciendo un análisis más detallado, usando la versión extendida de
    # los nombres. Se calcula el máximo del coeficiente de similitud entre una iteración y el
    # coeficiente máximo hasta esa. Si es mayor a 0.99 se considera que corresponde, si no, se
    # completa la comparación para todos los nombres y se mantiene el coeficiente mayor encontrado.
    coef_max = {'coef': 0}
    brk = False
    for i, nombres in nombres_extra.items():
        for nmb in nombres:
            coef = difflib.SequenceMatcher(None, nmb, nombre).ratio()
            if coef > coef_max['coef']:
                coef_max['i'] = i
                coef_max['nmb'] = nmb
                coef_max['coef'] = coef
            if coef > 0.99:
                brk = True
                break
        if brk:
            break

    msg = ('Nombre recibido: {} - Nombre correspondiente: {} - Índice: {} '
           '- coeficiente: {}'.format(nombre, coef_max['nmb'], coef_max['i'], coef_max['coef']))
    print(msg)
    return coef_max['i']


def asistencia(pag):
    """
    Analiza la página de asistencia y saca la lista de nombres. Con eso, prepara la estructura de
    datos donde se llevará la cuenta de intervenciones y uso de la palabra en el plenario.

    :param str pag: transcripción de una página extraída por la función ``leer_pdf``

    :returns data: estructura de datos donde la llave es el índice que corresponde en ``DIPS``,
        y las llaves de intervenciones y palabras inicializadas en 0
    :returns bitacora: información para reportar bitácora
    :rtype: dict, str
    """
    titulo = 'Analizando asistencia (sólo imprime nombres sin correspondencia inmediata)'
    print(titulo)
    print('=' * len(titulo))
    presentes = []
    bitacora = []
    for linea in pag.splitlines():
        nombres = LINEA_NOMBRES_DIP.search(linea)
        if nombres:
            c = 0
            for v in nombres.groupdict().values():
                if v is None:
                    continue
                presentes.append(v.strip())
                c += 1
            bitacora.append(('nombres={}'.format(c), linea))
        else:
            bitacora.append(('', linea))
    presentes.sort()
    data = {}
    for nombre in presentes:
        i = sacar_indice(nombre)
        data[i] = {}
        data[i]['intervenciones'] = 0
        data[i]['palabras'] = 0
    print('')
    return data, bitacora


def finalizar_analisis(linea_1, linea_2):
    """
    Determina si debe finalizar el análisis. Encadena 2 líneas y busca si cumple la regex de las
    frases que se usan para terminar una sesión ("se levanta la sesión" o "se da por terminada
    la sesión").

    Se usan dos líneas porque en algunos casos, la frase está dividida en 2 líneas.

    :param str linea_1: línea del acta
    :param str linea_2: línea siguiente a ``linea_1``

    :return: se encontró la frase o no
    :rtype: bool
    """
    l = linea_1 + ' ' + linea_2
    return True if LEVANTA_SESION.search(l) else False


def analizar(contenido):
    """
    Extrae las métricas. Es un desorden, ¡pero funciona! (igual hay que mejorarlo)

    Empieza ignorando hasta encontrar la página donde se lista los/as asistentes. Saca esos datos
    a una estructura.

    Luego va a la siguiente página y línea por línea busca el encabezado cuando alguna/ún
    diputada/o tiene la palabra. Cuando la palabra la tiene el/la presidente/a, lo ignora (ya
    que en ese caso su función es solamente coordinar el uso de la palabra), pero cuando alguien
    tiene la palabra en calidad de diputada/o, busca quién es, y suma una intervención y aumenta
    el contador de palabras según la cantidad que haya en la línea, hasta encontrar otro encabezado.
    Así sigue hasta encontrar que se levanta la sesión, y ahí para de contar.

    :param object contenido: objeto ``pdftotext.PDF``

    :returns data: estructura de datos con los contadores actualizados
    :rtype: dict
    """
    bitacora = []

    asistencia_tomada = False
    midiendo_intervenciones = False
    terminar = False
    habla_presidente = False
    for num_pag, pag in enumerate(contenido):
        num_pag += 1
        if not asistencia_tomada:
            if 'diputados presentes' in pag.lower():
                data, _bitacora = asistencia(pag)
                titulo = 'Analizando acta'
                print(titulo)
                print('='*len(titulo))
                asistencia_tomada = True
                bitacora.extend(_bitacora)
                continue
            else:
                bitacora.extend([('{}:{}:'.format(num_pag, num_linea), linea)
                                  for num_linea, linea
                                  in enumerate(pag.splitlines())])
                continue
        if not midiendo_intervenciones:
            if not HABLA_DIP.search(pag) and not HABLA_PRES.search(pag):
                bitacora.extend([('{}:{}:'.format(num_pag, num_linea), linea)
                                  for num_linea, linea
                                  in enumerate(pag.splitlines())])
                continue
            midiendo_intervenciones = True
        # No usamos el enumerate directamente en el for porque hace falta tener acceso a la
        # línea anterior para determinar si se debe detener el análisis
        pag_enum = [(n, l) for n, l in enumerate(pag.splitlines())]
        for num_linea, linea in pag_enum:
            if terminar:
                bitacora.append(('', linea))
                continue
            linea_anterior = pag_enum[num_linea-1][1]
            if finalizar_analisis(linea_anterior, linea):
                terminar = True
                bitacora.append(('{}:{}:Finaliza el análisis'.format(num_pag, num_linea), linea))
                continue
            if any([regex.search(linea) for regex in IGNORAR_LINEA]):
                bitacora.append(('{}:{}:ignorar línea'.format(num_pag, num_linea), linea))
                continue
            if HABLA_PRES.search(linea):
                habla_presi = True
            habla_dip = HABLA_DIP.search(linea)
            if habla_dip:
                dip = habla_dip.groupdict()['dip']
                habla_presi = False
                se_quien_es = False
                i = sacar_indice(dip)
                data[i]['intervenciones'] += 1
                se_quien_es = True
                bitacora.append(('{}:{}:habla dip, id: {}, intervención # {}'
                                 .format(num_pag, num_linea, i, data[i]['intervenciones']),
                                         linea))
                if not se_quien_es:
                    raise ValueError('¿Quién es {}?'.format(linea))
                continue
            if habla_presi:
                bitacora.append(('{}:{}:habla presidenta/e'.format(num_pag, num_linea), linea))
                continue
            data[i]['palabras'] += len(linea.split())
            bitacora.append(('{}:{}:habla dip, id: {}, palabras {}'
                            .format(num_pag, num_linea, i, data[i]['palabras']), linea))

    if not terminar:
        raise ValueError('No se encontró el final del acta, regex esperada: '
                         '"{}"'.format(LEVANTA_SESION.pattern))

    return data, bitacora


def leer_pdf(archivo):
    """Convierte un pdf a una serie de strings que contienen cada página."""
    def _leer(arch):
        with open(arch, 'rb') as f:
            return pdftotext.PDF(f)
    try:
        return _leer(archivo)
    except FileNotFoundError:
        return _leer('pdf_originales/'+archivo)

def obtener_cmd_db(arch, fecha):
    """
    Como todavía no he montado el ORM lo que hago es imprimir el comando para insertar la info
    a la DB, y agrego los datos manualmente.
    """
    cont = leer_pdf(arch)
    data, bitacora = analizar(cont)
    records = []
    for i, info in data.items():
        records.append(str((fecha, i, info['intervenciones'], info['palabras'])))
    print('Total diputados/as presentes:', len(records), '\n')
    stmt = 'insert into {} (fecha, iddip, intervenciones, palabras) values '.format(db)
    stmt += ', '.join(records)
    print(stmt+'\n')
    return bitacora


def escribir_bitacora(bitacora):
    """Escribe archivo de bitacora."""
    print('Escribiendo bitácora')
    with open(os.path.join('bitacoras', fecha+'.log'), 'w') as f:
        for info in bitacora:
            f.write('{:45} | {}\n'.format(info[0], info[1]))


def extender_nombres():
    """
    Genera una lista con todas las opciones de nombres extraídos de ``DIPS``. Para los nombres de
    la forma "Apellido1 Apellido2, Nombre1 Nombre2" le agrega las siguientes opciones::

        Apellido1 Apellido2, Nombre1
        Apellido1 Apellido2, Nombre2
        Apellido1, Nombre1 Nombre2
        Apellido1, Nombre1
        Apellido1, Nombre2

    No tiene un return explícito, si no que el diccionario ``nombres_extra`` se hace global.
    """
    global nombres_extra
    nombres_extra = {}

    for i, info in DIPS.items():
        apds = [info['apellidos']]
        nmbs = [info['nombres']]

        if ' ' in nmbs[0]:
            primer_nm, segundo_nm = nmbs[0].split()
            nmbs.append(primer_nm)
            nmbs.append(segundo_nm)
        if ' ' in apds[0]:
            apds.append(apds[0].split()[0])

        for apd in apds:
            for nmb in nmbs:
                nombres_extra.setdefault(i, []).append(' '.join((nmb, apd)))


if __name__ == '__main__':
    archivo = sys.argv[1]
    fecha = archivo.split('/')[-1].split('.')[0]

    extender_nombres()

    bitacora = obtener_cmd_db(archivo, fecha)
    escribir_bitacora(bitacora)
