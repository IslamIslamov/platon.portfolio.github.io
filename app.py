from flask import Flask, jsonify, request, render_template, session
import random
import os

app = Flask(__name__)
# Секретный ключ нужен для работы сессий (хранения счета)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-me")

# Данные для тренировки
TASKS = [
    {"word": "Девч_нка", "answer": "О"},
    {"word": "Медвеж_нок", "answer": "О"},
    {"word": "Крюч_к", "answer": "О"},
    {"word": "Ж_лтого", "answer": "Ё"},
    {"word": "Ш_пот", "answer": "Ё"},
    {"word": "Ут_нок", "answer": "О"},
    {"word": "Мыш_нок", "answer": "О"},
    {"word": "Обожж_нный", "answer": "Ё"},
    {"word": "Сраж_нный", "answer": "Ё"},
    {"word": "Реш_нный", "answer": "Ё"}
]

# --- Маршруты для фронтенда ---

@app.route('/')
def index():
    """Отдаем главную страницу"""
    return render_template('index.html')

# --- API Маршруты ---

@app.route('/api/start', methods=['GET'])
def start_game():
    """Начать новую игру"""
    session.clear() # Очищаем старую сессию
    session['score'] = 0
    session['used_tasks'] = []
    session['current_task'] = None
    return jsonify({
        'success': True,
        'total_tasks': len(TASKS)
    })

@app.route('/api/task', methods=['GET'])
def get_task():
    """Получить следующее задание"""
    used = session.get('used_tasks', [])
    # Фильтруем задачи, которых еще не было
    available = [t for t in TASKS if t not in used]
    
    if not available:
        return jsonify({
            'success': True,
            'finished': True,
            'score': session.get('score', 0),
            'total': len(TASKS)
        })
    
    task = random.choice(available)
    session['current_task'] = task
    
    # Обновляем список использованных
    if 'used_tasks' not in session:
        session['used_tasks'] = []
    session['used_tasks'].append(task)
    
    return jsonify({
        'success': True,
        'finished': False,
        'task': task,
        'progress': len(session['used_tasks']),
        'total': len(TASKS),
        'score': session.get('score', 0)
    })

@app.route('/api/answer', methods=['POST'])
def check_answer():
    """Проверить ответ"""
    data = request.json
    user_answer = data.get('answer')
    current_task = session.get('current_task')
    
    if not current_task:
        return jsonify({'success': False, 'error': 'No active task'}), 400
    
    is_correct = user_answer == current_task['answer']
    
    if is_correct:
        session['score'] = session.get('score', 0) + 1
    
    return jsonify({
        'success': True,
        'correct': is_correct,
        'correct_answer': current_task['answer'],
        'score': session.get('score', 0)
    })

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)