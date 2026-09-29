
// Incluir el mismo código autogenerado
pub mod usuarios {
    tonic::include_proto!("usuarios");
}
use std::path::Path;
use std::net::SocketAddr;
use std::path::PathBuf;
use hyper::body::Bytes;
use hyper::server::conn::http1;
use hyper::service::service_fn;
use hyper::{header, Method, Request, Response, StatusCode};
use hyper_util::rt::TokioIo;
use tokio::fs::File;
use tokio::io::AsyncReadExt;
use tokio::net::TcpListener;
use http_body_util::Full;
use serde_json::{json, Value};
//use tonic::transport::Channel;

use usuarios::usuario_service_client::UsuarioServiceClient;
use usuarios::UsuarioRequest;
use http_body_util::BodyExt;
use serde::Deserialize;
use hyper::body::Incoming;

#[derive(Deserialize, Debug)]
struct CrearUsuarioRequest {
    pub nombre: String,
    pub email: String,
}
async fn handle_request(req: Request<hyper::body::Incoming>) -> Result<Response<Full<Bytes>>, hyper::Error> {
// 1. Descomponer la petición en sus partes y su cuerpo
    let (parts, body) = req.into_parts();
    
    // 2. Extraer el path desde 'parts' (sin prestamos pendientes de 'req')
    let path = parts.uri.path();
    let method = &parts.method;

    if path.starts_with("/api/") {
        // 3. Ahora puedes pasar 'body' libremente
        return Ok(handle_api_routes(method, path, body).await);
    }
    // -------------------------------------------------------------
    // 2. BUSCAR ARCHIVOS ESTÁTICOS REALES (.js, .css, .png, etc.)
    // -------------------------------------------------------------
    let requested_path = path.trim_start_matches('/');
    let file_path = PathBuf::from("var/marlin/html").join(requested_path);

    if file_path.is_file() {
        if let Ok(contents) = read_file_to_bytes(&file_path).await {
            let mime_type = mime_guess::from_path(&file_path).first_or_octet_stream();
            return Ok(create_response(StatusCode::OK, mime_type.as_ref(), contents));
        }
    }

    // -------------------------------------------------------------
    // 3. FALLBACK DE LA SPA (Redirigir todo lo demás a index.html)
    // -------------------------------------------------------------
    let index_path = PathBuf::from("var/marlin/html/index.html");
    if let Ok(index_contents) = read_file_to_bytes(&index_path).await {
        return Ok(create_response(StatusCode::OK, "text/html", index_contents));
    }

    // Si var/marlin/html/index.html no existe
    Ok(create_response(
        StatusCode::INTERNAL_SERVER_ERROR,
        "text/plain",
        Bytes::from("Error: var/marlin/html/index.html no encontrado."),
    ))
}

