import sqlite3
import json
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

print('--- Existing users ---')
conn = sqlite3.connect('backend_dev.db')
cur = conn.cursor()
for row in cur.execute('SELECT id, username, email, password FROM users LIMIT 5'):
    print(row)

existing_email = 'testuser@example.com'
existing_password = 'Test1234'
cur.execute('SELECT password FROM users WHERE email = ?', (existing_email,))
row = cur.fetchone()
if row:
    stored_password = row[0]
    print('\nPassword verify for', existing_email, stored_password == existing_password)
else:
    print('\nNo such user found for verify check.')

print('\n--- API tests ---')
register_data = {'username': 'debugtest', 'email': 'debugtest@example.com', 'password': 'DebugTest123'}
resp = client.post('/register', json=register_data)
print('register', resp.status_code, resp.text)

login_data = {'email': register_data['email'], 'password': register_data['password']}
resp = client.post('/login', json=login_data)
print('login new user', resp.status_code, resp.text)

resp = client.post('/login', json={'email': existing_email, 'password': existing_password})
print('login existing user', resp.status_code, resp.text)
