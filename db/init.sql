CREATE USER IF NOT EXISTS '${MYSQL_USER}'@'%' IDENTIFIED BY '${MYSQL_PASSWORD}';
GRANT ALL PRIVILEGES ON *.* TO '${MYSQL_USER}'@'%' IDENTIFIED BY '${MYSQL_PASSWORD}' WITH GRANT OPTION;
FLUSH PRIVILEGES;
-- GRANT ALL PRIVILEGES ON *.* TO 'flask_user'@'%' IDENTIFIED BY 'flask_password' WITH GRANT OPTION;
-- FLUSH PRIVILEGES;


-- Criação do banco de dados e tabela para o CRUD
CREATE DATABASE IF NOT EXISTS flask_db;
USE flask_db;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    photo VARCHAR(255) DEFAULT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Tabela de pontuações 
CREATE TABLE IF NOT EXISTS pontuacoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    categoria INT NOT NULL,
    pontuacao INT NOT NULL,
    data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    DELETE FROM pontuacoes WHERE pontuacao IS NULL;
    
    SELECT u.username, SUM(p.pontuacao) AS total_pontuacao
    FROM pontuacoes p
    JOIN users u ON p.user_id = u.id
    WHERE p.pontuacao IS NOT NULL
    GROUP BY u.username
    ORDER BY total_pontuacao DESC;
    IF categoria = 1 THEN
        SELECT u.username, SUM(p.pontuacao) AS total_pontuacao
        FROM pontuacoes p
        JOIN users u ON p.user_id = u.id
        WHERE p.categoria = 1 AND p.pontuacao IS NOT NULL
        GROUP BY u.username
        ORDER BY total_pontuacao DESC;
    END IF;

);


INSERT INTO users (username, email, password, photo, is_active)
VALUES (
    'admin',
    'joao.silva@example.com',
    '1234',
    NULL,
    TRUE
);