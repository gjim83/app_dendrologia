# Asamblea Abierta


## ¿Cómo funciona?

* **`/pdf_originales`:** contiene los archivos PDF descargados de la [página de la Asamblea Legislativa]( http://www.asamblea.go.cr/Centro_de_informacion/Consultas_SIL/Pginas/Sesiones%20y%20Actas%20de%20sesiones.aspx). La página de la AL es en general *muy* lenta, así que prefiero sufrir una vez y guardarlos en el repositiorio para futura referencia.
* **`/bitacoras`:** contiene la bitácora resultante del análisis de un archivo. Principalmente para debuguear y asegurar que el análisis es correcto, pero si alguien duda de los datos, ahí los puede corroborar.
* **`analizar_acta.py`:** script que hace el análisis.

## Ejemplo
```
$ gtime python analizar_acta.py pdf_originales/2018-03-15.pdf 2018-03-15
nombre: Atencio Delgado, Ruperto Marvin - id: 8 - por probabilidad, opciones: ['Atencio Delgado, Ruperto Marvin', 'Atencio Delgado, Ruperto', 'Atencio Delgado, Marvin']
nombre: Monge Salas, Rony (cc Ronny) - id: 34 - por probabilidad, opciones: ['Monge Salas, Rony (cc Ronny)', 'Monge Salas, Rony', 'Monge Salas, (cc Ronny)', 'Monge Salas, Rony', 'Monge Salas, (cc', 'Monge Salas, Ronny)']
nombre: Mora Castellanos, Ana Patricia - id: 36 - por probabilidad, opciones: ['Mora Castellanos, Ana Patricia', 'Mora Castellanos, Ana', 'Mora Castellanos, Patricia']
nombre: Ramírez Zamora, Gonzalo Alberto - id: 44 - por probabilidad, opciones: ['Ramírez Zamora, Gonzalo Alberto']
Total diputados/as presentes: 41

insert into <tabla> (fecha, iddip, intervenciones, palabras) values ('2018-03-15', 1, 1, 693), ('2018-03-15', 2, 0, 0), ('2018-03-15', 5, 0, 0), ('2018-03-15', 7, 0, 0), ('2018-03-15', 8, 0, 0), ('2018-03-15', 10, 0, 0), ('2018-03-15', 11, 0, 0), ('2018-03-15', 12, 1, 1415), ('2018-03-15', 14, 1, 218), ('2018-03-15', 15, 1, 65), ('2018-03-15', 16, 0, 0), ('2018-03-15', 17, 1, 1593), ('2018-03-15', 18, 0, 0), ('2018-03-15', 22, 3, 2222), ('2018-03-15', 23, 2, 3812), ('2018-03-15', 25, 1, 995), ('2018-03-15', 26, 2, 570), ('2018-03-15', 27, 0, 0), ('2018-03-15', 29, 0, 0), ('2018-03-15', 30, 0, 0), ('2018-03-15', 31, 1, 618), ('2018-03-15', 32, 0, 0), ('2018-03-15', 33, 0, 0), ('2018-03-15', 34, 1, 146), ('2018-03-15', 35, 0, 0), ('2018-03-15', 36, 2, 1859), ('2018-03-15', 37, 0, 0), ('2018-03-15', 38, 0, 0), ('2018-03-15', 40, 2, 363), ('2018-03-15', 42, 0, 0), ('2018-03-15', 43, 0, 0), ('2018-03-15', 44, 0, 0), ('2018-03-15', 45, 0, 0), ('2018-03-15', 46, 0, 0), ('2018-03-15', 48, 7, 901), ('2018-03-15', 49, 0, 0), ('2018-03-15', 50, 0, 0), ('2018-03-15', 51, 0, 0), ('2018-03-15', 52, 2, 1907), ('2018-03-15', 55, 3, 220), ('2018-03-15', 56, 0, 0)

Escribiendo bitácora
0.35user 0.04system 0:00.48elapsed 82%CPU (0avgtext+0avgdata 18380maxresident)k
74inputs+5outputs (761major+4061minor)pagefaults 0swaps
```
