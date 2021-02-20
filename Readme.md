# Serverless Computing

## Abstract

Ya han empezado a coger fuerza otras tendencias tecnológicas como el caso de serverless computing[[5]](#1). 

Hay que aclarar que el nombre *serverless computing* puede llevar a confusión, no significa computación sin necesidad de servidor, la parte "*less*" de serverless a la oportunidad que les brinda a los clientes de no tener que administrar el servidor que ejecutas sus aplicaciones. En este paradigma, se factura las tareas en función del uso real de recursos que precisa cada aplicación o tarea en específico. A grandes rasgos y enfocándose en su uso más básico, *serverless computing* proporciona la ventaja de simplificar el proceso de implementación de código en un escenario de producción. Por tanto, se abaratan los costes y se agiliza la implementación, siendo proveedor cloud el encargado de las tareas como el escalado de recursos en función de la demanda. 

En este documento se muestra el desarrollo de funciones AWS Lambda seguido de una visión global de las distintas funciones, junto a la representación gráfica tanto de la arquitectura basada en AWS Lambda como sus interacciones. 



## Objetivos

El objetivo principal de este trabajo es entender y aprender a utilizar AWS Lambda de un modo más minucioso, junto a los servicios implicados para ser llevado a cabo. AWS Lambda es de coste reducido, es por ello, que es importante sacarle el máximo partido y para ello, existen otros servicios que logran proporcionar mayores ventajas a esta tecnología. 

Para llevar a cabo este objetivo principal, se crean tres funciones lambda que ejecuta una determinada tarea. En este caso particular, una función es invocada ante la subida de un fichero en un bucket de S3 y guardado el resultado en otro bucket S3, una segunda función es llamada por la invocación por parte de la primera función lambda y, por último, la tercera función es invocada ante el evento generado por la primera función al subir su resultado a un Bucket S3.  

 

## Metodología

Para poder abordar el objetivo principal, han sido desarrolladas 3 funcione lambda con diferentes roles, donde debido al resultado o invocación por parte de una de las tres funciones, se activan las demás funciones lambda. 

Estas funciones, junto a toda implementación servicio necesario para su funcionamiento, es credo automáticamente mediante Python utilizando la librería boto3. Para el desarrollo de las funciones se ha hecho uso de Python3 junto a boto3[^1]para dos de ella, siendo la última función lambda desarrollada con Nodejs junto a aws-sdk. 

[^1]: SDK de Amazon Web Services (AWS) para Python, permitiendo en Python crear, configurar y administrar servicios de AWS

## Desarrollo

![](docs/diagrams/Deployment_lambda_functions.png)

Una función lambda se ejecutará cuando se suba un fichero con extensión `.md` al bucket de S3 **alucloud-lambda** en una carpeta (31 para este trabajo) y descargará el fichero del bucket, una vez descargado lo convertirá a un fichero HTML y posteriormente lo subirá **alucloud-lambda-out**. Finalmente invocará a otra función para que actualice la lista de resultado de las conversiones o tareas realizadas, ofreciendo el resultado por medio de una página web estática actualizada). 

A su vez, la subida de un fichero con extensión `.html` al bucket **alucloud-lambda-out** provocará la ejecución de una tercera función. Esta descargará el fichero HTML y filtrará todo el contenido para obtener solo el texto, generando como resultado un fichero con extensión `.txt` que es subido al **bucket alucloud-lambda-out.** 

### **Funciones lambda** 

Antes de proceder con cada función es necesario poner en contexto sobre el modelo que se sigue en la programación de las funciones lambda expuestas anteriormente y detalladas posteriormente. Es necesario recalcar los aspectos más relevantes que las tres funciones lambda comparten: 

- **Handler**: Función del código suministrado que el servicio AWS Lambda ejecuta cuando la función es invocada. El evento se pasa como primer parámetro y como segundo parámetro el *context*. 

- **Context**: Segundo parámetro de la función lambda, utilizada, por ejemplo, obtener información que AWS lambda facilita (tiempo restante antes que la función termines) o marcar la finalización de una función asíncrona mediante “*context.succeed(‘Mensaje de finalización’)*” (Utilizada en lenguajes como Nodejs). 

