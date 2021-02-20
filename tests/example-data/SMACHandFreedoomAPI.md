# SMACH and Freedoom API





## Ejemplo

Con el ejemplo, lo que quiero simular es poder realizar un simple autómata, que:

- Detecte que hay robot activo y conectado
- Si esta conectado, que se mueve y para 3 veces. Es decir, hacer parones.
- Si no esta conectado, pasar directamente a un estado final.



### Gráfico:

![](/home/manu/Downloads/SMACH EJEMPLO.png)



### Lanzamiento:

En una ventana de terminal: `roscore` 

Lanzar : `python smach-test.py`  

Output:

```python
[ DEBUG ] : Adding state (WAIT, <__main__.WaitRobot object at 0x7f98a53195d0>, {'outcomeNoRobots': 'outcomeSINACCION', 'outcome3': 'ACCION'})
[ DEBUG ] : Adding state 'WAIT' to the state machine.
[ DEBUG ] : State 'WAIT' is missing transitions: {}
[ DEBUG ] : TRANSITIONS FOR WAIT: {'outcomeNoRobots': 'outcomeSINACCION', 'outcome3': 'ACCION'}
[ DEBUG ] : Adding state (MOVER, <__main__.Mover object at 0x7f98a5330c50>, {'outcome1': 'PARA', 'outcome2': 'outcomeSalir'})
[ DEBUG ] : Adding state 'MOVER' to the state machine.
[ DEBUG ] : State 'MOVER' is missing transitions: {}
[ DEBUG ] : TRANSITIONS FOR MOVER: {'outcome1': 'PARA', 'outcome2': 'outcomeSalir'}
[ DEBUG ] : Adding state (PARA, <__main__.Parar object at 0x7f98a5330d50>, {'outcome1': 'MOVER'})
[ DEBUG ] : Adding state 'PARA' to the state machine.
[ DEBUG ] : State 'PARA' is missing transitions: {}
[ DEBUG ] : TRANSITIONS FOR PARA: {'outcome1': 'MOVER'}
[ DEBUG ] : Adding state (ACCION, <smach.state_machine.StateMachine object at 0x7f98a994a750>, {'outcomeSalir': 'outcomeMOVIDO'})
[ DEBUG ] : Adding state 'ACCION' to the state machine.
[ DEBUG ] : State 'ACCION' is missing transitions: {}
[ DEBUG ] : TRANSITIONS FOR ACCION: {'outcomeSalir': 'outcomeMOVIDO'}
[  INFO ] : State machine starting in initial state 'WAIT' with userdata: 
        []
{u'PC Edu': u'D68F72DA6493FFFAFC019BC0976', u'SUMMIT': u'DBC2E519193B30D58920BDF5A4B', u'RB1_UR3': u'DAAE57251443090874861EDB530'}
[INFO] [1610322166.793632]: Executing state WaitRobot
[  INFO ] : State machine transitioning 'WAIT':'outcome3'-->'ACCION'
[  INFO ] : State machine starting in initial state 'MOVER' with userdata: 
        ['sm_counter']
[INFO] [1610322166.795235]: Executing state mover
[  INFO ] : State machine transitioning 'MOVER':'outcome1'-->'PARA'
[INFO] [1610322166.797487]: Executing state parar
[INFO] [1610322166.798930]: Counter = 1.000000
[  INFO ] : State machine transitioning 'PARA':'outcome1'-->'MOVER'
[INFO] [1610322166.800458]: Executing state mover
[  INFO ] : State machine transitioning 'MOVER':'outcome1'-->'PARA'
[INFO] [1610322166.801833]: Executing state parar
```



## Trabajar mas comodo

Para visualizar mejor los jsons grandes de la Api Freedom robots. Aquí un fragmento de código de la clase Fleet.py, de como imprimir un json por terminal correctamente en python (sin caracteres especiales y bien formado )

```

       # Manu
       #1. Hacer print correctamente de un objeto json
           # print(json.dumps(devices[1],indent = 1))
      #2. Visualizador http://jsonviewer.stack.hu
       # Returns only name and Id, but more data is available
```

### Visualizador json

**Copiar json**

![](/home/manu/Downloads/Opera Instantánea_2021-01-10_225852_jsonviewer.stack.hu.png)

**Visualizarlo mejor**

![](/home/manu/Downloads/Opera Instantánea_2021-01-10_225827_jsonviewer.stack.hu.png)