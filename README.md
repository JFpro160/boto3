# Creación de Máquina Virtual (MV) para Base de Datos en AWS usando Boto3

Este proyecto crea una máquina virtual (MV) en AWS, configurada para manejar PostgreSQL, MySQL (Aurora) y DynamoDB, además de permitir acceso por SSH. Utilizamos **Boto3** para gestionar los recursos en AWS.

## Requisitos previos

1. **AWS CLI** configurado con tus credenciales y región.
2. **Python 3** instalado en tu sistema.
3. El archivo del keypair **`vockey.pem`** para conectarte vía SSH a la instancia.

## Configuración del AWS CLI

Si aún no has configurado el AWS CLI, puedes hacerlo con los siguientes comandos:

1. Instala AWS CLI (si aún no lo has hecho):
   
   ```bash
   sudo apt-get install awscli  # En Ubuntu/Debian
   # O en MacOS:
   brew install awscli
   ```

2. Configura tus credenciales y región:

   ```bash
   aws configure
   ```

   Luego, introduce tus credenciales de acceso (Access Key ID, Secret Access Key), la región (por ejemplo, `us-east-1`) y el formato de salida preferido (JSON está bien).

   Para verificar que está bien configurado, revisa el archivo `~/.aws/config`, que debería verse algo así:

   **`~/.aws/config`**:
   ```ini
   [default]
   region = us-east-1
   ```

   **`~/.aws/credentials`**:
   ```ini
   [default]
   aws_access_key_id = YOUR_ACCESS_KEY
   aws_secret_access_key = YOUR_SECRET_KEY
   ```

## Uso del script de shell para automatizar el proceso

### 1. Hacer que el script sea ejecutable

Primero, asegúrate de que el script de shell sea ejecutable con el siguiente comando:

```bash
chmod +x script.sh
```

### 2. Ejecutar el script de shell

Para automatizar el proceso de creación del entorno, instalación de dependencias y ejecución del script de Python, ejecuta:

```bash
./script.sh
```

El script hará lo siguiente:

1. Crear un entorno virtual en Python.
2. Instalar las dependencias necesarias desde `requirements.txt`.
3. Ejecutar el script de Python para crear la máquina virtual en AWS.

### 3. Conectar a la MV vía SSH

Cuando el script termine de ejecutarse, la máquina virtual estará lista con una IP elástica asignada. Puedes conectarte a la MV vía SSH con el siguiente comando:

```bash
ssh -i /ruta/a/vockey.pem ubuntu@<tu-ip-elastica>
```

Reemplaza `/ruta/a/vockey.pem` con la ruta a tu archivo keypair, y `<tu-ip-elastica>` con la IP asignada por el script.

### 4. Borrar los recursos creados

Para borrar los recursos creados, usa los siguientes comandos con los **IDs generados por el script**:

```bash
# Terminar la instancia EC2
aws ec2 terminate-instances --instance-ids <instance-id>

# Liberar la IP elástica
aws ec2 release-address --allocation-id <allocation-id>

# Eliminar el grupo de seguridad
aws ec2 delete-security-group --group-id <group-id>
```

### Notas sobre los IDs

Los IDs de las instancias y grupos de seguridad son generados automáticamente por AWS cuando creas estos recursos. El script mostrará los IDs en la salida de la terminal para que puedas usarlos luego para borrar los recursos. No es posible definir directamente un ID específico para los grupos de seguridad o instancias, pero el script te permitirá identificar fácilmente los recursos creados.

## Script de Shell

Aquí está el script que automatiza el proceso de creación del entorno y ejecución del script de Python:

```bash
#!/bin/bash

# Crear un entorno virtual
python3 -m venv .venv

# Activar el entorno virtual
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar el script para crear la MV de base de datos
python3 mv-bd.py
```

### Instrucciones para el script de shell:

1. Haz que el script sea ejecutable:

```bash
chmod +x script.sh
```

2. Ejecuta el script:

```bash
./script.sh
```

Este script creará la máquina virtual en AWS, asignará una IP elástica, configurará las reglas de seguridad para SSH, PostgreSQL, MySQL y DynamoDB, y estará lista para que la uses.

## Recomendación de recursos:

- **Instancia EC2**: `t2.micro` (opción económica y dentro del free tier de AWS).
- **Espacio de almacenamiento**: 20 GB de espacio (especificado en el script).

Si tienes más dudas o necesitas ajustar algún parámetro, no dudes en preguntar.
```

