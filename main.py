from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import ply.yacc as yacc
import ply.lex as lex

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas las orígenes (modifica esto según tu necesidad)
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos
    allow_headers=["*"],  # Permite todos los encabezados
)

# Modelo para la solicitud de datos
class CodeRequest(BaseModel):
    code: str

palabrasClave = ["else","return","str","float","for","if","while","do","int"] #Palabras reservadas en C

#Detectar el error
ERROR = []

#LISTA DE SIMBOLOS {  identificador : [tipo de dato, direccion, tamaño]}
ListaSimbolos={}

#LISTA DE FUNCIONES { identificador : tipo que devuelve,[Lista de tipos datos de parametros]}
ListaFunciones ={}

#LISTA DE PARAMETROS TEMPORALES [Lista de tipos datos de parametros]
ListaParametros=[]

#LISTA DE ARGUEMENTOS TEMPORALES [Lista de expresiones]
ListaArgumentos = []

tokens = [
    # Literals (identifier, integer constant, float constant, string constant, char const)
    'ID', 'INTEGER', 'FLOAT', 'STR',

    # Operators (+,-,*,/,%,|,~,^,<<,>>, ||, &&, !, <, <=, >, >=, ==, !=)
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MODULO',
    'LOR', 'LAND', 'LNOT',
    'LT', 'LE', 'GT', 'GE', 'EQ', 'NE',

    # Assignment (=)
    'EQUALS',

    # Increment/decrement (++,--)
    'INCREMENT', 'DECREMENT',

    # Ternary operator (?)
    'TERNARY',

    # Delimiters ( ) [ ] { } , . ; :
    'LPAREN', 'RPAREN',
    'LBRACE', 'RBRACE',
    'COMMA', 'SEMI', 'COLON',

] + palabrasClave

# Operators
t_PLUS             = r'\+'
t_MINUS            = r'-'
t_TIMES            = r'\*'
t_DIVIDE           = r'/'
t_MODULO           = r'%'
t_LOR              = r'\|\|'
t_LAND             = r'&&'
t_LNOT             = r'!'
t_LT               = r'<'
t_GT               = r'>'
t_LE               = r'<='
t_GE               = r'>='
t_EQ               = r'=='
t_NE               = r'!='

# Assignment operators
t_EQUALS           = r'='

# Increment/decrement
t_INCREMENT        = r'\+\+'
t_DECREMENT        = r'--'

# ?
t_TERNARY          = r'\?'

# Delimiters
t_LPAREN           = r'\('
t_RPAREN           = r'\)'
t_LBRACE           = r'\{'
t_RBRACE           = r'\}'
t_COMMA            = r','
t_SEMI             = r';'
t_COLON            = r':'

# String literal
t_STR = r'\"([^\"]*)\"'

# Character constant 'c' or L'c'
#t_CHARACTER = r'(L)?\'([^\\\n]|(\\.))*?\''

t_ignore  = ' \t'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_ID(t):
    r'[A-Za-z_][A-Za-z0-9_]*'
    if t.value in palabrasClave:
        t.type =t.value  # Cambia el tipo si es una palabra clave ya que se debe quedar 
    return t

def t_FLOAT(t):
	r'\d+\.\d+'
	t.value = float(t.value)
	return t

def t_INTEGER(t):
	r'\d+'
	t.value = int(t.value)
	return t

# Comment (C-Style)
def t_COMMENT(t):
    r'/\*(.|\n)*?\*/'
    t.lexer.lineno += t.value.count('\n')
    return t

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# Definimos cada regla de la gramática en forma de función para PLY.
# La función `p_<NoTerminal>` define cada producción y usa la sintaxis PLY para especificar las reglas.

def p_program(p):
    '''program : external_declaration
               | program external_declaration'''
    p[0] = "Programa corrido correctamente"


def p_external_declaration(p):
    '''external_declaration : function_definition
                            | declaration'''
    pass

#LISTA DE FUNCIONES {identificador : tipo que devuelve, [Lista de tipos datos de parametros]}
def p_function_definition(p):
    '''function_definition : type_specifier ID LPAREN parameter_list RPAREN compound_statement
                           | type_specifier ID LPAREN RPAREN compound_statement'''
    global ListaParametros
    ListaFunciones[p[2]] = (p[1], ListaParametros) #Se agrega por definicion el valor de devolucion
    ListaParametros = []
    pass

def p_declaration(p): #Declaration
	'''declaration : init_declarator_list SEMI'''
	pass

