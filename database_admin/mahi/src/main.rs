use sqlx::MySqlPool;
use uuid::Uuid;
use tonic::{transport::Server, Request, Response, Status};

// Incluir el código autogenerado por tonic
pub mod usuarios {
    tonic::include_proto!("usuarios");
}

use usuarios::usuario_service_server::{UsuarioService, UsuarioServiceServer};
use usuarios::{UsuarioRequest, UsuarioResponse};
#[derive(sqlx::FromRow, serde::Serialize, Debug)]
pub struct VaultItem {
    pub id: i32,
    pub nombre: String,
    pub correo: String,
    pub dia_de_creacion: String,
}

pub async fn get_user(pool: &MySqlPool, user_id: i32) -> Result<VaultItem, sqlx::Error> {
    let items = sqlx::query_as::<_, VaultItem>(
        "SELECT id, nombre, correo, dia_de_creacion FROM usuarios WHERE id = ?"
    )
    .bind(user_id)
    .fetch_all(pool)
    .await?;

    Ok(items)
}
#[derive(Debug, Default)]
pub struct MiUsuarioService;

#[tonic::async_trait]
impl UsuarioService for MiUsuarioService {
    async fn obtener_usuario(
        &self,
        request: Request<UsuarioRequest>,
    ) -> Result<Response<UsuarioResponse>, Status> {
        let req = request.into_inner();
        let user = get_user(&MySqlPool::connect("mysql://user:pass@host/database").await.unwrap(), req.id).await.unwrap();
        // Lógica de negocio (ej. consultar base de datos)
        let respuesta = UsuarioResponse {
            id: user.id,
            nombre: user.nombre,
            email: user.correo,
        };
        
        Ok(Response::new(respuesta))
    }
}


#[tokio::main]
async fn main() {
    println!("Hello, world!");
    let pool = MySqlPool::connect("mysql://user:pass@host/database").await.unwrap();
    let user_id = Uuid::new_v4();
    let items=get_user_items(&pool, user_id).await.unwrap();
    println!("{:#?}", items);
}