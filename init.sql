PRAGMA foreign_keys = ON;

CREATE TABLE vehicle(
    vin VARCHAR(50) PRIMARY KEY NOT NULL,
    make INTEGER SECONDARY NOT NULL,
    model INTEGER SECONDARY NOT NULL,
    year INTEGER NOT NULL,
    body INTEGER SECONDARY NOT NULL,
    price_certified REAL NOT NULL,
    price_private REAL,
    price_retail REAL,
    price_trade REAL,
    FOREIGN KEY(make) REFERENCES make(make) ON DELETE CASCADE,
    FOREIGN KEY(model) REFERENCES model(model) ON DELETE CASCADE,
    FOREIGN KEY(body) REFERENCES body(body) ON DELETE CASCADE
);

CREATE TABLE make(
    make INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    name VARCHAR(50) NOT NULL
);

CREATE TABLE model(
    model INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    make INTEGER SECONDARY NOT NULL,
    name VARCHAR(50) NOT NULL,
    FOREIGN KEY(make) REFERENCES make(make) ON DELETE CASCADE
);

CREATE TABLE body(
    body INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    name VARCHAR(50) NOT NULL
);

CREATE INDEX make_index on make (name);
CREATE INDEX model_index on model (name);
CREATE INDEX make_model_index on model (make,name);
CREATE INDEX body_index on body (name);