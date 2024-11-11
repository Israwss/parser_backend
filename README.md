## C Language Parser using FastAPI and PLY

This API provides a tool to parse C language code and identify potential semantic errors. It uses FastAPI as a web framework and PLY (Python Lex-Yacc) for parsing functionalities.

### Features

* Parses C code provided in the request body.
* Identifies semantic errors during parsing and returns them as a list.
* Outputs the symbol table and function definitions if no errors are found.

### Usage

1. **Install dependencies:**

   ```bash
   pip install fastapi ply
   ```

2. **Run the server:**

   ```bash
   uvicorn main:app --reload
   ```

3. **Send a POST request to `/submit-code` endpoint:**

   ```
   curl -X POST http://localhost:8000/submit-code -H "Content-Type: application/json" -d '{"code": "int a; a = 10;"}'
   ```

### Response

* **Success:**

   ```json
   {
       "message": "Prueba de sintaxis superada\nPrograma corrido correctamente",
       "symbols": {
           "a": ["int", 10, None]
       },
       "functions": {}
   }
   ```

* **Error:**

   ```json
   {
       "message": "Errores semánticos",
       "errors": [
           "Error en la linea: 1, Error semantico, no se encuentra dicho id: b"
       ]
   }
   ```

### Notes

* This parser currently handles a subset of the C language syntax and semantics.
* The symbol table stores identifiers (`ID`), their data type (`type`), value (`dato`), and size (`tamaño`).
* The function definitions dictionary stores function names (`identifier`), return type (`tipo que devuelve`), and parameter data types (`lista de tipos datos de parametros`).
* This is a basic implementation and may not cover all potential semantic errors.

This API can be a helpful tool for students learning C syntax and identifying common parsing errors.
