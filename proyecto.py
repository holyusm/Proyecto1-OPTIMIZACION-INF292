import numpy as np
import random

# GENERACION DE PARAMETROS
I = range(30)  # Conjunto de asignaturas (DEPENDE DEL TAMANIO DE LA INSTANCIA)
S = range(15)  # Conjunto de salas
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

# Variables de decisión:
# x_{i,s,t,d}: 1 si la asignatura i se asigna a la sala s en el bloque t del día d, 0 en caso contrario
# y_i: 1 si la asignatura i es asignada, 0 en caso contrario
variables_x = {(i, s, t, d): f'X_{i}_{s}_{t}_{d}' for i in I for s in S for t in T for d in D}
variables_y = {i: f'Y{i}' for i in I}  # Nueva variable binaria para cada asignatura

# Funcion objetivo
def generar_funcion_objetivo(variables_y, prioridades):
    funcion_objetivo = "max: "
    for i in I:
        funcion_objetivo += f"{prioridades[i]} * {variables_y[i]} + "
    return funcion_objetivo.rstrip(" + ") + ";\n"


# Restriccion 1: Evitar solapamientos en las salas
def generar_restricciones_solapamientos(variables):
    restricciones = ""
    for s in S:
        for t in T:
            for d in D:
                restriccion = ""
                for i in I:
                    restriccion += f"{variables[(i, s, t, d)]} + "
                restriccion = restriccion.rstrip(" + ")  # Quita el último " + "
                restricciones += f"{restriccion} <= 1;\n"
    return restricciones

# Restriccion 2: Bloques consecutivos para asignaturas que requieren 2 bloques
def generar_restricciones_bloques_consecutivos(variables_x, variables_y, R_i):
    restricciones = ""
    for i in I:
        if R_i[i] == 2:  
            for s in S:
                for d in D: 
                    for t in range(len(T) - 1):  # Hasta el penúltimo bloque
                        restricciones += f"{variables_x[(i, s, t, d)]} - {variables_x[(i, s, t+1, d)]} <= {variables_y[i]};\n"
    return restricciones

# Restriccion 3: Asignación consecutiva en el penúltimo y último bloque del día
def generar_restricciones_exclusion_ultimo_bloque(variables_x, variables_y, R_i):
    restricciones = ""
    for i in I:
        if R_i[i] == 2:  # Si la asignatura requiere 2 bloques consecutivos
            for s in S:
                for d in D:
                    # Primera desigualdad: El último bloque solo puede estar asignado si el penúltimo también lo está
                    restricciones += f"{variables_x[(i, s, len(T)-1, d)]} <= {variables_x[(i, s, len(T)-2, d)]};\n"
                    # Segunda desigualdad: El último bloque solo puede estar asignado si la asignatura está asignada
                    restricciones += f"{variables_x[(i, s, len(T)-1, d)]} <= {variables_y[i]};\n"
                    # Tercera desigualdad: El penúltimo bloque solo puede estar asignado si la asignatura está asignada
                    restricciones += f"{variables_x[(i, s, len(T)-2, d)]} <= {variables_y[i]};\n"
    return restricciones


# Restriccion 4: Capacidad de la sala
def generar_restricciones_capacidad(variables, E_i, C_s):
    restricciones = ""
    for i in I:
        for s in S:
            for t in T:
                for d in D:
                    restricciones += f"{E_i[i]} * {variables[(i, s, t, d)]} <= {C_s[s]};\n"
    return restricciones

# Restriccion 5: Asignación Exacta de Bloques
def generar_restricciones_asignacion_exacta(variables_x, variables_y, R_i):
    restricciones = ""
    for i in I:
        restriccion = ""
        for s in S:
            for t in T:
                for d in D:
                    restriccion += f"{variables_x[(i, s, t, d)]} + "
        # Remover el último " + " para agregar la igualdad
        restriccion = restriccion.rstrip(" + ")
        # Aplicar la igualdad en función de y_i y R_i
        restricciones += f"{restriccion} = {R_i[i]} * {variables_y[i]};\n"
    return restricciones

# Restriccion 6: Prioridad de Asignación según Importancia
def generar_restricciones_prioridad_asignacion(variables_y, A_i):
    restricciones = ""
    for i in I:
        restricciones += f"{variables_y[i]} >= {A_i[i]};\n"
    return restricciones

# Restriccion 7: Restricciones de horario de los profesores
def generar_restricciones_horario_profesores(variables_x, B_itd):
    restricciones = ""
    for i in I:
        for s in S:
            for t in T:
                for d in D:
                    # Si el bloque está bloqueado (B_itd = 1), x_istd <= 0, lo que impide la asignación
                    restricciones += f"{variables_x[(i, s, t, d)]} <= {1 - B_itd[(i, t, d)]};\n"
    return restricciones

def declarar_variables_binarias(variables_x, variables_y):
    binarios = "bin "
    binarios += ", ".join(variables_x.values()) + ", " + ", ".join(variables_y.values()) + ";\n"
    return binarios

# Generación de la función objetivo
objetivo = generar_funcion_objetivo(variables_y, P_i)

# Generacion de restricciones
restricciones_solapamientos = generar_restricciones_solapamientos(variables_x)  # Restricción 1
restricciones_bloques_consecutivos = generar_restricciones_bloques_consecutivos(variables_x, variables_y, R_i)  # Restricción 2
restricciones_exclusion_ultimo_bloque = generar_restricciones_exclusion_ultimo_bloque(variables_x, variables_y, R_i)  # Restricción 3
restricciones_capacidad = generar_restricciones_capacidad(variables_x, E_i, C_s)  # Restricción 4
restricciones_asignacion_exacta = generar_restricciones_asignacion_exacta(variables_x, variables_y, R_i)  # Restricción 5
restricciones_prioridad_asignacion = generar_restricciones_prioridad_asignacion(variables_y, A_i)  # Restricción 6
restricciones_horario_profesores = generar_restricciones_horario_profesores(variables_x, B_itd)  # Restricción 7

# Declaracion de las variables binarias
declaracion_binarias = declarar_variables_binarias(variables_x, variables_y)

# Generación del modelo completo en formato lp_solve
modelo_lp_solve = (objetivo + "/* Restricciones: */\n" +
                   "/* SOLAPAMIENTOS: */\n" +
                   restricciones_solapamientos + 
                   "/* BLOQUES CONSECUTIVOS: */\n" +
                   restricciones_bloques_consecutivos +
                   "/* EXCLUSION ULTIMO BLOQUE: */\n" +
                   restricciones_exclusion_ultimo_bloque +
                   "/* CAPACIDAD: */\n" +
                   restricciones_capacidad +
                   "/* ASIGNACION EXACTA: */\n" +
                   restricciones_asignacion_exacta +  
                   "/* PRIORIDAD ASIGNACION: */\n" +
                   restricciones_prioridad_asignacion + 
                   "/* HORARIO PROFESORES: */\n" +
                   restricciones_horario_profesores +  
                   "/* DECLARACION BINARIA: */\n" +
                   declaracion_binarias)

# Escribir el modelo en un archivo .lp
with open('proyecto.lp', 'w') as file:
    file.write(modelo_lp_solve)

print("El archivo 'proyecto.lp' ha sido generado correctamente.")
