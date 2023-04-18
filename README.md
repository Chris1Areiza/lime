<h1 align="center"> AB Challenge MeLi </h1>

## Índice

* [Diseño experimental e hipótesis](#Diseño-experimental-e-hipótesis)

* [Supuestos estadísticos](#Supuestos-estadísticos)

* [Consideraciones y tradeoffs](#Consideraciones-y-tradeoffs)

* [API para consulta](#API-para-consulta)

## Diseño experimental e hipótesis

Cuando tenemos experimentos con dos variantes se establecen pruebas de hipótesis de dos colas, esto con el fin de establecer si existen diferencias significativas entre las medias de las compras por variante. 

$H_0: μ_1=μ_2$

$H_1: μ_1≠μ_2$

Donde $μ_1$ y $μ_2$ representa la media poblacional de las compras por cada variante del experimento. Se establece un nivel de significancia de `0.05`.

Generalmente el grupo de control corresponde a la variante `DEFAULT` y el grupo de experimento a la otra variante que se quiere probar. Lo importante es que las mediciones se realizan en la misma ventana temporal, por ello la importancia del grupo de control, para evitar la interferencia de otros aspectos y que solo se evalúen los resultados por los cambios expuestos en cada variante.

Ahora, cuando los experimentos poseen tres o cuatro variantes se utiliza la prueba ANOVA mediante la cual se comparan las medias de compras de todas las variantes. El juego de hipótesis para la ANOVA es:

$H_0: μ_1=μ_2=...μ_n$

$H_1:$ Al menos dos medias poblacionales son diferentes.

Por su parte, el test de Tukey es una prueba post hoc comúnmente usada para evaluar la importancia de las diferencias entre pares de medias de grupo. El test le sigue a la ANOVA unidireccional, cuando la prueba F revela la existencia de una diferencia significativa entre algunos de los grupos. 

La hipótesis nula $H_0$ para la prueba establece que las medias de los grupos probados son iguales.


Generalmente se tiene una población y se escoge una muestra significativa para hacer más precisas las estimaciones, la escogencia de la muestra dependería de la potencia de la prueba, el nivel de significancia e incluso el tamaño del efecto. En este caso, dado que se entregó un subset y que los registros con entrada `BUY` en la columna `event_name` son pocos entonces no se escogió una muestra sobre el subset, se trabajó con toda la data pues en teoría ya corresponde a una muestra.

## Supuestos estadísticos

En algunos casos las variantes (grupos) tienen muy pocos datos por lo que utiliza la prueba-t que tiene una ventaja y es que nos sirve para realizar estimaciones con pocos datos y cuando el número de datos es lo suficientemente grande tiende a ser muy similar a la distribución normal. Se utiliza adempás la desviación muestral dado que no se conoce la desviación poblacional. Se asume que los datos son independientes, los datos de caga grupo fueron obtenidos mediante muestreo aleatorio simple, que los datos tienen distribución normal, los valores son continuos y las varianzas de los dos grupos inpendientes son iguales. Se hace necesario mencionar que cuando las muestras son pequeñas, probar los supuestos es complicado por lo que se asumen.

Por otra parte, para la ANOVA se asume que las varianzas poblacionales son iguales, es decir, homocedasticidad, lo que en la teoría se podría probar con un test de Levene, también se asume distribución normal (un test de Shapiro-Wilk podría ayudar a comprobanrlo o incluso un Q-Q Plot) para las poblaciones y se asume además que las muestras sobre las que se aplican los tratamientos son independientes. Para el test de Tukey se asumen los mismos supuestos que la ANOVA.


## Consideraciones y tradeoffs

Algunas consideraciones que se podrían hacer sería evaluar el comportamiento en diferentes ventanas temporales, es decir, en vez de evaluar el comportamiento por horas y tomarlo como un data point, evaluar que sucede con las compras en ventanas de dos horas, doce horas, hasta días, considerando un subset más grande y observando como sería el cambio en la significancia estadística de la diferencia de las medias entre los grupos o si por el contrario se mantiene consistente. La otra consideración es que si se quisiera ser más riguroso y aplicar las pruebas estadísticas para comprobar los supuestos se puede descartar una proporción de data, en caso de que no se cumplan los supuestos, o se tendría que considerar otro tipo de tratamientos. Esto desde el punto de vista estadístico.

Desde el punto de vista de ingeniería, se podría usar un cluster de Hadoop para procesar y analizar la data de una manera distribuida y paralela. También se podría llevaar la solucón a las nubes de Google (GCP) o Amazon (AWS) utilizando la arquitectura de referencia de MeLi. Pensando en automatización, herramientas como Airflow o Composer de GCP pueden servir para programar jobs que ejecuten pipelines de datos. Y ya para el consumo, si se requiere real time el procesamiento a usar puede ser stream o para análisis en lote, procesamiento en batch. 

Las anteriores consideraciones se hacen desde el punto de vista de la rigurosidad estadística y desde la escalabilidad de la solución para una mayor cantidad de datos.

En este punto quisiera mencionar que no se realizó un análisis exploratorio estándar como generalmente se hace con otro tipo de data donde se constribuyen plots de distribución de frecuencias y demás gráficos vistosos porque no se consideró necesario, más allá de los hallazgos que se plasmaron en el notebook.

## API para consulta

Como ya se mencionó, se dispuso la data en un txt en github con el fin de disponibilizarla para el consumo de la API. Se utiliza el servicio Azure Functions para hostear la API pues el servicio es útil para implementar y ejecutar funciones sin servidor como la de la API. Cada función de Azure Functions se convierte en un endpoint y se ejecuta respondiendo a los eventos que en este caso son solicitudes HTTP. El código se encuentra en el repositorio bajo el nombre `_init_.py`. Allí se define una función asíncrona de Azure Functions que se activa mediante una solicitud HTTP y va a devolver información sobre un experimento y un día específicos.  

Se define una función asíncrona llamada `main` que toma una solicitud HTTP, se define la URL que apunta al .txt, se obtienen los parámetros de `experiment_id` y `day` de la solicitud HTTP. Es necesario tener en cuenta que en este caso el `experiment_id` será el nombre del experimento ya que en el subset inicial la tupla solo tenía nombre del experimento y variante. Se lee el archivo con `requests`, se convierte en pandas, se filtra el dataframe para mostrar las filas que coinciden con los parámetros de la solicitud, si no se encuentra un resultado se devuelve un error 404 y si se encuentra un resultado, se crea un diccionario con la información del total de participantes, la variante ganadora de acuerdo con las pruebas , la lista de variantes con sus ids y la cantidad de compras en cada variante. Ese diccionario se convierte en JSON y devuelve la respuesta HTTP con el código 200. Si ocurre un error en la consulta, devuelve la respuesta HTTP con código 500.

Para esto se debe descarga una extensión de azure en visual code, crear una nueva función, se configura y por defecto crea la estructura, luego en el archivo `_init_.py` de la estructura se coloca el código de la API y se despliega para obtener la URL de la API que se dispone a continuación:

https://meliproject.azurewebsites.net/api/meliproject?experiment_id={vip/showV2V3BoxMessages&day=2021-08-02%2023

Solo se cambia el experiment_id y el day para obtener los resultados del experimento en ese día específico. El siguiente es un ejemplo de una consulta con la API:

![image](https://user-images.githubusercontent.com/65421047/232831007-91f6098b-b937-4336-8089-6aa327693ed9.png)

La URL pública estará activa siempre y cuando la function esté activa en Azure.




