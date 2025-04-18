-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    fullname TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Groups Table
CREATE TABLE IF NOT EXISTS groups (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT
);

-- Permissions Table
CREATE TABLE IF NOT EXISTS permissions (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT
);

-- Many-to-many Users <-> Groups
CREATE TABLE IF NOT EXISTS user_groups (
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    group_id INT REFERENCES groups(id) ON DELETE CASCADE,
    PRIMARY KEY(user_id, group_id)
);

-- Many-to-many Groups <-> Permissions
CREATE TABLE IF NOT EXISTS group_permissions (
    group_id INT REFERENCES groups(id) ON DELETE CASCADE,
    permission_id INT REFERENCES permissions(id) ON DELETE CASCADE,
    PRIMARY KEY(group_id, permission_id)
);

-- Authorization Logging
CREATE TABLE IF NOT EXISTS auth_logs (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    action TEXT NOT NULL,
    success BOOLEAN NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    details TEXT
);



INSERT INTO users (username, password_hash, fullname, email)
VALUES (
  'justingraboski@gmail.com',
  '$2b$12$pyeuCHMyobtbym6epMs2WeWiOi3ULbt0Yz6EjoE/4AfVA6jC8EyqC', -- 'password123'
  'Justin Graboski', 'justingraboski@gmail.com'
) ON CONFLICT (username) DO NOTHING;
