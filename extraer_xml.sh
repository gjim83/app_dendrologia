#!/bin/sh
# Autor: Esmit Perez
# Fecha: Mayo 2018
#
# Convierte las actas de la Asamblea en documentos estructurados (XML) 
# que luego pueden ser alimentados a pipelines más avanzados.
#
# Requerimientos: 
# - pdftotext: 
#   en Mac OS X: brew cask install pdftotext

rm -fr actas_txt
rm -fr actas_xml
rm -fr tmp

# Preparemos el workspace
mkdir -p actas_txt
mkdir -p actas_xml
mkdir -p tmp

###################################################
# Saca una versión más corta y específica del acta
###################################################
for pdf in pdf_originales/*.pdf; do
    # 1- Convertir a Texto
    _CURR_FILE="$(basename "$pdf" .pdf).txt"
    _CURR_FILE_CLEAN="$(basename "$pdf" .pdf).clean.txt"

    pdftotext -layout -enc UTF-8 "$pdf" "actas_txt/$_CURR_FILE"

    # Si quisieramos solo la pagina 2, sería:
    # pdftotext -layout -enc UTF-8 -f 2 -l 2  "$pdf" "actas_txt/$_CURR_FILE"

    # 2- Elimina anexos,  limpia encabezados de pagina y números de página
    awk '/ASAMBLEA LEGISLATIVA DE LA REPÚBLICA DE COSTA RICA/,/^[[:space:]]*ANEXOS$/' "actas_txt/$_CURR_FILE"\
    | sed -e '/ACTA ORDINARIA N./d'  \
    | sed -e '/![0-9]*$/d' > "actas_txt/$_CURR_FILE_CLEAN" 
done


###################################################
# Obtener lista de diputados a partir de 
# tabla "Presentes" en todas las actas disponibles
# 
# Aún no sé para que podría servir, pero si un diputado
# eventualmente es reemplazado (renuncia, etc)
# su nombre dejará de aparecer, pero seguiremos teniendo un 
# tipo de histórico
###################################################

# - awk: con la coma (,) escoja el texto de los presentes
# - elimine los delimitadores del bloque
# - borre las lineas vacías #| sed -E -e 's/^[[:space:]]+//g' \  #
# - cambie los espacios de tabulacion por _'s
# - reemplace los _'s por nuevas lineas
# - elimine cualquier espacio al inicio de la linea 
# - reemplace los caracteres especiales (diacritics)
#   pero iconv convierte é en 'e y ñ en ~n...así que reemplace esos
# - deje solo los que tengan formato "apellido, nombre"
# - si el nombre, por error, le pusieron un caracter extra (no letra), quitelo
# - casos especiales (Flores Estrada, Dolanesco)
#   Oscar Mauricio Cascante en un acta sale con 2 nombres y en otra con 1
#   asi que para esta parte dejo solo el mas completo
# - borre las líneas vacías
# - ordene e imprima solo las lineas unicas
awk '/Diputados presentes/,/ÍNDICE/' actas_txt/*.clean.txt \
| sed 's/Diputados presentes//' \
| sed 's/ÍNDICE//' \
| sed -E -e 's/[[:space:]]{2,2}/_/g' \
| tr '_' '\n' \
| sed -E -e 's/^[[:space:]]+//g' \
| iconv -f utf8 -t ascii//TRANSLIT \
| sed "s/[~']//g" \
| grep "," \
| sed "s/[^[:alpha:]]$//g" \
| sed "s/Florez Estrada/Florez-Estrada/g" \
| sed "s/Donalescu/Dolanescu/g" \
| sed "s/Warner Alberto/Wagner Alberto/g" \
| sed "s/^Cascante, Oscar Mauricio//g" \
| sed '/^$/d' \
| sort | uniq > actas_txt/todos_diputados.txt


###################################################
# Convertir a XML (básico)
###################################################

# analice cada acta ya en "limpio"
for acta in actas_txt/*clean.txt; do
    # variables para algunos nombres de archivo que luego usaremos
    _CURR_FILE_FRAGMENT="tmp/$(basename "$acta" .clean.txt).fragment"
    _CURR_FILE_XML="tmp/$(basename "$acta" .clean.txt).xml"

    echo "🚨 Procesando $acta ... 🚨 "

    # casi la misma rutina arriba documentada, excepto que no saco
    # a Oscar Mauricio Cascante que podría sí aparecer con ambos nombres
    # en el acta actualmente procesada
    awk '/Diputados presentes/,/ÍNDICE/' "$acta" \
        | sed 's/Diputados presentes//' \
        | sed 's/ÍNDICE//' \
        | sed -E -e 's/[[:space:]]{2,2}/_/g' \
        | tr '_' '\n' \
        | sed -E -e 's/^[[:space:]]+//g' \
        | grep "," \
        | sed "s/[^[:alpha:]]$//g" \
        | sed "s/Florez Estrada/Florez-Estrada/g" \
        | sed "s/Donalescu/Dolanescu/g" \
        | sed "s/Warner Alberto/Wagner Alberto/g" \
        | sed '/^$/d' \
        | sort | uniq \
        | sed -E "s@([[:alpha:][:blank:]\-]+),([[:blank:]])?([[:alpha:][:blank:]\-]+)@<diputado><nombre>CDATA_START\3CDATA_END</nombre><apellidos>CDATA_START\1CDATA_END</apellidos></diputado>@g" \
    > tmp/presentes.xml

    # ya con la lista de diputados podemos hacer algunos analisis simples
    # como sacar el cuorum
    CUORUM=`wc -l tmp/presentes.xml | sed -E 's/^[[:blank:]]+//g' | cut -f1 -d' '`

    # - Si alguna linea dice "Diputado Fulano de Tal:"
    # taggeela como un fragmento de diputado
    # - Si caso contrario comienza con "Presidente Fulano de Tal:"
    # toma en cuenta que puede ser el interino (a.i.) y lo marca como tal
    # - luego, cambiamos el valor default tontillo por una bandera booleana decente
    # tambien "cerramos" los fragmentos, asumo que cuando hay un <fragmento>
    # justo ante de ese hay otro, ergo, lo cerramos con </fragmento>
    # - tambien meto uno cuasi-CDATA para procesamiento posterior
    # - "cierro" el documento, asumo que la frase "se levanta la sesion" siempre estara
    sed -E \
        -e 's/President(e|a) de la República (.+):/<fragmento tipo="mandatario" nombre="\2">CDATA_START/g'\
        -e 's/Diputad(o|a) (.+):/<fragmento tipo="diputado" nombre="\2">CDATA_START/g' \
        -e 's/President(e|a) (a\. (i|í)\.? )?(.+):/<fragmento tipo="presidente" nombre="\4" interino="\2">CDATA_START/g'\
        "$acta" \
    | sed -E \
        -e 's/interino="a. í. "/interino="true"/g' -e 's/interino=""/interino="false"/g' \
        -e 's%<fragmento%CDATA_END</fragmento><fragmento%g' \
        -e 's/(se levanta la sesión.)/\1CDATA_END<\/fragmento><fragmento tipo="cierre">CDATA_START/g' \
    > $_CURR_FILE_FRAGMENT

    # OK, vamos al futbol. Contruyamos el XML válido final
    # defina el root node como <acta>
    echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?><acta>" > "$_CURR_FILE_XML"

    # populemos la tabla de atendencia y el quorum derivado de la extracción anterior
    echo "<atendencia cuorum=\"$CUORUM\">" >> "$_CURR_FILE_XML"
    cat tmp/presentes.xml >> "$_CURR_FILE_XML"
    echo "</atendencia>" >> "$_CURR_FILE_XML"

    # la logica anterior nos deja un </fragmento> sin cerrar al inicio
    # entonces empatamos el pedacito de <fragmento> inicial que va con ese
    # por default es el de apertura.
    echo "<fragmento tipo=\"apertura\">CDATA_START" >> "$_CURR_FILE_XML"

    # escribimos el XML que generamos arriba
    cat "$_CURR_FILE_FRAGMENT" >> "$_CURR_FILE_XML"

    # cerramos el documento, para que sea well-formed.
    echo "CDATA_END</fragmento></acta>" >> "$_CURR_FILE_XML"

    # - reemplazo los cuasi-CDATA por los correctos
    # la razón de que las expresiones de 'sed' se hacian (aun más) ilegibles
    # - ademas deshágase de los control characters que corrompen el XML
    # Nota: creo que son "artifacts" de la conversion pdf -> txt

    echo "⚡️ Escribiendo XML...⚡️"
    sed -i -E \
        -e "s/CDATA_START/<![CDATA[/g" \
        -e "s/CDATA_END/]]>/g" \
        -e "s/[[:cntrl:]]//" \
        "$_CURR_FILE_XML"
    
    # limpieza del workspace
    mv "$_CURR_FILE_XML" actas_xml
    rm "$_CURR_FILE_FRAGMENT"
    rm tmp/presentes.xml

    # ce fini.

done
