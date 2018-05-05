#!/bin/sh
# Autor: Esmit Perez
# Fecha: Mayo 2018
# ⚠️ ⚠️ PRUEBA DE CONCEPTO ⚠️ ⚠️
# 
# Analiza las actas de la Asamblea estructuradas (XML) 
#
# Requerimientos:  
# - xmllint
# - xpath
# - xml (xmlstarlet) 

# sacar cuorum/atendencia
echo "Atendencia:"
xmllint --xpath 'count(/acta/atendencia/diputado/apellidos)' actas_xml/2018-2019-PLENARIO-SESION-1.xml 

echo 
# cuantas intervenciones hizo el presidente (no interino)
echo "Intervenciones del presidente"
xmllint --xpath 'count(/acta/fragmento[@tipo="presidente" and @interino="false"])' actas_xml/2018-2019-PLENARIO-SESION-1.xml

echo

# cuenta palabras del presidente interino
echo "Cuantas palabras dijo el presidente interino"
xmllint --xpath 'string-length(/acta/fragmento[@tipo="presidente" and @interino="true"]/text())' actas_xml/2018-2019-PLENARIO-SESION-2.xml 

echo

# xpath parece no manejar bien los diacritics, 
# xmllint lo hace pero se come los \n entre resultados :(
echo "Orden de intervenciones ("
xpath actas_xml/2018-2019-PLENARIO-SESION-1.xml '//fragmento[@tipo="diputado"]/@nombre'