#LISTA DE SIMBOLOS {  identificador : [tipo de dato, dato, tamaño]}
# int a;
def p_init_declarator_list(p): #Voy metiendo los identificadores a la tabla de simbolos
	'''init_declarator_list : type_specifier init_declarator'''
	tamaño = len(p)
	if (tamaño == 3):
		if (ListaSimbolos[p[2]][1] != 0 and type(ListaSimbolos[p[2]][1]).__name__ != p[1]):
			ERROR.append(f"Error de asignacion, no es del tipo")
		ListaSimbolos[p[2]][0] = p[1]
	p[0] = p[1]

def p_type_specifier(p):
	'''type_specifier : int
	| float
	| str'''
	p[0]= p[1]


def p_init_declarator(p): #Ahora guardo el valor, si es que se inicializa.
	'''init_declarator : declarator
	| declarator EQUALS initializer'''
	if (len(p) == 4): ListaSimbolos[p[1]][1] = p[3]
	p[0] = p[1] 

#LISTA DE SIMBOLOS {  identificador : [tipo de dato, dato, tamaño]}

def p_declarator(p): #Que pasa si desde aqui meto los valores a la tabla donde, el ID es la llave, sino se modifica 'ID', entonces
	'''declarator : ID'''
	p[0]= p[1]
	ListaSimbolos[p[1]] =[None,0,None]
    
    
def p_parameter_list(p):
    '''parameter_list : parameter
                      | parameter_list COMMA parameter'''
    pass

#Se agregan los parametros al arreglo de parametros, para luego guardarlo
#Se al ponerlo en parametros, son las denominadas declaraciones rapidas, ya que se declaran de manera global
def p_parameter(p):
    '''parameter : type_specifier declarator'''
    ListaParametros.append(p[1])

#No acepta inicializacion de arreglos
def p_initializer(p):
	'''initializer : assignment_expression '''
	p[0] = p[1]
    
    
def p_statement_list(p):
    '''statement_list : statement
                      | statement_list statement'''
    pass

def p_statement(p):
	'''statement : expression_statement
	| declaration	
	| compound_statement
	| selection_statement
	| iteration_statement
	| jump_statement'''
	p[0] = p[1]

def p_expression_statement(p):
    '''expression_statement : expression SEMI'''
    pass

def p_compound_statement(p):
	'''compound_statement : LBRACE statement_list RBRACE
	| LBRACE  RBRACE'''
	pass


def p_selection_statement(p):
    '''selection_statement : if LPAREN expression RPAREN statement
                           | if LPAREN expression RPAREN statement else statement'''
    pass

def p_iteration_statement(p):
    '''iteration_statement : while LPAREN expression RPAREN statement
                           | do statement while LPAREN expression RPAREN SEMI
                           | for LPAREN expression SEMI expression SEMI expression RPAREN statement'''
    if (len(p) == 5): p[0] = p[3]
    elif (len(p) == 7): p[0] = p[3]
    else: p[0] = p[5] 

def p_jump_statement(p):
    '''jump_statement : return expression SEMI'''
    pass

def p_expression(p):
	'''expression : assignment_expression
	| expression COMMA assignment_expression'''
	if (len(p)==2): p[0] = p[1]
	else: p[0] = p[3]

def p_assignment_expressionConstante(p):
	'''assignment_expression : conditional_expression '''
	p[0] = p[1]

def p_assignment_expression(p): #Aqui se debe verificar que unary es un id previamente creado en la tabla de simbolos
	'''assignment_expression : ID EQUALS assignment_expression'''
	
	if (p[1] not in ListaSimbolos): 
		ERROR.append("Error semantico, no se encuentra dicho id: ", p[1])
		return
	if (ListaSimbolos[p[1]][0] == type(p[3]).__name__):
		print("LD id(direccion de memoria), Acumulador ")
		ListaSimbolos[p[1]][1] = p[3]
		p[0] = p[3]
	else: 
		ERROR.append(f" Error en la linea: {p.lineno(1)},Error semantico el valor asignado es de otro tipo, al id") 
		return
			

#Yo solo voy a verificar que se ha diferente de 0
def p_conditional_expression(p):
	'''conditional_expression : logical_or_expression
	| logical_or_expression TERNARY expression COLON conditional_expression'''
	if (len(p)==2): p[0] = p[1]
	else:
		if (type(p[1]) != type(1)): 
			ERROR.append(f"Error en la linea: {p.lineno(1)},Error Semantica, la condicion debe ser entera")
			return
		p[0] = p[3] if p[1] != 0 else p[5]
	
