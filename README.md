# Introduction 
Repositorio exclusivo para el desarrollo de la aplicacion web de chats.


NOTA: Realizar sus commits diarios en esta rama, y clonar el repo diario para llevar el proyecto actualizado, de la siguiente manera:
```
git clone https://programacion-4-app@dev.azure.com/programacion-4-app/chat-app/_git/chat-app
```

# Getting Started
Pequeña intro de como usar este repositorio:

1. Primero inicializamos git:
```
git init
```
2. Despues agregamos nuetro repo remoto como *origin* (puedes ponerle el nombre que quieras):
```
git remote add origin https://programacion-4-app@dev.azure.com/programacion-4-app/chat-app/_git/chat-app
```
3. Ahora vamos a hacer Fetch de nuestro repo remoto (La rama main solo sera para los commits de produccion):
```
git fetch origin
```
4. Ahora validamos nuestra rama de desarrollo (este paso es opcional):
```
git checkout desarrollo
```
5. Ahora agregamos todos nuestros documentos a nuestro nuevo pull:
```
git add .
```
6. Ahora hacemos nuestro commit de los cambios:
```
git commit -m "La informacion de nuestros cambios"
```
7. Y ahora hacemos nuestro push:
```
git push origin desarrollo
```