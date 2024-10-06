import numpy as np

# GENERACION DE PARAMETROS
I = range(2)  # Conjunto de asignaturas (DEPENDE DEL TAMANIO DE LA INSTANCIA)
S = range(3)  # Conjunto de salas
T = range(3)  # bloques horarios disponibles por dia
D = range(1)  # Dias de la semana, de lunes a viernes

# Capacidades
C_s = {}
for s in S:
    capacidad = np.random.randint(20, 46)  # Capacidades aleatorias entre 20 y 45
    C_s[s] = capacidad  # la sala s tendra capacidad "capacidad"

# Estudiantes interesados
E_i = {}
for i in I:
    estudiantes = np.random.randint(10, 41)  # cant estudiantes aleatoria entre 10 y 40
    E_i[i] = estudiantes  # la asignatura i tendra una cantidad "estudiantes"

# Asignaturas indispensables
A_i = {}
for i in I:
    # 20% de prob de que la asignatura i sea indispensable
    # 80%                   =                dispensable
    A_i[i] = np.random.choice([0, 1], p=[0.8, 0.2])

# Prioridades
P_i = {}
for i in I:
    if A_i[i] == 1:
        # Si la asignatura es indispensable, la prioridad se asigna entre 6 y 10
        P_i[i] = np.random.randint(6, 11)
    else:
        # Si la asignatura no es indispensable, la prioridad se asigna entre 1 y 5
        P_i[i] = np.random.randint(1, 6)


# Bloques bloqueados por el horario del profesor
B_itd = {}
for i in I:
    num_bloques_bloqueados = np.random.randint(7, 22) # un profesor tiene bloqueado entre 7 a 21 bloques semanalmente
    
    # Combinaciones t_d
    combinaciones_t_d = []
    for t in T:
        for d in D:
            combinaciones_t_d.append((t, d))
    
    # Se seleccionan aleatoriamente las combinaciones t_d bloqueadas que tendra el profesor de la asignatura i
    bloques_bloqueados = np.random.choice(len(combinaciones_t_d), num_bloques_bloqueados, replace=False)
    
    # Se inicializan todos los bloques como disponibles
    for t in T:
        for d in D:
            B_itd[(i, t, d)] = 0
    
    # Se asignan como bloqueados los escogidos aleatoriamente
    for indice in bloques_bloqueados:
        t, d = combinaciones_t_d[indice]
        B_itd[(i, t, d)] = 1


# La asignatura i necesita 1 o 2 bloques semanalmente?
R_i = {}
for i in I:
    # Nuestro grupo es B = 1
    # 65% de prob de que una asignatura tenga 1 bloque a la semana
    # 35% de prob             =               2         =    
    R_i[i] = np.random.choice([1, 2], p=[0.65, 0.35])

# Variable de decision X_i_s_t_d
variables = {}
for i in I:
    for s in S:
        for t in T:
            for d in D:
                variables[(i, s, t, d)] = f'X_{i}_{s}_{t}_{d}'

# Funcion objetivo
def generar_funcion_objetivo(variables, prioridades):
    funcion_objetivo = ""
    for i in I:
        for s in S:
            for t in T:
                for d in D:
                    funcion_objetivo += f" + {prioridades[i]} * {variables[(i, s, t, d)]}"
    return "Maximize\n" + funcion_objetivo

objetivo = generar_funcion_objetivo(variables, P_i)
print(objetivo)
