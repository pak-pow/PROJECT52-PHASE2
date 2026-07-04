CREATE TABLE IF NOT EXISTS quizzes (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    title               TEXT NOT NULL,
    description         TEXT,
    category            TEXT NOT NULL,
    time_limit_seconds  INTEGER NOT NULL DEFAULT 60
);

CREATE TABLE IF NOT EXISTS questions (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    quiz_id              INTEGER NOT NULL,
    question_text        TEXT NOT NULL,
    options              TEXT NOT NULL,
    correct_option_index INTEGER NOT NULL,
    FOREIGN KEY (quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS leaderboard (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    quiz_id             INTEGER NOT NULL,
    username            TEXT NOT NULL,
    score               INTEGER NOT NULL,
    time_taken_seconds  INTEGER NOT NULL,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE
);

INSERT OR IGNORE INTO quizzes (id, title, description, category, time_limit_seconds)
VALUES (1, 'Web Development Basics', 'Test your knowledge of HTML, CSS, and JavaScript fundamentals.', 'Web Dev', 60);

INSERT OR IGNORE INTO quizzes (id, title, description, category, time_limit_seconds)
VALUES (2, 'Python Programming Trivia', 'How well do you know Python? Cover syntax, types, and idioms.', 'Python', 90);

INSERT OR IGNORE INTO questions (quiz_id, question_text, options, correct_option_index)
VALUES (1, 'What does HTML stand for?', '["HyperText Markup Language","HighText Machine Language","HyperText and links Markup Language","None of the above"]', 0);

INSERT OR IGNORE INTO questions (quiz_id, question_text, options, correct_option_index)
VALUES (1, 'Which CSS property controls the text size?', '["font-size","text-size","font-style","text-style"]', 0);

INSERT OR IGNORE INTO questions (quiz_id, question_text, options, correct_option_index)
VALUES (1, 'Which JavaScript keyword declares a block-scoped variable?', '["var","let","define","set"]', 1);

INSERT OR IGNORE INTO questions (quiz_id, question_text, options, correct_option_index)
VALUES (1, 'What is the correct HTML element for the largest heading?', '["<h6>","<heading>","<h1>","<head>"]', 2);

INSERT OR IGNORE INTO questions (quiz_id, question_text, options, correct_option_index)
VALUES (1, 'Which event fires when a user clicks an element?', '["onhover","onclick","onpress","onselect"]', 1);

INSERT OR IGNORE INTO questions (quiz_id, question_text, options, correct_option_index)
VALUES (2, 'What data type is the result of: 3 / 2 in Python 3?', '["int","float","double","str"]', 1);

INSERT OR IGNORE INTO questions (quiz_id, question_text, options, correct_option_index)
VALUES (2, 'Which keyword is used to define a function in Python?', '["function","def","fun","define"]', 1);

INSERT OR IGNORE INTO questions (quiz_id, question_text, options, correct_option_index)
VALUES (2, 'What is the output of: bool(0)?', '["True","False","None","0"]', 1);

INSERT OR IGNORE INTO questions (quiz_id, question_text, options, correct_option_index)
VALUES (2, 'Which built-in function returns the length of an object?', '["size()","count()","len()","length()"]', 2);

INSERT OR IGNORE INTO questions (quiz_id, question_text, options, correct_option_index)
VALUES (2, 'What symbol is used for single-line comments in Python?', '["//","--","#","/*"]', 2);