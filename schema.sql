CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    username TEXT,
    status TEXT,
    message TEXT,
    machine TEXT,
    timestamp TIMESTAMP
);

CREATE TABLE channels (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE
);
