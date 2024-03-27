-- Use your database
USE chat_app;

-- Table structure for 'users'
CREATE TABLE IF NOT EXISTS users (
    username VARCHAR(255) PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL
);

-- Table structure for 'messages'
CREATE TABLE IF NOT EXISTS messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sender_username VARCHAR(255) NOT NULL,
    receiver_username VARCHAR(255) NOT NULL,
    message_text TEXT NOT NULL,
    time_sent DATETIME NOT NULL,
    FOREIGN KEY (sender_username) REFERENCES users(username),
    FOREIGN KEY (receiver_username) REFERENCES users(username)
);
