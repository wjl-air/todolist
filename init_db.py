import pymysql

conn = pymysql.connect(host='localhost', user='root', password='root', charset='utf8mb4')
cursor = conn.cursor()
cursor.execute('CREATE DATABASE IF NOT EXISTS `1111` DEFAULT CHARACTER SET utf8mb4')
cursor.execute('USE `1111`')
cursor.execute('''CREATE TABLE IF NOT EXISTS todos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    completed TINYINT(1) DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)''')
conn.commit()
cursor.close()
conn.close()
print('Database and table created successfully')
