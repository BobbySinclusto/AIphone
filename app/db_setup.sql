CREATE TABLE Users (
    id INTEGER PRIMARY KEY NOT NULL,
    username VARCHAR(255)
);

CREATE TABLE Games (
    id INTEGER PRIMARY KEY NOT NULL,
    num_turns INT NOT NULL
);

CREATE TABLE Players (
    user_id INT NOT NULL,
    game_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(id),
    FOREIGN KEY (game_id) REFERENCES Games(id),
    PRIMARY KEY (user_id, game_id)
);

CREATE TABLE Rounds (
    id INTEGER PRIMARY KEY NOT NULL,
    round_number INT NOT NULL,
    game_id INT NOT NULL,
    FOREIGN KEY (game_id) REFERENCES Games(id)
);

CREATE TABLE Images (
    id INTEGER PRIMARY KEY NOT NULL,
    drawn_for INTEGER NOT NULL,
    prompt TEXT,
    path VARCHAR(255),
    FOREIGN KEY (drawn_for) REFERENCES Users(id)
);

CREATE TABLE Turns (
    round_id INT NOT NULL,
    user_id INT NOT NULL,
    image_id INT,
    prompt VARCHAR(255),
    working BIT,
    ready BIT,
    FOREIGN KEY (round_id) REFERENCES Rounds(id),
    FOREIGN KEY (user_id) REFERENCES Users(id),
    FOREIGN KEY (image_id) REFERENCES Images(id),
    PRIMARY KEY (round_id, user_id)
);
