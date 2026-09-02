use sqlx::MySqlPool;
use uuid::Uuid;

#[derive(sqlx::FromRow, serde::Serialize, Debug)]
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
#[tokio::main]
async fn main() {
    println!("Hello, world!");
    let pool = MySqlPool::connect("mysql://user:pass@host/database").await.unwrap();
    let user_id = Uuid::new_v4();
    let items=get_user_items(&pool, user_id).await.unwrap();
    println!("{:#?}", items);
}