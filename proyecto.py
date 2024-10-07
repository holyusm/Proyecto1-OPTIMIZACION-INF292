import numpy as np
import random

# GENERACION DE PARAMETROS
I = range(25)  # Conjunto de asignaturas (DEPENDE DEL TAMANIO DE LA INSTANCIA)
S = range(1)  # Conjunto de salas
T = range(7)  # Bloques horarios disponibles por dia
D = range(5)  # Dias de la semana, de lunes a viernes

C_s = {s: np.random.randint(20, 46) for s in S}  # Capacidad de salas aleatoria (20 a 45) (A=1)
E_i = {i: np.random.randint(10, 41) for i in I}  # Estudiantes interesados (10 a 40) (A=1)
A_i = {i: np.random.choice([0, 1], p=[0.8, 0.2]) for i in I}  # Asignatura indispensable (80% no, 20% si)
P_i = {i: np.random.randint(6, 11) if A_i[i] == 1 else np.random.randint(1, 6) for i in I} #6-10 indispensable, 1-5 dispensable
R_i = {i: np.random.choice([1, 2], p=[0.65, 0.35]) for i in I}  # i Requiere 1 o 2 bloques? (65% 1 bloque, 35% 2 bloques)(B=1)

# Bloques bloqueados para profesores
B_itd = {}
for i in I:
    # Numero de bloques bloqueados que va a tener profesor de asignatura i
    num_bloques_bloqueados = np.random.randint(7, 22)
    
    # En un inicio todos los bloques estan disponibles
    for t in T:
        for d in D:
            B_itd[(i, t, d)] = 0
    
    # Combinaciones bloques-dia
    combinaciones_t_d = [(t, d) for t in T for d in D]
    
    # Seleccionamos aleatoriamente las combinaciones bloque-dia bloqueadas
    bloques_bloqueados = random.sample(combinaciones_t_d, num_bloques_bloqueados)
    
    # Asignamos los bloques bloqueados (B_itd = 1)
    for (t, d) in bloques_bloqueados:
        B_itd[(i, t, d)] = 1

# Variables de decisión: si la asignatura i está asignada a la sala s, bloque t, día d
variables = {(i, s, t, d): f'X_{i}_{s}_{t}_{d}' for i in I for s in S for t in T for d in D}

# Funcion objetivo
def generar_funcion_objetivo(variables, prioridades):
    funcion_objetivo = "max: "
    for i in I:
        for s in S:
            for t in T:
                for d in D:
                    funcion_objetivo += f"{prioridades[i]} * {variables[(i, s, t, d)]} + "
    return funcion_objetivo.rstrip(" + ") + ";\n"

# Restriccion 1: Evitar solapamientos en las salas
def generar_restricciones_solapamientos(variables):
    restricciones = ""
    for s in S:
        for t in T:
            for d in D:
                restriccion = " + ".join([variables[(i, s, t, d)] for i in I])
                restricciones += f"{restriccion} <= 1;\n"
    return restricciones

# Restriccion 2: Asignacion de bloques requeridos por asignatura
def generar_restricciones_asignacion_bloques(variables, requerimientos):
    restricciones = ""
    for i in I:
        restriccion = ""
        for s in S:
            for t in T:
                for d in D:
                    restriccion += f"{variables[(i, s, t, d)]} + "
        restricciones += f"{restriccion.rstrip(' + ')} = {requerimientos[i]};\n"
    return restricciones

# Restriccion 3: Capacidad de la sala
def generar_restricciones_capacidad(variables, E_i, C_s):
    restricciones = ""
    for i in I:
        for s in S:
            for t in T:
                for d in D:
                    restricciones += f"{E_i[i]} * {variables[(i, s, t, d)]} <= {C_s[s]};\n"
    return restricciones

# Restriccion 4: Asignaturas indispensables deben asignarse
def generar_restricciones_indispensables(variables, A_i):
    restricciones = ""
    for i in I:
        if A_i[i] == 1:  # Si la asignatura es indispensable
            restriccion = " + ".join([variables[(i, s, t, d)] for s in S for t in T for d in D])
            restricciones += f"{restriccion} >= 1;\n" # La asignatura i debe estar asignada almenos 1 vez
    return restricciones

# Restriccion 5: Bloques bloqueados para los profesores
def generar_restricciones_bloques_bloqueados(variables, B_itd):
    restricciones = ""
    for i in I:
        for s in S:
            for t in T:
                for d in D:
                    if B_itd[(i, t, d)] == 1:   #Si B_itd == 1 => X_istd <= 0, es decir X_istd = 0
                        restricciones += f"{variables[(i, s, t, d)]} = 0;\n"
    return restricciones

# Restriccion 6: Bloques consecutivos (ERROR)
def generar_restricciones_bloques_consecutivos(variables, R_i):
    restricciones = ""
    for i in I:
        if R_i[i] == 2:  # Si la asignatura requiere 2 bloques consecutivos
            for s in S:
                for d in D:  # Aseguramos que se apliquen solo dentro del mismo dia
                    for t in range(len(T) - 1):  # Hasta el penultimo bloque (t)
                        # Si se asigna al bloque t, también debe estar en el bloque t+1
                        restricciones += f"{variables[(i, s, t, d)]} - {variables[(i, s, t+1, d)]} = 0;\n"
    return restricciones

# Restriccion 7: Exclusion del ultimo bloque del dia para asignaturas que requieren 2 bloques
def generar_restricciones_exclusion_ultimo_bloque(variables, R_i):
    restricciones = ""
    for i in I:
        if R_i[i] == 2:  # Si la asignatura requiere 2 bloques consecutivos
            for s in S:
                for d in D:
                    # Bloquear la asignación del ultimo bloque del día
                    restricciones += f"{variables[(i, s, len(T)-1, d)]} = 0;\n"
    return restricciones

# Declaracion de variables binarias
def declarar_variables_binarias(variables):
    binarios = "bin "
    binarios += ", ".join(variables.values()) + ";\n"
    return binarios

# Generación de la función objetivo
objetivo = generar_funcion_objetivo(variables, P_i)

# Generacion de restricciones
restricciones_solapamientos = generar_restricciones_solapamientos(variables)
restricciones_asignacion = generar_restricciones_asignacion_bloques(variables, R_i)
restricciones_capacidad = generar_restricciones_capacidad(variables, E_i, C_s)
restricciones_indispensables = generar_restricciones_indispensables(variables, A_i)
restricciones_bloques_bloqueados = generar_restricciones_bloques_bloqueados(variables, B_itd)
restricciones_bloques_consecutivos = generar_restricciones_bloques_consecutivos(variables, R_i)
restricciones_exclusion_ultimo_bloque = generar_restricciones_exclusion_ultimo_bloque(variables, R_i) 

# Declaracion de las variables binarias
declaracion_binarias = declarar_variables_binarias(variables)

# Generacion del modelo completo en formato lp_solve
modelo_lp_solve = (objetivo + "/* Restricciones: */\n" +restricciones_solapamientos + 
                   restricciones_asignacion + restricciones_capacidad + 
                   restricciones_indispensables + restricciones_bloques_bloqueados + 
                   restricciones_exclusion_ultimo_bloque + declaracion_binarias)

# Escribir el modelo en un archivo .lp
with open('proyecto.lp', 'w') as file:
    file.write(modelo_lp_solve)

print("El archivo 'proyecto.lp' ha sido generado correctamente.")
