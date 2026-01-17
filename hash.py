import bcrypt

# Escribe aquí la contraseña que quieres usar entre las comillas
password = "u3w6FyXQ36uuyV" 

# Generar el hash
hash_generado = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# Imprimir el resultado para copiarlo
print(hash_generado.decode('utf-8'))