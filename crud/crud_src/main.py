import grpc
import contrasena_pb2
import contrasena_pb2_grpc

def ejecutar_cliente():
    # Abrimos un canal de comunicación inseguro (sin SSL/TLS) hacia el servidor
    with grpc.insecure_channel('localhost:50051') as channel:
        # Creamos el "stub" (el cliente que conoce los métodos del servicio)
        stub = contrasena_pb2_grpc.ServicioContrasenasStub(channel)
        
        # Construimos la petición
        peticion = contrasena_pb2.SolicitudContrasena(id=123)
        print(f"[Cliente] Solicitando información para el ID: {peticion.id}")
        
        # Realizamos la llamada remota como si fuera una función local
        respuesta = stub.ObtenerContrasena(peticion)
        
        print("\n--- Respuesta del Servidor ---")
        print(f"Contrasena: {respuesta.contrasena}")

if __name__ == '__main__':
    ejecutar_cliente()
