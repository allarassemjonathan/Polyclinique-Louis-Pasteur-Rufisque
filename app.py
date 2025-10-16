from flask import Flask, render_template, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import os

app = Flask(__name__)
DATABASE_URL= os.getenv("DATABASE_URL")

# Get database connection
def get_db_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


# Initialize database table
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Create publications table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS publications (
            id SERIAL PRIMARY KEY,
            title VARCHAR(500) NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    cur.close()
    conn.close()
    print("Database initialized successfully!")

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/api/publications', methods=['GET'])
def get_publications():
    try:
        init_db()
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute('''
            SELECT id, title, content, created_at 
            FROM publications 
            ORDER BY created_at DESC
        ''')
        
        publications = cur.fetchall()
        cur.close()
        conn.close()
        
        # Format dates
        formatted_pubs = []
        for pub in publications:
            formatted_pubs.append({
                'id': pub['id'],
                'title': pub['title'],
                'content': pub['content'],
                'created_at': pub['created_at'].strftime('%d %B %Y')
            })
        
        return jsonify(formatted_pubs)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/publications', methods=['POST'])
def create_publication():
    try:
        init_db()
        data = request.json
        
        # Verify password
        if data.get('password') != 'post':
            return jsonify({'error': 'Mot de passe invalide'}), 401
        
        # Validate input
        if not data.get('title') or not data.get('content'):
            return jsonify({'error': 'Titre et contenu requis'}), 400
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Insert new publication
        cur.execute('''
            INSERT INTO publications (title, content)
            VALUES (%s, %s)
            RETURNING id, title, content, created_at
        ''', (data.get('title'), data.get('content')))
        
        new_pub = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        
        # Format response
        result = {
            'id': new_pub['id'],
            'title': new_pub['title'],
            'content': new_pub['content'],
            'created_at': new_pub['created_at'].strftime('%d %B %Y')
        }
        
        print(result, 'result')
        return jsonify(result), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Initialize database on first run
    try:
        init_db()
    except Exception as e:
        print(f"Database initialization error: {e}")
    
    app.run(debug=True)