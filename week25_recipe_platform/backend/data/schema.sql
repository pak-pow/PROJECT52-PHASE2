DROP TABLE IF EXISTS recipes;

CREATE TABLE recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    ingredients TEXT NOT NULL, 
    instructions TEXT NOT NULL, 
    image_filename TEXT,       
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);