- **Logging**: Todo el mensaje mostrado por salida estándar ( e.g *print, console.log, system.out.print*) serán trasladados a CloudWatch Logs[^2], permitiendo ser consultados. 

  [^2]: Servicio CloudWatch Logs para monitorizar y almacenar archivos de registro, así como obtener acceso a ellos

- **Stateless**: No se asume que el sistema archivos será compartido entre las distintas invocaciones de la función lambda. Solo /tmp tiene permisos de escrituro, el resto es solo de lectura para todo el sistema de archivos. 

En este trabajo han sido desarrollados 3 funciones lambda que van a ser detalladas de una manera generalizada a continuación.

#### Función lambda maestra

Es denominada maestra puesto que será la encargada de realizar la primera acción, provocando a posteriores la invocación de las dos funciones restante, ya sea por llamada o por nuevo evento S3.  Esta función tiene como nombre en AWS lambda como **lambda-markdown-alucloud31**. 

A continuación, las características del código de la función:

##### Características

- Lenguaje Python 3.6
- Librería markdown convertir el fichero a html
- Librería boto3 para interactuar con los servicios de AWS (como S3).

##### Funcionalidad

Esta función es invocada cuando un fichero Markdown (.md) es subido al bucket alucloud-lambda y realiza los siguientes pasos:

1. Descarga el nuevo fichero subido
2. Lo convierte a formato HTML
3. Lo sube al bucket *alucloud-lambda-out*, generando una página web estática (importante especificar *Content-Type=text/html*)
4. Invoca a la función llamada **lambda-check-alucloud31** con información sobre el evento que invoco a la función, el nuevo fichero subido e información sobre la propia función (nombre, mensaje, resultado ...)
5. Obtiene el mensaje de respuesta de la función lambda invocada

El código de la implementación en el anexo sección A.1

Como resultado se obtiene un fichero html generado sobre un markdown:

#### Función lambda hija invocada

Esta función tiene como nombre en AWS lambda como **lambda-check-alucloud31**, es invocada por la anterior función denominada **lambda-markdown-alucloud31**. Entre ellos se realiza la siguiente interacción:

Esta función tiene otras características diferenciadoras del anterior:

##### Características

- Lenguaje Nodejs12.x
- Librería fs para tratar operaciones de Lectura/Escritura (Permite realizar dichas operaciones de forma síncrona)
- Librería aws-sdk para interactuar con los servicios de AWS (como S3).

Como podemos observar, entre las características diferenciadoras se encuentra el lenguaje utilizado. De esta manera, vemos la flexibilidad que AWS Lambda ofrece y en un futuro permite que este despliegue mediante funciones lambda no esté ligada a las limitaciones de un solo lenguaje.

##### Funcionalidad

Esta función es invocada por la función **lambda-markdown-alucloud31** y efectúa los siguientes pasos:

1. Obtiene el mensaje generado por la función invocadora

2. Comprueba todas las modificaciones realizadas sobre el bucket lambda-bucket-out en una carpeta especificada por el mensaje trasmitido
   
3. Realiza un HTML con la información que ha obtenido, generando una página web estática.

4. Sube el nuevo fichero al bucket alucloud-lambda-out (Especificando el tipo de contenido ‘*text/html*’).

El código de la implementación en el **anexo** sección A.2

Como resultado se obtiene un fichero HTML que actúa como una página web estática, permitiendo acceder a cada uno de los ficheros creados:

<img src="docs/imgs/static_web_page_results.png" style="zoom:80%;" />



#### Función lambda hija

Esta función tiene como nombre en AWS lambda como **lambda-html-alucloud31**, función invocada cuando es detectado como su nombre indica, es la encargada de tratar con ficheros con extensión `.html`. A continuación, las características del código de la función:

##### Características

- Lenguaje Python 3.6
- Librería html2text para convertir el fichero HTML a texto (Además filtra todos los patrones de un
  HTML)
- Librería boto3 para interactuar con los servicios de AWS (como S3).

##### Funcionalidad

