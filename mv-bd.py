import boto3

# Crear cliente de EC2
ec2 = boto3.client('ec2')

def crear_grupo_seguridad(nombre_grupo, descripcion):
    try:
        # Verificar si el grupo de seguridad ya existe
        existing_groups = ec2.describe_security_groups(
            Filters=[{'Name': 'group-name', 'Values': [nombre_grupo]}]
        )
        if existing_groups['SecurityGroups']:
            print(f"El grupo de seguridad '{nombre_grupo}' ya existe. Usando el ID existente.")
            return existing_groups['SecurityGroups'][0]['GroupId']
        
        # Crear el grupo de seguridad si no existe
        response = ec2.create_security_group(
            GroupName=nombre_grupo,
            Description=descripcion,
            VpcId=get_vpc_default()  # Usar la VPC por defecto
        )
        security_group_id = response['GroupId']
        print(f"Grupo de seguridad creado con ID: {security_group_id}")

        # Agregar reglas al grupo de seguridad
        ec2.authorize_security_group_ingress(
            GroupId=security_group_id,
            IpPermissions=[
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 22,
                    'ToPort': 22,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]  # SSH
                },
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 5432,
                    'ToPort': 5432,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]  # PostgreSQL
                },
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 3306,
                    'ToPort': 3306,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]  # Aurora MySQL
                },
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 8000,
                    'ToPort': 8000,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]  # DynamoDB local
                }
            ]
        )
        print("Reglas de seguridad agregadas correctamente.")
        return security_group_id
    except Exception as e:
        print(f"Error al crear el grupo de seguridad: {e}")

def crear_instancia_bd(security_group_id):
    ami_id = obtener_ultima_ami_ubuntu()
    try:
        # Crear la instancia EC2
        response = ec2.run_instances(
            ImageId=ami_id,
            InstanceType='t2.micro',  # Instancia mínima para ahorrar
            KeyName='vockey',  # KeyPair SSH
            MinCount=1,
            MaxCount=1,
            SecurityGroupIds=[security_group_id],
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [{'Key': 'Name', 'Value': 'BaseDeDatos'}]
                }
            ],
            BlockDeviceMappings=[
                {
                    'DeviceName': '/dev/xvda',
                    'Ebs': {
                        'VolumeSize': 20,  # 20 GB de espacio
                        'DeleteOnTermination': True,
                        'VolumeType': 'gp2'
                    }
                }
            ]
        )
        instance_id = response['Instances'][0]['InstanceId']
        print(f"Instancia de Base de Datos creada con ID: {instance_id}")
        
        # Asignar una IP elástica
        elastic_ip = obtener_o_asignar_ip_elastica(instance_id)
        print(f"IP elástica asignada a la instancia: {elastic_ip}")
    except Exception as e:
        print(f"Error al crear la instancia de Base de Datos: {e}")

def obtener_ultima_ami_ubuntu():
    ec2_resource = boto3.client('ec2')
    images = ec2_resource.describe_images(
        Filters=[{'Name': 'name', 'Values': ['ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*']}],
        Owners=['099720109477']  # Canonical
    )
    latest_image = sorted(images['Images'], key=lambda x: x['CreationDate'], reverse=True)[0]
    return latest_image['ImageId']

def get_vpc_default():
    # Obtener la VPC por defecto
    vpcs = ec2.describe_vpcs(Filters=[{'Name': 'isDefault', 'Values': ['true']}])
    return vpcs['Vpcs'][0]['VpcId']

def obtener_o_asignar_ip_elastica(instance_id):
    try:
        # Verificar si ya hay una IP elástica asignada
        addresses = ec2.describe_addresses()
        for address in addresses['Addresses']:
            if 'InstanceId' in address and address['InstanceId'] == instance_id:
                print("IP elástica ya asignada.")
                return address['PublicIp']

        # Crear una nueva IP elástica
        allocation = ec2.allocate_address(Domain='vpc')
        ec2.associate_address(InstanceId=instance_id, AllocationId=allocation['AllocationId'])
        return allocation['PublicIp']
    except Exception as e:
        print(f"Error al asignar IP elástica: {e}")

# Ejecutar el script
security_group_id = crear_grupo_seguridad("BD-Security-Group", "Grupo de seguridad para la base de datos")
if security_group_id:
    crear_instancia_bd(security_group_id)