def p_logical_or_expression(p):
	'''logical_or_expression : logical_and_expression
	| logical_or_expression LOR logical_and_expression'''
	if (len(p)==2): p[0] = p[1]
	else:
		if not (isinstance(p[1], (int, float)) and isinstance(p[3], (int, float))): 
			ERROR.append(f"Error en la linea: {p.lineno(1)},Error Semantico,no acepta comparacion cadenas0")
			return 
		if (p[2] == '||'): p[0] = 1 if (p[2] != 0 or p[3] != 0) else 0
	
#Sabemos que cualquier numero por 0, me da cero, y cualquier numero + 0, me da el numero.
def p_logical_and_expression(p):
	'''logical_and_expression : equality_expression
	| logical_and_expression LAND equality_expression'''
	if (len(p)==2): p[0] = p[1]
	else:
		if not (isinstance(p[1], (int, float)) and isinstance(p[3], (int, float))): 
			ERROR.append(f"Error en la linea: {p.lineno(1)},Error Semantico, no acepta comparacion cadenas3")
			return
		if (p[2] == '&&'): p[0] = 1 if (p[2] != 0 and p[3] != 0) else 0

def p_equality_expression(p):
	'''equality_expression : relational_expression
	| equality_expression EQ relational_expression
	| equality_expression NE relational_expression'''
	if (len(p)==2): p[0] = p[1]
	else:
		if not (isinstance(p[1], (int, float)) and isinstance(p[3], (int, float))): 
			ERROR.append(f"Error en la linea: {p.lineno(1)},Error Semantico, no acepta comparacion cadenas2")
			return 
		if (p[2] == '=='): p[0] = 1 if p[1] == p[3] else 0
		elif (p[2] == '!='): p[0] = 1  if p[1] != p[3] else 0
		
# <, <=, >, >=, ==, !=
def p_relational_expression(p):
	'''relational_expression : additive_expression
	| relational_expression LT additive_expression
	| relational_expression GT additive_expression
	| relational_expression LE additive_expression
	| relational_expression GE additive_expression'''
	if (len(p)==2): p[0] = p[1]
	else:
		if not (isinstance(p[1], (int, float)) and isinstance(p[3], (int, float))): 
				ERROR.append(f"Error en la linea: {p.lineno(1)},Error Semantico, no acepta comparacion de cadenas1") 
				return
		if (p[2] == '<'): p[0] = 1 if p[1] < p[3] else 0
		elif (p[2] == '>'): p[0] = 1  if p[1] > p[3] else 0
		elif (p[2] == '<='): p[0] = 1 if p[1] <= p[3] else 0
		elif (p[2] == '>='): p[0] = 1 if p[1] >= p[3] else 0
		
def p_additive_expression(p):
	'''additive_expression : multiplicative_expression
	| additive_expression PLUS multiplicative_expression
	| additive_expression MINUS multiplicative_expression'''
	if (len(p)==2): p[0] = p[1]
	else:
		if not (isinstance(p[1], (int, float)) and isinstance(p[3], (int, float))): 
			ERROR.append(f"Error en la linea: {p.lineno(1)}, Error Semantico, no es tipo numerico") 
			return 
		if (p[2] == '+'): p[0] = p[1] + p[3]
		elif (p[2] == '-'): p[0] = p[1] - p[3]

def p_multiplicative_expression(p):
	'''multiplicative_expression : unary_expression
	| multiplicative_expression TIMES unary_expression
	| multiplicative_expression DIVIDE unary_expression
	| multiplicative_expression MODULO unary_expression'''
	if (len(p)==2): p[0] = p[1]
	else:
		if not (isinstance(p[1], (int, float)) and isinstance(p[3], (int, float))): 
			ERROR.append(f"Error en la linea: {p.lineno(1)}, Error Semantico, no es tipo numerico") 
			return
		if (p[2] == '*'): p[0] = p[1] * p[3]
		elif (p[2] == '/'): p[0] = p[1] / p[3]
		elif (p[2] == '%'): p[0] = p[1] % p[3]

def p_unary_expression(p):
	'''unary_expression : postfix_expression
	| LNOT unary_expression
	| MINUS unary_expression
	| INCREMENT unary_expression
	| DECREMENT unary_expression'''
	if (len(p)==2): p[0] = p[1]
	else: 
		if not (isinstance(p[2], (int, float))): 
			ERROR.append(f"Error en la linea: {p.lineno(1)}, Error Semantico, no es tipo numerico") 
			return
		if(p[1] == '!'): p[0] = 0 if p[2] != 0 else 1 
		elif(p[1] == '-'): p[0] = -p[2]
		elif(p[1] == '++'): p[0] = p[2] + 1
		elif(p[1] == '--'): p[0] = p[2] - 1

