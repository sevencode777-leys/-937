
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import secrets
import json
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Database initialization
def init_db():
    conn = sqlite3.connect('islamic_app.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            user_type TEXT NOT NULL,
            student_code TEXT UNIQUE,
            teacher_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (teacher_id) REFERENCES users (id)
        )
    ''')
    
    # Lessons table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lessons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            content TEXT,
            video_url TEXT,
            topic TEXT,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
    ''')
    
    # Quiz questions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quiz_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lesson_id INTEGER,
            question TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            FOREIGN KEY (lesson_id) REFERENCES lessons (id)
        )
    ''')
    
    # Student progress table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS student_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            lesson_id INTEGER,
            quiz_score INTEGER,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES users (id),
            FOREIGN KEY (lesson_id) REFERENCES lessons (id)
        )
    ''')
    
    # Quran progress table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quran_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            page_number INTEGER,
            memorized TEXT DEFAULT 'false',
            read_count INTEGER DEFAULT 0,
            last_read TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES users (id)
        )
    ''')
    
    # Chat messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_id TEXT,
            sender_id INTEGER,
            message TEXT,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sender_id) REFERENCES users (id)
        )
    ''')
    
    # Live sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS live_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id INTEGER,
            title TEXT,
            description TEXT,
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            is_active BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (teacher_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# User type codes
USER_CODES = {
    'developer': '3457',        # ليث المطور
    'main_teacher': '7777',     # الأستاذ معتصم
    'teacher': '08208888',      # الأساتذة
    'vip': 'sadik77'           # الأصدقاء والأقارب
}

def generate_student_code():
    return secrets.token_hex(4).upper()

def get_user_type_from_code(code):
    for user_type, stored_code in USER_CODES.items():
        if code == stored_code:
            return user_type
    return 'student'

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('islamic_app.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, password_hash, user_type FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['user_type'] = user[3]
            return redirect(url_for('dashboard'))
        else:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        special_code = request.form.get('special_code', '')
        
        user_type = get_user_type_from_code(special_code)
        student_code = generate_student_code() if user_type == 'student' else None
        
        password_hash = generate_password_hash(password)
        
        conn = sqlite3.connect('islamic_app.db')
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users (username, password_hash, user_type, student_code)
                VALUES (?, ?, ?, ?)
            ''', (username, password_hash, user_type, student_code))
            conn.commit()
            
            user_id = cursor.lastrowid
            session['user_id'] = user_id
            session['username'] = username
            session['user_type'] = user_type
            
            if student_code:
                flash(f'تم إنشاء حسابك بنجاح. رمز الطالب الخاص بك هو: {student_code}')
            
            conn.close()
            return redirect(url_for('dashboard'))
            
        except sqlite3.IntegrityError:
            flash('اسم المستخدم موجود بالفعل')
            conn.close()
    
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_type = session.get('user_type')
    return render_template('dashboard.html', user_type=user_type)

@app.route('/lessons')
def lessons():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('islamic_app.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM lessons ORDER BY created_at DESC')
    lessons = cursor.fetchall()
    conn.close()
    
    return render_template('lessons.html', lessons=lessons)

@app.route('/lesson/<int:lesson_id>')
def lesson_detail(lesson_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('islamic_app.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM lessons WHERE id = ?', (lesson_id,))
    lesson = cursor.fetchone()
    
    cursor.execute('SELECT * FROM quiz_questions WHERE lesson_id = ?', (lesson_id,))
    questions = cursor.fetchall()
    conn.close()
    
    return render_template('lesson_detail.html', lesson=lesson, questions=questions)

@app.route('/quran')
def quran():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('quran.html')

@app.route('/chat')
def chat():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('chat.html')

@app.route('/admin')
def admin():
    if 'user_id' not in session or session.get('user_type') not in ['developer', 'main_teacher', 'teacher']:
        return redirect(url_for('dashboard'))
    
    return render_template('admin.html')

@app.route('/live_session')
def live_session():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('live_session.html')

# API endpoints
@app.route('/api/track_quran_progress', methods=['POST'])
def track_quran_progress():
    if 'user_id' not in session:
        return jsonify({'error': 'غير مسموح'}), 401
    
    data = request.get_json()
    page_number = data.get('page_number')
    action = data.get('action')
    
    conn = sqlite3.connect('islamic_app.db')
    cursor = conn.cursor()
    
    # Check if record exists
    cursor.execute('SELECT id, read_count FROM quran_progress WHERE student_id = ? AND page_number = ?', 
                   (session['user_id'], page_number))
    existing = cursor.fetchone()
    
    if existing:
        if action == 'read':
            cursor.execute('UPDATE quran_progress SET read_count = read_count + 1, last_read = ? WHERE id = ?',
                          (datetime.now(), existing[0]))
        elif action == 'memorized':
            cursor.execute('UPDATE quran_progress SET memorized = "true" WHERE id = ?', (existing[0],))
    else:
        memorized = 'true' if action == 'memorized' else 'false'
        read_count = 1 if action == 'read' else 0
        cursor.execute('''INSERT INTO quran_progress (student_id, page_number, memorized, read_count) 
                         VALUES (?, ?, ?, ?)''', (session['user_id'], page_number, memorized, read_count))
    
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/save_quiz_results', methods=['POST'])
def save_quiz_results():
    if 'user_id' not in session:
        return jsonify({'error': 'غير مسموح'}), 401
    
    data = request.get_json()
    lesson_id = data.get('lesson_id')
    score = data.get('score')
    
    conn = sqlite3.connect('islamic_app.db')
    cursor = conn.cursor()
    
    cursor.execute('''INSERT INTO student_progress (student_id, lesson_id, quiz_score) 
                     VALUES (?, ?, ?)''', (session['user_id'], lesson_id, score))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'تم حفظ النتيجة'})

@app.route('/api/mark_lesson_completed', methods=['POST'])
def mark_lesson_completed():
    if 'user_id' not in session:
        return jsonify({'error': 'غير مسموح'}), 401
    
    data = request.get_json()
    lesson_id = data.get('lesson_id')
    
    conn = sqlite3.connect('islamic_app.db')
    cursor = conn.cursor()
    
    # Check if already completed
    cursor.execute('SELECT id FROM student_progress WHERE student_id = ? AND lesson_id = ?', 
                   (session['user_id'], lesson_id))
    existing = cursor.fetchone()
    
    if not existing:
        cursor.execute('''INSERT INTO student_progress (student_id, lesson_id, quiz_score) 
                         VALUES (?, ?, ?)''', (session['user_id'], lesson_id, 100))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/dashboard_stats')
def dashboard_stats():
    if 'user_id' not in session:
        return jsonify({'error': 'غير مسموح'}), 401
    
    conn = sqlite3.connect('islamic_app.db')
    cursor = conn.cursor()
    
    # Get completed lessons count
    cursor.execute('SELECT COUNT(*) FROM student_progress WHERE student_id = ?', (session['user_id'],))
    lessons_completed = cursor.fetchone()[0]
    
    # Get Quran pages read
    cursor.execute('SELECT COUNT(*) FROM quran_progress WHERE student_id = ? AND read_count > 0', (session['user_id'],))
    quran_pages_read = cursor.fetchone()[0]
    
    # Get quiz average
    cursor.execute('SELECT AVG(quiz_score) FROM student_progress WHERE student_id = ? AND quiz_score IS NOT NULL', 
                   (session['user_id'],))
    quiz_avg = cursor.fetchone()[0] or 0
    
    conn.close()
    
    return jsonify({
        'lessons_completed': lessons_completed,
        'quran_pages_read': quran_pages_read,
        'quiz_average': round(quiz_avg, 1),
        'attendance_days': 22  # This would be calculated based on login history
    })

@app.route('/api/connect_to_teacher', methods=['POST'])
def connect_to_teacher():
    if 'user_id' not in session:
        return jsonify({'error': 'غير مسموح'}), 401
    
    data = request.get_json()
    student_code = data.get('student_code')
    
    conn = sqlite3.connect('islamic_app.db')
    cursor = conn.cursor()
    
    # Find student by code
    cursor.execute('SELECT id FROM users WHERE student_code = ? AND user_type = "student"', (student_code,))
    student = cursor.fetchone()
    
    if not student:
        return jsonify({'success': False, 'message': 'رمز الطالب غير صحيح'})
    
    # Connect student to teacher
    cursor.execute('UPDATE users SET teacher_id = ? WHERE id = ?', (session['user_id'], student[0]))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'تم ربط الطالب بنجاح'})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# Initialize sample data
def init_sample_data():
    conn = sqlite3.connect('islamic_app.db')
    cursor = conn.cursor()
    
    # Check if lessons already exist
    cursor.execute('SELECT COUNT(*) FROM lessons')
    if cursor.fetchone()[0] == 0:
        # Add sample lessons
        sample_lessons = [
            ('أركان الإسلام الخمسة', 'تعلم عن الأركان الخمسة للإسلام وأهميتها', 'هذا الدرس يغطي الأركان الخمسة للإسلام...', '', 'عقيدة', 1),
            ('الصلاة وأحكامها', 'دراسة شاملة لأحكام الصلاة وشروطها', 'تعرف على أحكام الصلاة...', '', 'فقه', 1),
            ('السيرة النبوية', 'حياة النبي محمد صلى الله عليه وسلم', 'دراسة السيرة النبوية...', '', 'سيرة', 1),
            ('الحديث الشريف', 'دراسة الأحاديث النبوية وعلومها', 'تعلم علوم الحديث...', '', 'حديث', 1),
            ('التفسير', 'فهم معاني القرآن الكريم', 'دراسة تفسير القرآن...', '', 'تفسير', 1)
        ]
        
        for lesson in sample_lessons:
            cursor.execute('''INSERT INTO lessons (title, description, content, video_url, topic, created_by) 
                             VALUES (?, ?, ?, ?, ?, ?)''', lesson)
        
        # Add sample quiz questions
        for lesson_id in range(1, 6):
            for i in range(50):
                cursor.execute('''INSERT INTO quiz_questions 
                                 (lesson_id, question, option_a, option_b, option_c, option_d, correct_answer) 
                                 VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                              (lesson_id, f'ما هو السؤال رقم {i+1}؟', 'الخيار الأول', 'الخيار الثاني', 'الخيار الثالث', 'الخيار الرابع', 'a'))
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    init_sample_data()
    app.run(host='0.0.0.0', port=5000, debug=True)
