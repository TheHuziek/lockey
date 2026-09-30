import grpc
from concurrent import futures
import pass_data_pb2
import pass_data_pb2_grpc
from database import SessionLocal, UsuarioModel, init_db

class UsuarioServiceServicer(pass_data_pb2_grpc.UsuarioServiceServicer):

    def CrearUsuario(self, request, context):
        db = SessionLocal()
        try:
            nuevo_usuario = UsuarioModel(nombre=request.nombre, email=request.email)
            db.add(nuevo_usuario)
            db.commit()
            db.refresh(nuevo_usuario)
            return pass_data_pb2.Usuario(
                id=nuevo_usuario.id,
                nombre=nuevo_usuario.nombre,
                email=nuevo_usuario.email
            )
        finally:
            db.close()

    def ObtenerUsuario(self, request, context):
        db = SessionLocal()
        try:
            usuario = db.query(UsuarioModel).filter(UsuarioModel.id == request.id).first()
            if not usuario:
                context.abort(grpc.StatusCode.NOT_FOUND, "Usuario no encontrado")
            return pass_data_pb2.Usuario(id=usuario.id, nombre=usuario.nombre, email=usuario.email)
        finally:
            db.close()

    def ListarUsuarios(self, request, context):
        db = SessionLocal()
        try:
            usuarios = db.query(UsuarioModel).all()
            respuesta = [pass_data_pb2.Usuario(id=u.id, nombre=u.nombre, email=u.email) for u in usuarios]
            return pass_data_pb2.ListaUsuariosResponse(usuarios=respuesta)
        finally:
            db.close()

    def ActualizarUsuario(self, request, context):
        db = SessionLocal()
        try:
            usuario = db.query(UsuarioModel).filter(UsuarioModel.id == request.id).first()
            if not usuario:
                context.abort(grpc.StatusCode.NOT_FOUND, "Usuario no encontrado")
            
            usuario.nombre = request.nombre
            usuario.email = request.email
            db.commit()
            db.refresh(usuario)
            return pass_data_pb2.Usuario(id=usuario.id, nombre=usuario.nombre, email=usuario.email)
        finally:
            db.close()

    def EliminarUsuario(self, request, context):
        db = SessionLocal()
        try:
            usuario = db.query(UsuarioModel).filter(UsuarioModel.id == request.id).first()
            if not usuario:
                context.abort(grpc.StatusCode.NOT_FOUND, "Usuario no encontrado")
            
            db.delete(usuario)
            db.commit()
            return pass_data_pb2.EliminarUsuarioResponse(exito=True)
        finally:
            db.close()

def serve():
    init_db()  # Inicializar la base de datos
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pass_data_pb2_grpc.add_UsuarioServiceServicer_to_server(UsuarioServiceServicer(), server)
    
    puerto = "50051"
    server.add_insecure_port(f"[::]:{puerto}")
    print(f"Servidor gRPC corriendo en el puerto {puerto}...")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()