Esta función es invocada cuando un fichero HTML es subido al bucket alucloud-lambda-out y como
consecuencia lleva a cabo los siguientes pasos:

1. Descargar el nuevo fichero subido al bucket *alucloud-lambda-out*
2. Realiza su lectura y posterior filtrado del texto.
3. El resultado lo sube al mismo bucket de nuevo manteniendo el nombre, pero con extensión .txt

El código de la implementación en el anexo sección A.3.

### Creación y Lanzamiento

En el siguiente apartado se muestra y explica cómo se ha llevado a cabo el despliegue, indicando los elementos o servicios necesarios, paso a seguir y aspectos a tener en cuenta. Además, se especifica como se ha llevado a cabo el despliegue automáticamente con ayuda de Python junto a la librería Boto3.

Para realizar el despliegue es necesario tener a disposición:

- Una cuenta de AWS, sus credenciales serán utilizadas para interactuar con AWS mediante Boto3
- Los buckets en S3 con los permisos necesarios ( *alucloud-lambda* y *alucloud-lambda-cloud* en este caso)
- Un rol con el que se ejecuta la función lambda, aportando los privilegios de acceso a las funciones lambda.

Partiendo de la base de los puntos anteriores, se procede al despliegue de las funciones lambda. Los siguientes pasos, cuentan de forma resumida la configuración seguida, para un detalle más preciso consultar el código bien comentado del **anexo** en el apartado B.

Todo ello ha sido realizado con el siguiente orden:

- Se comprueba si la primera función **lambda-markdown-alucloud31** existe, si no existe es creada-
- Ahora se añade una nueva política a la función para que permita ser invocado por un “*trigger*” del servicio S3 (Se debe especificar el **arn** del bucket alucloud-lambda en cuestión).
- Ahora es añadido el “*trigger*” para que sea ejecutado automática ante un evento “*PutObject*” del bucket *alucloud-lambda*.
- Es creado el "*trigger*" con el prefijo "31/" y el sufijo `.md`, antes de añadirlo se comprueba que nuestro disparador no existe.
- Es turno de añadir la función **lambda-html-alucloud31** si no existe.
- Añade una nueva política, para permitirla invocación mediante un "*trigger*" de S3, pero ahora indicado el bucket *alucloud- lambda -out*.
- Es creado el "*trigger*" con el prefijo "31/" y sufijo `.html`, especificando el bucket *alucloud-lambda-out*
- Por último, la función **lambda-markdown-alucloud31** es creada, siguiendo los mismos puntos de la función anterior, pero sin añadir el "*trigger*" para eventos de S3 (*putObject*).
- Para finalizar, solo se debe permitir que esta función sea invocada por otra función, se añade una nueva política (*add new policy*) para permitir a esta nueva función ser invocada por la función **lambda-markdown-alucloud31** (se debe especificar el **arn** de la función lambda invocadora)



####  Implementación automática mediante script

Para llevar el despliegue automático de los puntos anteriores, se ha generado una serie de scripts en Python utilizando la librería boto 3. En concreto se han creado dos ficheros Python, siendo una de las encargadas de proporciona la configuración adecuada y otra las funciones para realizar cada uno de los pasos. 

A continuación, en el siguiente diagrama de clases se visualiza la estructura y metodología utilizada:

<img src="docs/imgs/uml_classes.png" style="zoom:80%;" />

Como muestra el diagrama existen tres clases:

- **setupDeployment** creada en el fichero `init-deployment.py` (Anexo B.1)
- **SettingsAlucloud31** localizada en el fichero `studentSettings.py` (Anexo B.2)
- **LambdaManager** localizada en el fichero `studentSettings.py` (Anexo B.2)

**SettingsAlucloud31**, contiene la configuración con todos los nombres de los servicios o elementos implicados, así como la sesión de nuestra cuenta de AWS y la configuración de cada función lambda en formato YAML.