// Sub-manejador exclusivo para endpoints de la API
async fn handle_api_routes(method: &Method, path: &str, req: hyper::body::Incoming) -> Response<Full<Bytes>> {
    let path_vec: Vec<&str> = path.split('/').filter(|s| !s.is_empty()).collect();
    match (method, path_vec.as_slice()) {
        // GET /api/usuarios
        (&Method::GET, ["api", "usuarios", id_raw]) => {
            // En lugar de expect(), usamos match/if let seguro
            match id_raw.parse::<i32>() {
                Ok(id) => {
                    let usuario_json = obtener_usuario_handler(&id).await.to_string();
                    create_response(StatusCode::OK, "application/json", Bytes::from(usuario_json))
                }
                Err(_) => {
                    let error_payload = r#"{"error": "El ID de usuario debe ser un número entero válido"}"#;
                    create_response(StatusCode::BAD_REQUEST, "application/json", Bytes::from(error_payload))
                }
            }
        }
    
        // GET /api/status
        (&Method::GET, &["api", "status"]) => {
            let json_payload = r#"{"status": "ok", "version": "1.0"}"#;
            create_response(StatusCode::OK, "application/json", Bytes::from(json_payload))
        }
        (&Method::GET, &["api", "passwords"]) => {
            // Aquí iría la lógica para obtener los passwords, por ejemplo:
            let json_payload = r#"{"passwords": ["pass1", "pass2", "pass3"]}"#;
            create_response(StatusCode::OK, "application/json", Bytes::from(json_payload))
        }
        (&Method::POST, &["api", "usuarios"]) => {
            // 1. Extraer y leer todos los bytes del cuerpo de la petición
            let body_bytes = match leer_cuerpo(req).await {
                Ok(bytes) => bytes,
                Err(err) => {
                    return create_response(
                        StatusCode::BAD_REQUEST,
                        "application/json",
                        Bytes::from(format!(r#"{{"error": "{}"}}"#, err)),
                    );
                }
            };

            // 2. Parsear/Deserializar el JSON recibido a la estructura Rust
            let nuevo_usuario: CrearUsuarioRequest = match serde_json::from_slice(&body_bytes) {
                Ok(datos) => datos,
                Err(_) => {
                    return create_response(
                        StatusCode::BAD_REQUEST,
                        "application/json",
                        Bytes::from(r#"{"error": "Formato JSON inválido o faltan campos obligatorios"}"#),
                    );
                }
            };

            // 3. (Aquí iría tu lógica de negocio, ej. guardar en Base de Datos o llamar gRPC)
            println!("Creando usuario: {:?}", nuevo_usuario);

            // 4. Responder con código 201 Created y los datos creados
            let respuesta_json = format!(
                r#"{{"mensaje": "Usuario creado con éxito", "nombre": "{}"}}"#,
                nuevo_usuario.nombre
            );

            create_response(StatusCode::CREATED, "application/json", Bytes::from(respuesta_json))
        }
        // Ruta de API no encontrada (Devuelve 404 JSON, NO el index.html)
        _ => {
            let error_payload = r#"{"error": "Endpoint de API no encontrado"}"#;
            create_response(StatusCode::NOT_FOUND, "application/json", Bytes::from(error_payload))
        }
    }
}
// Función para leer todo el cuerpo entrante como Bytes
async fn leer_cuerpo(body: Incoming) -> Result<hyper::body::Bytes, String> {
    body.collect()
        .await
        .map(|collected| collected.to_bytes())
        .map_err(|e| format!("Error al leer el cuerpo de la petición: {}", e))
}
async fn obtener_usuario_handler(id: &i32) -> Value {
    // 1. Conectar al microservicio gRPC en el puerto interno
    let mut client = match UsuarioServiceClient::connect("http://localhost:50051").await {
        Ok(c) => c,
        Err(_) => return json!({"error": "No se pudo conectar al microservicio"}),
    };

    // 2. Hacer la petición gRPC
    let request = tonic::Request::new(UsuarioRequest { id: *id });
    match client.obtener_usuario(request).await {
        Ok(response) => {
            let u = response.into_inner();
            json!({
                "id": u.id,
                "nombre": u.nombre,
                "email": u.email
            })
        }
        Err(status) => json!({"error": status.message()}),
    }
}
// Funciones auxiliares
async fn read_file_to_bytes(path: &PathBuf) -> Result<Bytes, std::io::Error> {
    let mut file = File::open(path).await?;
    let mut contents = Vec::new();
    file.read_to_end(&mut contents).await?;
    Ok(Bytes::from(contents))
}

fn create_response(status: StatusCode, content_type: &str, body: Bytes) -> Response<Full<Bytes>> {
    Response::builder()
        .status(status)
        .header(header::CONTENT_TYPE, content_type)
        .body(Full::new(body))
        .unwrap()
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
    let addr = SocketAddr::from(([127, 0, 0, 1], 3000));
    let listener = TcpListener::bind(addr).await?;
    println!("Servidor SPA + API corriendo en http://{}", addr);

    loop {
        let (stream, _) = listener.accept().await?;
        let io = TokioIo::new(stream);

        tokio::task::spawn(async move {
            if let Err(err) = http1::Builder::new()
                .serve_connection(io, service_fn(handle_request))
                .await
            {
                eprintln!("Error en la conexión: {:?}", err);
            }
        });
    }
}