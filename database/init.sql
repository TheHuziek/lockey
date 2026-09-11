-- init.sql

-- Opcional: Asegúrate de usar la base de datos correcta
USE lockeydb;

-- Crear la tabla
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Opcional: Insertar datos iniciales
INSERT INTO usuarios (nombre, email) VALUES 
('Carlos Mendoza', 'carlos@example.com'),
('Ana Gomez', 'ana@example.com'),
('luciana mercado', 'luciana@example.com'),
('maricler lopez', 'maricler@example.com'),
('jose hernandez', 'josehernandez@example.com'),
('teresa sanchez', 'tere@example.com'),
('Luna martinez', 'lunam@example.com'),
('nicolas gonzalez', 'nico@example.com'),
('Alejandro castro', 'alex@example.com'),
('Viri Torres', 'viriT@example.com');