```yaml
self.configParent=yaml.load("""
            role: myrole
            name: lambda-markdown-alucloud31
            zip: lambda-markdown-alucloud31.zip
            path: parent-lambda-code
            handler: MarkdownConverter.handler
            runtime: python3.6
            description: Convert mardownk documents to html
            suffix: .md
            statementid: '1-lambda'
            bucket: {}
            arn_bucket: arn:aws:s3:::alucloud-lambda
            """.format(self.Bucket), 
            Loader=yaml.FullLoader)
            
 self.configChild=yaml.load("""
            ......
            """.format(self.BucketOut), 
            Loader=yaml.FullLoader)

 self.configChildNode=yaml.load("""
           ......
            """.format(self.BucketOut), 
            Loader=yaml.FullLoader)
```


**LambdaManager**, encargada de proporcionar una serie de funcionalidades para realizar el despliegue. Se instancia, pasándole como parámetro la instancia de la clase anterior (*SettingsAlucloud31*), junto a la configuración lambda que deseamos. A continuación un fragmente de código para ejemplificar:

```python
self.lambdaManagerParent=studentSettings.lambdaManager(self.alucloud31,self.alucloud31.configParent)

#Child is invoked when Parent putObject type .html tu Bucket S3
self.lambdaManagerChild=studentSettings.lambdaManager(self.alucloud31,self.alucloud31.configChild)

#Node Child is invoked by parent when he finish the task
self.lambdaManagerNodeChild=studentSettings.lambdaManager(self.alucloud31,self.alucloud31.configChildNode)
```

Por cada función se instancia una nueva clase **LambdaManager** permitiendo facilitar la gestión individual de cada función.

**setupDeployment**, es la clase encargada de iniciar el despliegue utilizando la clase *LambdaManager*para tratar cada función y *SettingsAlucloud31* para establecer la configuración deseada. A continuación se muestra como ejemplo, como lanzar o inicializar el despliegue:

```sh
$ init-deployment.py --Init
```
Si ha tenido exito la inicialzación, es motrado la siguigente salida.
```c#
[SUCCES] QUEUE sqs-alucloud31 exist
[SUCCES] RULE alucloud-events-rule-s3-to-sqs-31 exist
[SUCCES] FOLDER (31/) on BUCKET (alucloud-lambda)
[SUCCES] FUNCTION LAMBDA(lambda-markdown-alucloud31) exist
[SUCCES] TRIGGER ON BUCKET(alucloud-lambda) exist
[INFO] CHECK OUR TRIGGER ON BUCKET(alucloud-lambda-out) exist
[SUCCES] TRIGGER ON BUCKET(alucloud-lambda) exist
[SUCCES] FUNCTION LAMBDA(lambda-html-alucloud31) exist
[INFO] TRIGGER ON BUCKET(alucloud-lambda-out) exist
[INFO] CHECK OUR TRIGGER ON BUCKET(alucloud-lambda-out) exist
[SUCCES] TRIGGER ON BUCKET(alucloud-lambda) exist
[SUCCES] FUNCTION LAMBDA(lambda-html-alucloud31) exist
```

Además, existen otros parámetros para en un futuro poder ser escalado, por ejemplo, esta implementado la visualización de los registros generados por cada una de las funciones en las últimas 24 horas. Para obtener los parámetros disponibles:
```sh
$ init-deployment.py -h

usage: init-deployment.py [-h] [-i INIT] [-l]

optional arguments:
  -h, --help            show this help message and exit
  -i INIT, --Init INIT  Launch the developed setup
  -l, --Logs            Display the logs of each lambda function deployed.
```
### Resultados obtenidos

