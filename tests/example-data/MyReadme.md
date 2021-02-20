#  Trabajo de Investigación CC

- [Trabajo de Investigación CC](#trabajo-de-investigación-cc)
  - [1. Metodología](#1-metodología)
  - [2. Decisión del diseño](#2-decisión-del-diseño)
    - [2.1. Primeros Pasos](#21-primeros-pasos)
  - [3. Tests](#3-tests)
    - [3.1. Contexto:](#31-contexto)
    - [3.2. Test throughput y latency](#32-test-throughput-y-latency)
      - [3.2.1. Lanzamiento](#321-lanzamiento)
      - [3.2.2. Resultados generados](#322-resultados-generados)
    - [3.3. Test 1](#33-test-1)
      - [3.3.1. Lanzamiento](#331-lanzamiento)
      - [3.3.2. Resultados generados](#332-resultados-generados)
    - [3.4. Test2](#34-test2)
      - [3.4.1. Lanzamiento:](#341-lanzamiento)
      - [3.4.2. Resultados generados](#342-resultados-generados)
    - [3.5. Gráficas de resultados](#35-gráficas-de-resultados)
  - [4. Test vía Python](#4-test-vía-python)

## 1. Metodología

Para abordar las pruebas, primero se ha creado el campo de pruebas a medida para favorecer la obtención de los resultados deseados. Para ello las imágenes son creados de la siguiente manera:

Las imágenes generadas para los tests o benchmark realizados tienen como base `ubuntu:18.04`

Primero se crea una imagen(base) simple a partir del siguiente Dockerfile:

```dockerfile
FROM ubuntu:18.04
```

Al realizar un **Inspect** sobre esta imagen , se observan un total de 3 capas:

```json
 "Layers": [
 	"sha256:80580270666742c625aecc56607a806ba343a66a8f5a7fd708e6c4e4c07a3e9b",
	"sha256:3fd9df55318470e88a15f423a7d2b532856eb2b481236504bf08669013875de1",
	"sha256:7a694df0ad6cc5789a937ccd727ac1cda528a1993387bf7cd4f3c375994c54b6"
     ]
```

En las pruebas realizadas se parte de un _Dockerfile.base_ donde se generan diferentes ficheros a tratas dentro de la carpeta /test:

```dockerfile
FROM ubuntu:18.04

RUN mkdir -p /test/big-files /test/small-files \
&& for i in $(seq 0 9); do \
       for size in 1M 8M 32M 128M; do \
          dd if=/dev/urandom of=/test/big-files/${size}-${i}.bin bs=${size} count=1 2>/dev/null; \
      done; \
   done \
&& for i in $(seq 0 10000); do \
     dd if=/dev/urandom of=/test/small-files/$i bs=512 count=1 2>/dev/null; \
   done

COPY /scripts/. /usr/local/
```

Este da como resultados las misma capas que el anterior debido a que provienen de la misma base y nuevas capas generadas por cada nueva instrucción en el fichero _Dockerfile.base_:

```json
 "Layers": [
      "sha256:80580270666742c625aecc56607a806ba343a66a8f5a7fd708e6c4e4c07a3e9b",
      "sha256:3fd9df55318470e88a15f423a7d2b532856eb2b481236504bf08669013875de1",
      "sha256:7a694df0ad6cc5789a937ccd727ac1cda528a1993387bf7cd4f3c375994c54b6",
      "sha256:d8bdd3f330e618bb018d5eb391610c21701b66a10d2092548c7f35eceef93f65",
      "sha256:eb58b7f49ecb05d709a90a20c060dc0b41051992f6f118d983b605089eefa7e2"
        ]
```

Desde arriba hacia abajo, la capa donde se han generado los primeros ficheros de muestra estarían en la **4ª capa** `sha256:7a694df0ad6cc5789a937ccd727ac1cda528a1993387bf7cd4f3c375994c54b6`, es decir, a una capa desde la capa R/W al tratar con el contenedor generado de la imagen.

> Nota: El nombre de la capa puede variar si se generan de nuevo las imágenes, pero el orden se mantiene.

Por último para la imagen de pruebas, se basa en esta última imagen:

```dockerfile
FROM manu/mybaseimage:1.0
RUN mkdir -p /test2/big-files
RUN mkdir -p /test2/small-files
WORKDIR /usr/src/app
RUN for i in $(seq 0 9); do \
        for size in 1M 8M 32M 128M; do \
            dd if=/dev/urandom of=/test2/big-files/${size}-${i}.bin bs=${size} count=1 2>/dev/null; \
        done; \
    done \
&& for i in $(seq 0 10000); do \
        dd if=/dev/urandom of=/test2/small-files/$i bs=512 count=1 2>/dev/null; \
    done
RUN mkdir -p myvolumen
RUN mkdir -p results
COPY /scripts/. /usr/src/app/.
RUN mkdir -p /test3/big-files /test3/small-files \
&&  for i in $(seq 0 9); do \
        for size in 1M 8M 32M 128M; do \
            dd if=/dev/urandom of=/test3/big-files/${size}-${i}.bin bs=${size} count=1 2>/dev/null; \
        done; \
    done \
&& for i in $(seq 0 10000); do \
        dd if=/dev/urandom of=/test3/small-files/$i bs=512 count=1 2>/dev/null; \
    done
COPY /node_project/. ./web
```

Se generan nuevas capas adicionales:

```json
 "Layers": [
     "sha256:80580270666742c625aecc56607a806ba343a66a8f5a7fd708e6c4e4c07a3e9b",
     "sha256:3fd9df55318470e88a15f423a7d2b532856eb2b481236504bf08669013875de1",
     "sha256:7a694df0ad6cc5789a937ccd727ac1cda528a1993387bf7cd4f3c375994c54b6",
     "sha256:d8bdd3f330e618bb018d5eb391610c21701b66a10d2092548c7f35eceef93f65",
     "sha256:eb58b7f49ecb05d709a90a20c060dc0b41051992f6f118d983b605089eefa7e2",

     "sha256:897c4cd95ebc3238c9fc5a06733990fb6212355cff1d074a63e6caf28f3b8111",
     "sha256:262aec81cc2d966eb5dee503a1ccc1d506ab43ef57a1427e1c4e686bd96fe85b",
     "sha256:580521ef7b8cdec061b09b2f72acba4ba4fe50b722e08e820a021b466ef15729",
     "sha256:0baebc6e32f5fb4e53aba40928d785eebe2fa69d5409c856bdb667f184667092",

     "sha256:066953c49a4874924527a0f2f43b4b28838194a72829019bf5e61b36efeec176",
     "sha256:e6ccbb61242b68c8864dbaf6109093ffcc9ec1e7a54e03712ea9cf366c8e0e6f",
     "sha256:477d53b14e97505229ebbe70294942c53ef4356e5378124fc00b55cf35921e6e",

     "sha256:575f18911f4c639d240510fa6a78e6a88148316d4860639de6e5594a6f8ba94f"
        ]
```

Ahora tenemos los mismo ficheros de pruebas generados en las siguientes capas, empezando a contar desde la capa más superficial:

- Capa 1 - /test3
- Capa 5 - /test2
- Capa 10 - /test

Respecto a los tests, se hará referencia a la **Capa 1** (/_test3_) como valor numérico **1**, debido a que la **Capa R/W** será la **0**.

## 2. Decisión del diseño

Existen diferentes tipos de scripts para llevar a cabo el estudio, unos son creados para ofrecer una automatización durante el lanzamiento y otros son dedicados a realizar las operaciones oportunas que se desean medir (ej operaciones escritura o lectura.)

Los tests realizados para la realización y medición de operaciones:

- read-file-by-size.sh
- read-to-files.sh
- write-files-by-size.sh
- write-to-files.sh

Los scripts realizados para el lanzamiento automatizado:

- dd-benchmark.sh
- test1-read-write-benchmark.sh
- test2-read-write-benchmark

El script realizado para la construcción del campo de pruebas:

- docker-build.sh

Como particularidad el ejecutable utilizado para realizar pruebas de rendimiento y latencia, lanza directamente el comando a ejecutar (**dd**).

Por tanto, para agilizar las pruebas a realizar, se ha construido una serie de scripts tanto para la creación y eliminación de nuestro campo de pruebas, como para el lanzamiento de tests y la captura de las salidas generadas por estos. A continuación se profundiza un poco mas en cada uno de los distintos script y tests.

### 2.1. Primeros Pasos

Generar el campo de pruebas para la posterior realización de los tests. Todo el código implementado esta contenido en la carpeta campo-pruebas-docker y pyhton-benchmark-graph

Lanzamiento del primer script:

```
PWD/campo-pruebas-docker# ./docker-build.sh
```

Pasos que se siguen:

1. Comprobar que se lanza como sudo
2. Parar el contenedor de pruebas en caso de estar en marcha
3. Eliminar el volumen donde se almacenan los resultados generados por el contenedor
4. En caso de no existir las imágenes, se crea la Imagen Base y la Imagen test basada en la Base
5. Crear el volumen compartido con el mismo tipo de muestra que en la carpeta /test de la imagen Base y la imagen
6. Crear el volumen compartido donde se almacenarán los resultados
7. Arrancar la imagen(*manu/test1:1.0*) creada con los "_bind mount_" correspondientes, con Test1 como nombre de contenedor

```
./docker-build.sh delete
```

1. Elimina los contenedores utilizados
2. Elimina las imágenes creadas por este scripts
3. Elimina los dos volúmenes creados

Volumen de datos para los test:

```
/var/lib/docker/volumes/data_test/_data
├── big-files
│   ├── 128M-0.bin
│................
│   ├── 128M-9.bin
│   ├── 1M-0.bin
│...............
│   ├── 1M-9.bin
│   ├── 32M-1.bin
│................
│   ├── 32M-9.bin
│   ├── 8M-1.bin
│...............
│   └── 8M-9.bin
├── generate-files-container
└── small-files
    ├── 0
    ├── 1
	|.......
    ├── 10000
```

## 3. Tests

### 3.1. Contexto:

- Los test son lanzados en el contenedor de pruebas (_Test1_) de la imagen: **manu/test1:1.0**.

- Los resultados son almacenados en **/usr/src/app/myresults**, que corresponden en nuestra maquina **host** a la dirección:
  **/var/lib/docker/volumes/myresults/\_data/**

- Los resultados generados por los siguientes scripts:

  Carpeta **out-container-scripts**:

  ```
  dd-benchmark.sh
  test1-read-write-benchmark.sh
  test2-read-write-benchmark.sh
  ```

  Son almacenados en el directorio actual donde son lanzados, con el  patrón: **image-1-**<storage driver>

  > Nota: El nombre storage driver  es el controlador de almacenamiento actualmente utilizado (_docker info_)

  Para la creación de las gráficas, dicho directorio deberá ser copiado a **/my-results**, ejemplo:

  ```
  /my-results
  ├── image-1-aufs
  ├── image-1-overlay
  ├── image-1-overlay2
  ```


### 3.2. Test throughput y latency

Para el test de rendimiento y latencia se ha generado un script donde se lanza el comando **dd** con diferentes patrones dependiendo de la salida que deseamos como resultado.

Por ejemplo, en caso de la **latencia** se opta por el siguiente patrón del comando **dd**:

```
dd if=/dev/zero of=(carpeta de destino) bs=512 count=1000 oflag=dsync
```

**output**: `512000 bytes (512 kB, 500 KiB) copied, 0.997219 s, 513 kB/s`

> Con esta cadena, 512 bytes serán escritos 1000 veces, por tanto la latencia:
> 0.997219s / 1000 = 0.000997s

En caso de obtener el **throughput**:

```powershell
dd if=/dev/zero of=(carpeta de destino) bs=1G count=1 oflag=dsync
```

Un Gigabyte será escrito. Para este test debemos de tener una RAM con memoria suficiente para 1GB, sino es el caso, el parámetro **bs** se debe de reducir.

Tenemos que tener en cuenta que estamos trabajando sobre un equipo con **ssd nvme** donde las velocidades de escritura y de lectura son bastante altas, en un **HDD** tradicional los tiempos serían mucho más elevados.

#### 3.2.1. Lanzamiento

```powershell
sudo ./scripts/dd-benchmark.sh <Number repeats>
```

Existen diferentes modo de lanzar los test, alguno de ellos permiten sen lanzados sin necesidad de acceder dentro del contenedor. A continuación una serie de lanzamientos sobre el actual test comentado:

**Dentro del contenedor**

```shell
$sudo ./scripts/dd-benchmark.sh 3

[1] Test[throughput] host...
[2] Test[throughput] container docker on /usr/src/app/myvolumen ....
[2] Test[throughput] container docker on /test ....
[2] Test[throughput] container docker on /test3 ....

[1] Test[latency] host...
[2] Test[latency] container docker on /usr/src/app/myvolumen ....
[2] Test[latency] container docker on /test ....
[2] Test[latency] container docker on /test3 ....
```

**Fuera del contenedor (sin arrancarlo)**

> Nota: El contenedor deberá de estar parado o eliminado previamente

```
$sudo ./dd-benchmark <<n repeticiones>>
```

Si no se especifica ningún parámetro numérico, por defecto numero repeticiones será 1.

#### 3.2.2. Resultados generados

Genera la carpeta **dd-test-results** (_En el mismo directorio donde se haya ejecutado el script_) con:

```
./image-1-<current-storage-driver>/dd-test-results
├── latency-0
├── latency-1
├── latency-10
├── latency-5
├── latency-volumen
├── throughput-0
├── throughput-1
├── throughput-10
├── throughput-5
└── throughput-volumen
```

### 3.3. Test 1

Consiste el probar el tiempo de lectura y de escritura de diferentes tamaños de ficheros, variando el número de capas donde estos ficheros se encuentran. Al principio del documento se explica en más detalle las diferentes ubicaciones los ficheros según la capa.

Se opera solo con la carpeta **big-files** (muestra), cuyo contenido es el siguiente:

- **Big Files**:
  - 10 ficheros de 1M
  - 10 ficheros de 8M
  - 10 ficheros de 32M
  - 10 ficheros de 128M

Procedimiento:

Se realiza el calculo del tiempo para las diferentes ubicaciones (_Capa 10,Capa 5,Capa 1 Capa superior R/W y Carpeta compartida_) de la carpeta big-files:

- Tiempo de lectura de:
  - 10 ficheros de 1M n veces (n=10 default)
  - 10 ficheros de 8M n veces
  - 10 ficheros de 32M n veces
  - 10 ficheros de 128M n veces
- Tiempo de escritura de:

  - 10 ficheros de 1M n veces (n=10 default)
  - 10 ficheros de 8M n veces
  - 10 ficheros de 32M n veces
  - 10 ficheros de 128M n veces

#### 3.3.1. Lanzamiento

**Dentro del contenedor**

```powershell
root@4aac9191c35e:/usr/src/app# ./benchmark-command.sh -t 1 -s all
[CREATE] big-files and small-files in [/usr/src/app/test-current-layer] ...
[LAUNCH]\[SIMPLE TEST] Script of write in folder: /usr/src/app/myvolumen
[LAUNCH]\[SIMPLE TEST] Script of read in folder: /usr/src/app/myvolumen
[LAUNCH]\[SIMPLE TEST] Script of write in folder: /usr/src/app/test-current-layer
[LAUNCH]\[SIMPLE TEST] Script of read in folder: /usr/src/app/test-current-layer
[LAUNCH]\[SIMPLE TEST] Script of write in folder: /test3
[LAUNCH]\[SIMPLE TEST] Script of read in folder: /test3
[LAUNCH]\[SIMPLE TEST] Script of write in folder: /test2
[LAUNCH]\[SIMPLE TEST] Script of read in folder: /test2
[LAUNCH]\[SIMPLE TEST] Script of write in folder: /test
[LAUNCH]\[SIMPLE TEST] Script of read in folder: /test
```

**Fuera del contenedor (sin arrancarlo)**

```
$/campo-pruebas-docker# ./out-container-scripts/test2-read-write-benchmark.sh
```

#### 3.3.2. Resultados generados

```powershell
# ll /var/lib/docker/volumes/myresults/_data/image-1/test2 or ./image-1/test1
drwxr-xr-x 2 root root 4096 nov 15 17:50 ./
drwxr-xr-x 4 root root 4096 nov 15 17:42 ../
-rw-rw-rw- 1 root root 31 nov 20 14:39 read-128-big-file-0
-rw-rw-rw- 1 root root 30 nov 20 14:39 read-128-big-file-1
-rw-rw-rw- 1 root root 30 nov 20 14:39 read-128-big-file-10
-rw-rw-rw- 1 root root 30 nov 20 14:39 read-128-big-file-volumen
-rw-rw-rw- 1 root root 30 nov 20 14:39 read-128-big-file-5
# read-[1,8,32,128]-big-file-[0,1,2,5,10].................
-rw-rw-rw- 1 root root 20 nov 20 14:39 write-128-big-file-0
-rw-rw-rw- 1 root root 20 nov 20 14:39 write-128-big-file-1
-rw-rw-rw- 1 root root 22 nov 20 14:39 write-128-big-file-10
-rw-rw-rw- 1 root root 22 nov 20 14:39 write-128-big-file-volumen
-rw-rw-rw- 1 root root 22 nov 20 14:39 write-128-big-file-5
# write-[1,8,32,128]-big-file-[0,1,2,5,10].................
```

### 3.4. Test2

En este caso, se realiza la lectura y escritura del contenido de dos carpetas **small-files** y **big-files**, cuyo contenido es el siguiente:

- **Small files**: Contiene un total de 10000 ficheros de 521 bytes
- **Big Files**:
  - 10 ficheros de 1M
  - 10 ficheros de 8M
  - 10 ficheros de 32M
  - 10 ficheros de 128M

Se realiza el cálculo del tiempo para las diferentes ubicaciones (_Capa 10, Capa 5, Capa 1 Capa superior R/W y Carpeta compartida_):

- Tiempo de lectura de los ficheros de /small-files
- Tiempo de lectura de los ficheros de /big-files
- Tiempo de escritura de los ficheros de /small-files
- Tiempo de escritura de los ficheros de /big-files

#### 3.4.1. Lanzamiento:

**Dentro del contenedor**

```powershell
root@4aac9191c35e:/usr/src/app#  ./benchmark-command.sh -n 10 -t 2
 [CREATE] big-files and small-files in [/usr/src/app/test-current-layer] ...
 [LAUNCH] Test 2 in /usr/src/app/test-current-layer ...
 [LAUNCH] Test 2 in /test3 ...
 [LAUNCH] Test 2 in /test2 ...
 [LAUNCH] Test 2 in /test ...
```

**Fuera del contenedor (sin arrancarlo)**

```
$/campo-pruebas-docker# ./out-container-scripts/test2-read-write-benchmark.sh
```

#### 3.4.2. Resultados generados

```powershell
# ll /var/lib/docker/volumes/myresults/_data/image-1/test2 or ./image-1/test2
drwxr-xr-x 2 root root 4096 nov 15 17:50 ./
drwxr-xr-x 4 root root 4096 nov 15 17:42 ../
-rw-rw-rw- 1 root root 31 nov 20 14:39 read-128-big-file-0
-rw-rw-rw- 1 root root 30 nov 20 14:39 read-128-big-file-1
-rw-rw-rw- 1 root root 30 nov 20 14:39 read-128-big-file-10
-rw-rw-rw- 1 root root 30 nov 20 14:39 read-128-big-file-volumen
-rw-rw-rw- 1 root root 30 nov 20 14:39 read-128-big-file-5
# read-[1,8,32,128]-big-file-[0,1,2,5,10].................
-rw-rw-rw- 1 root root 20 nov 20 14:39 write-128-big-file-0
-rw-rw-rw- 1 root root 20 nov 20 14:39 write-128-big-file-1
-rw-rw-rw- 1 root root 22 nov 20 14:39 write-128-big-file-10
-rw-rw-rw- 1 root root 22 nov 20 14:39 write-128-big-file-volumen
-rw-rw-rw- 1 root root 22 nov 20 14:39 write-128-big-file-5
# write-[1,8,32,128]-big-file-[0,1,2,5,10].................

```

### 3.5. Gráficas de resultados

Para crear gráficas en base a los datos obtenido se ha basado en la implementación realizada por el usuario [chriskuehl](https://github.com/chriskuehl).

[docker-storage-benchmark](https://github.com/chriskuehl/docker-storage-benchmark)

Para este proyecto:

- Creado el fichero **make_simple_graph.py** basado en _make_graph.py_
- Creado el fichero **make_complex_graph.py** basado en _make_simple_graph_ para realizar gráficos que engloba 3 UFS Storage Driver utilizados en este proyecto (_overlay2, overlay y aufs_)
- Se ha mejorado la creación de las gráficos (Tiempo de creación y ajustes gráficos)
- Adaptado para el tipo de muestra y resultados de este proyecto
- Creación de distintas gráficas dependiendo del tipo de resultado (_latency, throughput, read or write files by size_)
- Valores (_labels_) de throuphut y latency (resultados) en cada bar de la gráfica

Vía Python:

**Simple Graph**

```
python:$ python3 make_simple_graph.py STORAGE-DRIVER
```

**STORAGE-DRIVER:** 'aufs', 'overlay', 'overlay2'

Genera una serie de gráficas basados en los resultados de los test de latencia y rendimiento, junta al test 1.

**Gráficas generadas** (e.j overlay2):

```
python:$ls -l graphs/
-rw-rw-r-- 1 manuel manuel 14532 nov 20 22:50 mygraph-latency-overlay2.png
-rw-rw-r-- 1 manuel manuel 33945 nov 20 22:50 mygraph-read-overlay2.png
-rw-rw-r-- 1 manuel manuel 16413 nov 20 22:50 mygraph-throughput-overlay2.png
-rw-rw-r-- 1 manuel manuel 26939 nov 20 22:50 mygraph-write-overlay2.png
-rw-rw-r-- 1 manuel manuel 26940 nov 20 22:50 mygraph-read-small-files-overlay2.png
-rw-rw-r-- 1 manuel manuel 26850 nov 20 22:50 mygraph-write-small-files-overlay2.png
```

Una gráfica de salida:

<img src="./python-benchmark-graphs/graphs/mygraph-write-overlay2.png" style="zoom:80%;" />

**Lanzamiento de Complex Graph**

```
python:$ python3 make_complex_graph.py
```

**Gráficas generadas:**

```
python:$ls -l graphs/
-rw-rw-r-- 1 manuel manuel 14532 nov 20 22:50 mygraph-latency-overall.png
-rw-rw-r-- 1 manuel manuel 33945 nov 20 22:50 mygraph-read-small-files.png
-rw-rw-r-- 1 manuel manuel 16413 nov 20 22:50 mygraph-throughput-overall.png
-rw-rw-r-- 1 manuel manuel 26939 nov 20 22:50 mygraph-write-small-files.png
```

Una gráfica de salida:

<img src="./python-benchmark-graphs/graphs/mygraph-throughput-overall.png" style="zoom:80%;" />

## 4. Test vía Python

Como se ha comentado anteriormente, para la creación de gráficas se ha basado en el ejemplo **make_graph.py** del proyecto:

[docker-storage-benchmark](https://github.com/chriskuehl/docker-storage-benchmark)

Este proyecto esta basado en unos simples benchmark para comprobar la eficiencia de los diferentes Docker Storage Drivers, ademas de ficheros de diferentes tamaños incluye archivos tipo [binary tree](https://en.wikipedia.org/wiki/Binary_tree), es decir, una serie de ficheros en forma de árbol mediante directorios.

Este proyecto lleva sin actualizarse desde 2017.

Se han realizado una serie de cambios para hacerlo funcionar en el equipo de pruebas:

- Ubuntu 18.04 OS/Arch: linux/amd64
- Python 3.6
- Dokcer Version: 19.03.6

Las modificaciones son las siguientes:

- Modificado la _func running_containers_ para filtrar por el nombre del contenedor utilizado
- Mod. la _func. docker_storage_driver_ para obtener correctamente el campo Storage Driver
- Añadido nuevo volumen en el lanzamiento del contenedor ('-v', 'data_test:/test/myvolumen')
- Mod. el test _read-file-tree-mounted_ para realizar las pruebas sobre el volumen montado

Antes del lanzamiento:

1. Tener el volumen docker **data_test** creado.

2. Desde el terminal (host) en la ruta del volumen creado:

   ```
   /var/lib/docker/volumes/data_test/_data $:
   bash -c 'make_tree() { \
       local cur="$1"; local remaining_depth="$2"; \
       mkdir "$cur"; \
       if [ "$remaining_depth" -gt 0 ]; then \
           make_tree "${cur}/0" "$((remaining_depth - 1))"; \
           make_tree "${cur}/1" "$((remaining_depth - 1))"; \
       else \
           echo "oh, hi!" > "${cur}/oh-hi"; \
       fi; \
   }; \
   make_tree tree-of-files 14 \
   '
   ```

   Necesario para el funcionamiento del test: _read-file-tree-mounted.sh_

3. Crear la imagen a partir del Dockerfile de la carpeta /python

   ```
   $(pwd)/python$ docker build -t benchmark .
   ```

4. Por último lanzamos:

   ```
   $(pwd)/python$ python3 ./test.py
   ```

Se deberá de **lanzar por cada storage driver** establecido.

1. Cambiamos el storage driver:

   ```
   # nano /etc/docker/daemon.json
   {
     "storage-driver": "aufs"
   }
   # service docker restart
   ```

2. Creamos de nuevo la imagen benchmark

3. Lanzamos de nuevo el test
