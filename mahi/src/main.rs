use sqlx::MySqlPool;
use uuid::Uuid;

#[derive(sqlx::FromRow, serde::Serialize)]
pub struct VaultItem {
    pub id: Vec<u8>,             // BINARY(16)
    pub encrypted_data: String,  // TEXT
    pub iv: Vec<u8>,             // BINARY(12)
    pub auth_tag: Vec<u8>,       // BINARY(16)
}

pub async fn get_user_items(pool: &MySqlPool, user_id: Uuid) -> Result<Vec<VaultItem>, sqlx::Error> {
    let items = sqlx::query_as::<_, VaultItem>(
        "SELECT id, encrypted_data, iv, auth_tag FROM vault_items WHERE user_id = ?"
    )
    .bind(user_id.as_bytes().as_slice())
    .fetch_all(pool)
    .await?;

    Ok(items)
}
fn main() {
    println!("Hello, world!");
}