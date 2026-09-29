-- init.sql

-- Opcional: Asegúrate de usar la base de datos correcta
USE lockeydb;

-- Crear la tabla
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    plataforma VARCHAR(100) NOT NULL,
    nombre_usuario VARCHAR(100) NOT NULL,
    pass VARCHAR(100) UNIQUE NOT NULL,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

