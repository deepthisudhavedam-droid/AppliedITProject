import json
import sqlite3
import urllib.request
import urllib.error

print('Connecting to DB backend_dev.db...')
conn = sqlite3.connect('backend_dev.db')
cur = conn.cursor()
rows = cur.execute('SELECT id, username, email FROM users LIMIT 5').fetchall()
print('Users:', rows)


def post_json(url, payload):
    data = json.dumps(payload).encode('utf-8')
    headers = {'Content-Type': 'application/json', 'Origin': 'http://127.0.0.1:5500'}
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req) as resp:
            body = resp.read().decode('utf-8')
            print('POST', url, 'STATUS', resp.status)
            print('HEADERS', dict(resp.getheaders()))
            print('BODY', body)
    except urllib.error.HTTPError as e:
        print('POST', url, 'HTTP ERROR', e.code)
        print('HEADERS', dict(e.headers))
        print('BODY', e.read().decode('utf-8'))
    except Exception as e:
        print('POST', url, 'ERROR', type(e).__name__, e)

print('\nTesting /login with existing user credentials...')
post_json('http://127.0.0.1:8000/login', {'email': 'testuser@example.com', 'password': 'Test1234'})

print('\nTesting /register then /login with a new user...')
new_user = {
    'username': 'auto_test',
    'email': 'auto_test@example.com',
    'password': 'AutoTest123'
}
post_json('http://127.0.0.1:8000/register', new_user)
post_json('http://127.0.0.1:8000/login', {'email': new_user['email'], 'password': new_user['password']})