def p_postfix_expression(p): #La primera opcion es traspado de funcion, la segunda es la asignacion de un arreglo, y la tercera es funcion con sus parametros, quite la llamada a punteros . y ->
	'''postfix_expression : primary_expression'''
	p[0] = p[1] #Regresa el tipo

#Representa una llama a funcion por lo cual, se verifica que exista la funcion, y que cada elemento se ha del mismo tipo al declarado	
def p_postfix_Expression_Funciones(p):
	''' postfix_expression : ID LPAREN argument_expression_list RPAREN '''
	if(p[1] not in ListaFunciones): 
		ERROR.append(f"Definir primero la funcion : {p[1]}")
		return
	global ListaArgumentos
	Paramentros  = ListaFunciones[p[1]][1]
	if (len(ListaArgumentos) == len(Paramentros)):
		for i in range(len(ListaArgumentos)):
			if (Paramentros[i] != type(ListaArgumentos[i]).__name__):
				ERROR.append(f" Funcion; {p[1]} : Asignacion de argumentos de diferente tipo, {ListaArgumentos[i]}, se esperaba {Paramentros[i]}")
				return
	else: 
		ERROR.append(f"Funcion: {p[1]} , Revisar numero de argumentos")
		return
	#Simulamos el comportamiento de retorno
	t = 1
	if (ListaFunciones[p[1]][0] == "float"): t = 2.4
	elif  (ListaFunciones[p[1]][0] == "str"): t = "Tem"
	ListaArgumentos = []
	p[0]= t
		
#raise SyntaxError("Error: Literal '*' encontrado, deteniendo el análisis.")		
#Aqui realizamos la validacion del id, y en las demas damos por hecho que ya se atrapo aqui el error del id, que se haya declarado
def p_primary_expression_ID(p):
	'''primary_expression : ID '''
	if (p[1] not in ListaSimbolos): 
		ERROR.append(f"Error en la linea: {p.lineno(1)} Declara primero el id : {p[1]}")
		return
	else: 
		p[0] = ListaSimbolos[p[1]][1] if p[1] in ListaSimbolos else p[1]

def p_primary_expression(p):
	'''primary_expression : INTEGER
	| FLOAT
	| STR
	| LPAREN expression RPAREN'''
	#Se verifica y se obtiene el valor de la lista de simbolos
	if (len(p) == 2 ): p[0] = p[1]#ListaSimbolos[p[1]][1] if p[1] in ListaSimbolos else p[1] #ListaSimbolos[p[1]][1] if p[1] in ListaSimbolos else p[1] #Primer caso, solo traspasamo el valor
	else: 
		p[0] = p[2] #Segundo caso, solo traspasamo el valor de la expresion para su posterior verificacion

#Lo que puedo hacer es un pop a cada valor del arreglo hasta que vacie [P1,P2,P3]---[P2,P3]----[P3]----[], si no hay mas datos entonces error y se va verificando que si el tipo coincide con lo que le meti
def p_argument_expression_list(p):
	'''argument_expression_list : assignment_expression
	| argument_expression_list COMMA assignment_expression'''
	if (len(p) == 2): ListaArgumentos.append(p[1])
	else: ListaArgumentos.append(p[3])

    
# Error rule for syntax errors
def p_error(p):
	if p:
		print(f"Error de sintaxis en la línea {p.lineno}, algo falta antes de {p.value}")
		raise ValueError("Error de sintaxis")
	else:
		print(f"Error de sintaxis al final de la entrada")
		raise ValueError("Error de sintaxis")


# Function to create and initialize the lexer and parser
def create_lexer_and_parser():
    # Define your lexer and parser construction here
    lexer = lex.lex()
    parser = yacc.yacc()
    return lexer, parser

@app.post("/submit-code")
async def submit_code(request: CodeRequest):
    global ERROR, ListaSimbolos, ListaFunciones

    # Reset state for each request
    ERROR = []
    ListaSimbolos = {}
    ListaFunciones = {}

    # Create a new lexer and parser for this request
    lexer, parser = create_lexer_and_parser()

    # Set up the lexer with the provided code
    lexer.input(request.code)
    lexer.lineno = 1  # Ensure the line number starts at 1

    try:
        # Parse the code
        result = parser.parse(request.code, lexer=lexer)
        
        # Check for semantic errors
        if len(ERROR) != 0:
            return {"message": "Semantic errors", "errors": ERROR}
        
        return {
            "message": "Syntax check passed. Program executed successfully.",
            "symbols": ListaSimbolos,
            "functions": ListaFunciones,
        }
    except Exception as e:
        return {"message": "Syntax error", "errors": [str(e)]}