A continuación, se muestran imágenes de AWS Management Console[[4]](#1), estas son el resultado del despliegue obtenido:

**Funciones Lambda desplegadas:**

![](docs/imgs/lambda_markdown_with_trigger.png)

![](/home/manu/Documents/MASTER/ICP/Trabajo-Final/Trabajo/docs/imgs/lambda_check_withouth_trigger.png)

![](/home/manu/Documents/MASTER/ICP/Trabajo-Final/Trabajo/docs/imgs/lambda_html_with_trigger.png)

### Pruebas

En este apartado, se elaboran una serie de pruebas para comprobar el correcto funcionamiento del despliegue. Para ello, se siguen una serie de pasos para verificar su adecuado funcionamiento.

##### Invocación de la función lambda lambda-markdown-alucloud31

```sh
aws lambda invoke \
--invocation-type Event \
--function-name lambda-markdown-alucloud31 \
--region us-east-1 \
--payload file://${PWD}/test_deployment_parent.json \
outputfile.txt
#Successful output: 202
```

Registros generados por la invocación:

```sh
LOG_GROUP=/aws/lambda/lambda-markdown-alucloud31
aws logs get-log-events --log-group-name $LOG_GROUP --log-stream-name `aws logs describe-log-streams --log-group-name $LOG_GROUP --max-items 1 --order-by LastEventTime --descending --query logStreams[].logStreamName --output text | head -n 1` --query events[].message --output text

## Succellfull output
START RequestId: e869dd5f-cc13-437e-b2fd-ca6602e67530 Version: $LATEST
[1] Downloading markdown in bucket alucloud-lambda with key 31/Readme.md
[2] Uploading html in bucket alucloud-lambda-out with key 31/Readme.html
[3] Changing ACLs for public-read for object in bucket alucloud-lambda-out with key 31/Readme.html
[4] Invoke the lambda function lambda-check-alucloud31
Check and Summary HTML Created: File $31/ListOfResult.html with url: https://alucloud-lambda-out.s3.amazonaws.com/31/ListOfResult.html
END RequestId: e869dd5f-cc13-437e-b2fd-ca6602e67530
REPORT RequestId: e869dd5f-cc13-437e-b2fd-ca6602e67530	Duration: 4145.55 ms	Billed Duration: 4146 ms	Memory Size: 128 MB	Max Memory Used: 84 MB	Init Duration: 509.80 ms
```

Aquí se muestra como por comandos podemos realizar la invocación de un evento, utilizado una plantilla de evento creada. Se ha creado una plantilla distinta para cada evento creado.

Estas plantillas pueden ser lanzadas además, desde AWS Management Console, como se muestra en la siguiente imagen: 

<img src="docs/imgs/4_functions_lambda_deploy_test.png" style="zoom:80%;" />

Obteniendo como resultado de la ejecución:

![](docs/imgs/execution_result_markdown.png)


##### Subida de un fichero a S3 y visualización del evento generado

```sh
aws s3 cp ${PWD}/example-data/cuda.md s3://alucloud-lambda/$ID/cudatest.md
# Successful output: 
#   upload: example-data/cuda.md to s3://alucloud-lambda-out/31/cudatest.md
```

Ahora es listado el fichero en el nuevo bucket:

```sh
aws s3 ls s3://alucloud-lambda-out/$ID/  | grep --color=always 'cuda'
#Successful output:
#   2021-02-17 21:10:22      13197 cudatest.md
```

Por último, esta nueva subida a provocado la la invocación de la función lambda **lambda-markdown-alucloud31**, ahora se procede a visualizar los últimos registros (*logs*) de dicha función.

```sh
LOG_GROUP=/aws/lambda/lambda-markdown-alucloud31
aws logs get-log-events --log-group-name $LOG_GROUP --log-stream-name `aws logs describe-log-streams --log-group-name $LOG_GROUP --max-items 1 --order-by LastEventTime --descending --query logStreams[].logStreamName --output text | head -n 1` --query events[].message --output text

## Succellfull output
START RequestId: e869dd5f-cc13-437e-b2fd-ca6602e67530 Version: $LATEST
[1] Downloading markdown in bucket alucloud-lambda with key 31/cudatest.md
[2] Uploading html in bucket alucloud-lambda-out with key 31/cudatest.html
[3] Changing ACLs for public-read for object in bucket alucloud-lambda-out with key 31/cudatest.html
[4] Invoke the lambda function lambda-check-alucloud31
Check and Summary HTML Created: File $31/ListOfResult.html with url: https://alucloud-lambda-out.s3.amazonaws.com/31/ListOfResult.html
END RequestId: e869dd5f-cc13-437e-b2fd-ca6602e67530
REPORT RequestId: e869dd5f-cc13-437e-b2fd-ca6602e67530	Duration: 4145.55 ms	Billed Duration: 4146 ms	Memory Size: 128 MB	Max Memory Used: 84 MB	Init Duration: 509.80 ms
```

También puede ser visualizado directamente desde AWS Management Console en la siguiente dirección, CloudWatch Logs > Log groups > /aws/lambda/lambda-markdown-alucloud-31.:

![](docs/imgs/cloudwatch_events_of_lambda_markdown.png)

Si son observados detalladamente los logs,  la función **lambda-check-alucloud31** ha funcionado satisfactoriamente, ya que ha contestado a la invocación de la función testeada. A continuación la linea que representa la contestación de la función **lambda-check-alucloud31**.

```sh
Check and Summary HTML Created: File $31/ListOfResult.html with url: https://alucloud-lambda-out.s3.amazonaws.com/31/ListOfResult.html
```

##### Invocación de la función lambda lambda-html-alucloud31

```sh
aws lambda invoke \
--invocation-type Event \
--function-name lambda-html-alucloud31 \
--region us-east-1 \
--payload file://${PWD}/test_deployment_child.json \
outputfile.txt
#Successful output: 202
```
Una vez a tenido éxito el lanzamiento del evento, es turno de visualizar los últimos registros de la función.

```sh
LOG_GROUP=/aws/lambda/lambda-html-alucloud31
aws logs get-log-events --log-group-name $LOG_GROUP --log-stream-name `aws logs describe-log-streams --log-group-name $LOG_GROUP --max-items 1 --order-by LastEventTime --descending --query logStreams[].logStreamName --output text | head -n 1` --query events[].message --output text
## Succellfull output
START RequestId: 1029f3e5-3848-44c8-9316-64fa973ca0c2 Version: $LATEST
	[1] Downloading markdown in bucket alucloud-lambda-out with key 31/Readme.html
	[2] Uploading html in bucket alucloud-lambda-out with key 31/Readme.txt
	[3] Changing ACLs for public-read for object in bucket alucloud-lambda-out with key 31/Readme.txt
	END RequestId: 1029f3e5-3848-44c8-9316-64fa973ca0c2
	REPORT RequestId: 1029f3e5-3848-44c8-9316-64fa973ca0c2	Duration: 1462.16 ms	Billed Duration: 1463 ms	Memory Size: 128 MB	Max Memory Used: 78 MB	Init Duration: 477.93 ms	
```

Para finalizar las pruebas y confirmar su correcto funcionamiento, es mostrado el resultado con imagenes de la interfaz de AWS Management Console:

<img src="docs/imgs/result_s3.png" style="zoom:80%;" />

## Futuras Mejoras

La intención inicial era poder convertir un fichero ".doc" a PDF con Python, pero debido a que es necesario trabajar con Windows no ha podido ser posible. Además, las librerías existentes para convertir otros tipos de documentos a PDF utilizan otras "*sub-librerías*", como consecuencia a la hora de comprimir el código para ser enviado a AWS, siempre existe algún error debido a que una librería no es detectada. Por tanto, para este trabajo has sido utilizadas librerías más ligueras con menos dependencias, permitiendo de ese modo, la posibilidad de probar y modificar la función desde la propia plataforma de AWS Management Console. 

Para un futuro, es posible tratar cada una de las dependencias o elegir otro lenguaje, como NodeJs que es utilizado en entre trabajo.



## References
<a id="1">[1]</a> 
[Microsoft azure](https://docs.microsoft.com/en-us/azure/?product=featured)
Microsoft Azure: Cloud Computing Services

<a id="1">[2]</a> 
[Google Cloud](https://cloud.google.com)
Servicio en la nube de Google

<a id="1">[3]</a> 
[IBM Cloud Functions](https://cloud.ibm.com/functions/)
Plataforma de función como servicio (FaaS) basada en Apache OpenWhisk

<a id="1">[4]</a> 
[AWS Management Console](https://aws.amazon.com/es/console/)
Consola de administración de AWS

<a id="1">[5]</a> 
[Serverless Computing](https://www.ibm.com/cloud/learn/serverless)
What is serverless computing?
