"""
╔════════════════════════════════════════════════════════════════╗
║           EVENTURA API - ПОЛНАЯ ДОКУМЕНТАЦИЯ                   ║
║        Flask + MongoDB для управления студентами               ║
╚════════════════════════════════════════════════════════════════╝
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime, timedelta
from functools import wraps
import random
import os

# ═══════════════════════════════════════════════════════════════
# КОНФИГУРАЦИЯ
# ═══════════════════════════════════════════════════════════════

app = Flask(__name__)
CORS(app)

# MongoDB подключение
MONGODB_URL = os.getenv('MONGODB_URL', 'mongodb+srv://gygg8574:Fn7gIIvxIoi7bpxm@cluster0.tz94fib.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
client = MongoClient(MONGODB_URL)
db = client.eventura

# Инициализация коллекций
collections = {
    'students': db.students,
    'colleges': db.colleges,
    'events': db.events,
    'ratings': db.ratings
}

# ═══════════════════════════════════════════════════════════════
# ИНИЦИАЛИЗАЦИЯ ДАННЫХ
# ═══════════════════════════════════════════════════════════════

def init_database():
    """Создает и заполняет базу данных"""
    
    # Очищаем старые данные
    for collection in collections.values():
        collection.delete_many({})
    
    # 1. Колледжи (42 колледжа)
    colleges = [
        {"id": i, "name": f"Колледж №{i}", "city": "РФ", "students_count": 0}
        for i in range(1, 43)
    ]
    collections['colleges'].insert_many(colleges)
    
    # 2. События (256 событий)
    events = [
        {
            "id": i,
            "name": f"Событие {i}",
            "date": datetime.now() - timedelta(days=random.randint(0, 365)),
            "college_id": random.randint(1, 42),
            "participants": random.randint(10, 500)
        }
        for i in range(1, 257)
    ]
    collections['events'].insert_many(events)
    
    # 3. Студенты (1627 студентов)
    names = [
        "Иван", "Алексей", "Мария", "Дмитрий", "Елена", "Николай",
        "Анна", "Сергей", "Ольга", "Михаил", "Татьяна", "Владимир",
        "Екатерина", "Андрей", "Вероника", "Константин", "Яна", "Павел"
    ]
    surnames = [
        "Петров", "Сидоров", "Иванов", "Козлов", "Смирнов", "Волков",
        "Кузнецов", "Морозов", "Попов", "Лебедев", "Новиков", "Орлов",
        "Соколов", "Юрьев", "Захаров", "Павлов", "Александров", "Святославов"
    ]
    
    students = []
    for i in range(1627):
        score = random.randint(50, 1500)
        students.append({
            "id": i + 1,
            "name": f"{random.choice(names)} {random.choice(surnames)}",
            "college_id": random.randint(1, 42),
            "score": score,
            "events_count": random.randint(1, 15),
            "rating": random.randint(1, 1627),
            "last_activity": datetime.now() - timedelta(days=random.randint(0, 90)),
            "joined_date": datetime.now() - timedelta(days=random.randint(30, 365))
        })
    
    # Сортируем по баллам и переассайним рейтинг
    students.sort(key=lambda x: x["score"], reverse=True)
    for idx, student in enumerate(students):
        student["rating"] = idx + 1
    
    collections['students'].insert_many(students)
    
    print("✅ База инициализирована:")
    print(f"   📚 Колледжей: {collections['colleges'].count_documents({})}")
    print(f"   🎓 Студентов: {collections['students'].count_documents({})}")
    print(f"   🎪 Событий: {collections['events'].count_documents({})}")

# ═══════════════════════════════════════════════════════════════
# УТИЛИТЫ
# ═══════════════════════════════════════════════════════════════

def serialize_document(doc):
    """Конвертирует ObjectId в строку"""
    if doc and '_id' in doc:
        doc['_id'] = str(doc['_id'])
    return doc

def serialize_documents(docs):
    """Конвертирует список документов"""
    return [serialize_document(doc) for doc in docs]

# ═══════════════════════════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════════════════════════

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📊 СТАТИСТИКА
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.route('/api/v1/stats', methods=['GET'])
def get_stats():
    """
    GET /api/v1/stats
    Получает общую статистику системы
    
    Ответ:
    {
        "events": 256,
        "students": 1627,
        "colleges": 42,
        "status": "healthy"
    }
    """
    return jsonify({
        "events": collections['events'].count_documents({}),
        "students": collections['students'].count_documents({}),
        "colleges": collections['colleges'].count_documents({}),
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/v1/stats/by-college', methods=['GET'])
def get_stats_by_college():
    """
    GET /api/v1/stats/by-college
    Получает статистику по каждому колледжу
    
    Ответ:
    {
        "colleges": [
            {
                "id": 1,
                "name": "Колледж №1",
                "students_count": 40,
                "events_count": 10,
                "total_score": 45200
            }
        ]
    }
    """
    pipeline = [
        {
            "$group": {
                "_id": "$college_id",
                "students_count": {"$sum": 1},
                "total_score": {"$sum": "$score"},
                "avg_score": {"$avg": "$score"}
            }
        }
    ]
    
    stats = list(collections['students'].aggregate(pipeline))
    
    for stat in stats:
        college = collections['colleges'].find_one({"id": stat["_id"]})
        stat["college_name"] = college["name"] if college else "Unknown"
        
        events = collections['events'].count_documents({"college_id": stat["_id"]})
        stat["events_count"] = events
    
    return jsonify({"colleges": stats})

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎓 СТУДЕНТЫ
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.route('/api/v1/students', methods=['GET'])
def get_students():
    """
    GET /api/v1/students?page=1&limit=20&college=1&period=month&sort=score
    Получает список студентов с фильтрацией и пагинацией
    
    Параметры:
    - page (int): номер страницы (default: 1)
    - limit (int): студентов на странице (default: 20, max: 100)
    - college (int): фильтр по колледжу (optional)
    - period (str): фильтр по периоду (all/week/month, default: all)
    - sort (str): сортировка (score/rating/name, default: score)
    
    Ответ:
    {
        "students": [...],
        "pagination": {
            "page": 1,
            "limit": 20,
            "total": 1627,
            "pages": 82
        }
    }
    """
    page = max(1, int(request.args.get('page', 1)))
    limit = min(100, int(request.args.get('limit', 20)))
    college = request.args.get('college', type=int)
    period = request.args.get('period', 'all')
    sort = request.args.get('sort', 'score')
    
    # Фильтр
    query = {}
    if college:
        query['college_id'] = college
    
    if period == 'week':
        query['last_activity'] = {'$gte': datetime.now() - timedelta(days=7)}
    elif period == 'month':
        query['last_activity'] = {'$gte': datetime.now() - timedelta(days=30)}
    
    # Сортировка
    sort_field = {'score': 'score', 'rating': 'rating', 'name': 'name'}.get(sort, 'score')
    sort_order = -1 if sort in ['score', 'rating'] else 1
    
    total = collections['students'].count_documents(query)
    
    students = list(
        collections['students'].find(query)
        .sort([(sort_field, sort_order)])
        .skip((page - 1) * limit)
        .limit(limit)
    )
    
    return jsonify({
        "students": serialize_documents(students),
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        }
    })

@app.route('/api/v1/students/top3', methods=['GET'])
def get_top3_students():
    """
    GET /api/v1/students/top3
    Получает топ-3 студентов
    
    Ответ:
    {
        "students": [
            {"rating": 1, "name": "...", "score": 1500, ...},
            {"rating": 2, "name": "...", "score": 1450, ...},
            {"rating": 3, "name": "...", "score": 1400, ...}
        ]
    }
    """
    top3 = list(
        collections['students'].find()
        .sort([('score', -1)])
        .limit(3)
    )
    
    return jsonify({"students": serialize_documents(top3)})

@app.route('/api/v1/students/<int:student_id>', methods=['GET'])
def get_student(student_id):
    """
    GET /api/v1/students/{id}
    Получает информацию о конкретном студенте
    
    Ответ:
    {
        "student": {
            "id": 1,
            "name": "Иван Петров",
            "college_id": 1,
            "score": 1234,
            "rating": 5,
            ...
        }
    }
    """
    student = collections['students'].find_one({"id": student_id})
    if not student:
        return jsonify({"error": "Student not found"}), 404
    
    return jsonify({"student": serialize_document(student)})

@app.route('/api/v1/students/search', methods=['POST'])
def search_students():
    """
    POST /api/v1/students/search
    Поиск студентов по имени
    
    Body:
    {
        "query": "Иван",
        "limit": 10
    }
    
    Ответ:
    {
        "results": [...]
    }
    """
    data = request.get_json()
    query = data.get('query', '')
    limit = int(data.get('limit', 10))
    
    results = list(
        collections['students'].find(
            {"name": {"$regex": query, "$options": "i"}}
        ).limit(limit)
    )
    
    return jsonify({"results": serialize_documents(results)})

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🏫 КОЛЛЕДЖИ
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.route('/api/v1/colleges', methods=['GET'])
def get_colleges():
    """
    GET /api/v1/colleges
    Получает список всех колледжей
    
    Ответ:
    {
        "colleges": [
            {"id": 1, "name": "Колледж №1", ...},
            ...
        ]
    }
    """
    colleges = list(collections['colleges'].find({}, {'_id': 0}).sort('id', 1))
    return jsonify({"colleges": colleges})

@app.route('/api/v1/colleges/<int:college_id>', methods=['GET'])
def get_college(college_id):
    """
    GET /api/v1/colleges/{id}
    Получает информацию о колледже и его студентов
    
    Ответ:
    {
        "college": {...},
        "students": [...],
        "stats": {
            "students_count": 40,
            "avg_score": 850
        }
    }
    """
    college = collections['colleges'].find_one({"id": college_id}, {'_id': 0})
    if not college:
        return jsonify({"error": "College not found"}), 404
    
    students = list(collections['students'].find({"college_id": college_id}))
    
    stats = {
        "students_count": len(students),
        "avg_score": sum(s["score"] for s in students) // len(students) if students else 0,
        "total_score": sum(s["score"] for s in students)
    }
    
    return jsonify({
        "college": college,
        "students": serialize_documents(students),
        "stats": stats
    })

@app.route('/api/v1/colleges/leaderboard', methods=['GET'])
def colleges_leaderboard():
    """
    GET /api/v1/colleges/leaderboard
    Лидерборд колледжей по среднему баллу
    
    Ответ:
    {
        "colleges": [
            {"id": 1, "name": "...", "avg_score": 900, "rank": 1, ...}
        ]
    }
    """
    pipeline = [
        {
            "$group": {
                "_id": "$college_id",
                "avg_score": {"$avg": "$score"},
                "students_count": {"$sum": 1},
                "total_score": {"$sum": "$score"}
            }
        },
        {"$sort": {"avg_score": -1}}
    ]
    
    results = list(collections['students'].aggregate(pipeline))
    
    for idx, result in enumerate(results):
        college = collections['colleges'].find_one({"id": result["_id"]})
        result["college_name"] = college["name"] if college else "Unknown"
        result["rank"] = idx + 1
    
    return jsonify({"colleges": results})

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎪 СОБЫТИЯ
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.route('/api/v1/events', methods=['GET'])
def get_events():
    """
    GET /api/v1/events?page=1&limit=20&college=1
    Получает список событий
    
    Параметры:
    - page (int): номер страницы
    - limit (int): событий на странице
    - college (int): фильтр по колледжу
    
    Ответ:
    {
        "events": [...],
        "pagination": {...}
    }
    """
    page = max(1, int(request.args.get('page', 1)))
    limit = min(100, int(request.args.get('limit', 20)))
    college = request.args.get('college', type=int)
    
    query = {}
    if college:
        query['college_id'] = college
    
    total = collections['events'].count_documents(query)
    
    events = list(
        collections['events'].find(query)
        .sort('date', -1)
        .skip((page - 1) * limit)
        .limit(limit)
    )
    
    return jsonify({
        "events": serialize_documents(events),
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        }
    })

@app.route('/api/v1/events/top', methods=['GET'])
def get_top_events():
    """
    GET /api/v1/events/top
    Получает топ события по количеству участников
    
    Ответ:
    {
        "events": [...]
    }
    """
    events = list(
        collections['events'].find()
        .sort('participants', -1)
        .limit(10)
    )
    
    return jsonify({"events": serialize_documents(events)})

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📋 РЕЙТИНГИ
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.route('/api/v1/ratings/global', methods=['GET'])
def get_global_rating():
    """
    GET /api/v1/ratings/global?page=1&limit=50
    Получает глобальный рейтинг студентов
    
    Параметры:
    - page (int): номер страницы
    - limit (int): студентов на странице
    
    Ответ:
    {
        "rating": [...],
        "pagination": {...}
    }
    """
    page = max(1, int(request.args.get('page', 1)))
    limit = min(100, int(request.args.get('limit', 50)))
    
    total = collections['students'].count_documents({})
    
    students = list(
        collections['students'].find()
        .sort('score', -1)
        .skip((page - 1) * limit)
        .limit(limit)
    )
    
    return jsonify({
        "rating": serialize_documents(students),
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        }
    })

@app.route('/api/v1/ratings/college/<int:college_id>', methods=['GET'])
def get_college_rating(college_id):
    """
    GET /api/v1/ratings/college/{id}?page=1&limit=50
    Получает рейтинг студентов по колледжу
    
    Ответ:
    {
        "college_rating": [...],
        "college_name": "..."
    }
    """
    college = collections['colleges'].find_one({"id": college_id})
    if not college:
        return jsonify({"error": "College not found"}), 404
    
    students = list(
        collections['students'].find({"college_id": college_id})
        .sort('score', -1)
    )
    
    return jsonify({
        "college_rating": serialize_documents(students),
        "college_name": college["name"]
    })

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔍 АНАЛИТИКА
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.route('/api/v1/analytics/distribution', methods=['GET'])
def get_score_distribution():
    """
    GET /api/v1/analytics/distribution
    Распределение студентов по количеству баллов
    
    Ответ:
    {
        "distribution": [
            {"range": "0-200", "count": 50},
            {"range": "200-400", "count": 100},
            ...
        ]
    }
    """
    pipeline = [
        {
            "$bucket": {
                "groupBy": "$score",
                "boundaries": [0, 200, 400, 600, 800, 1000, 1200, 1400, 1600],
                "default": "Other",
                "output": {"count": {"$sum": 1}}
            }
        }
    ]
    
    distribution = list(collections['students'].aggregate(pipeline))
    
    return jsonify({"distribution": distribution})

@app.route('/api/v1/analytics/top-by-college', methods=['GET'])
def get_top_by_college():
    """
    GET /api/v1/analytics/top-by-college
    Топ студент из каждого колледжа
    
    Ответ:
    {
        "top_by_college": [
            {"college": "Колледж №1", "student": "Иван", "score": 1500}
        ]
    }
    """
    pipeline = [
        {
            "$sort": {"score": -1}
        },
        {
            "$group": {
                "_id": "$college_id",
                "top_student": {"$first": "$$ROOT"}
            }
        },
        {
            "$project": {
                "college_id": "$_id",
                "student": "$top_student.name",
                "score": "$top_student.score"
            }
        }
    ]
    
    results = list(collections['students'].aggregate(pipeline))
    
    for result in results:
        college = collections['colleges'].find_one({"id": result["college_id"]})
        result["college_name"] = college["name"] if college else "Unknown"
    
    return jsonify({"top_by_college": results})

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🏥 ЗДОРОВЬЕ
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.route('/health', methods=['GET'])
def health_check():
    """
    GET /health
    Проверка состояния API
    
    Ответ:
    {
        "status": "healthy",
        "database": "connected",
        "collections": {...}
    }
    """
    return jsonify({
        "status": "healthy",
        "database": "connected",
        "timestamp": datetime.now().isoformat(),
        "collections": {
            "students": collections['students'].count_documents({}),
            "colleges": collections['colleges'].count_documents({}),
            "events": collections['events'].count_documents({})
        }
    })

@app.route('/api/v1/docs', methods=['GET'])
def api_docs():
    """
    GET /api/v1/docs
    Полная документация API
    """
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Eventura API Documentation</title>
        <style>
            body { font-family: 'Courier New', monospace; margin: 0; padding: 20px; background: #1e1e1e; color: #e0e0e0; }
            .endpoint { background: #2d2d2d; padding: 15px; margin: 10px 0; border-left: 4px solid #0f7; border-radius: 5px; }
            .method { color: #0f7; font-weight: bold; }
            .url { color: #87ceeb; }
            h1 { color: #0f7; border-bottom: 2px solid #0f7; padding-bottom: 10px; }
            h2 { color: #ffa500; margin-top: 30px; }
            pre { background: #1a1a1a; padding: 10px; border-radius: 3px; overflow-x: auto; }
            .version { color: #666; font-size: 12px; }
        </style>
    </head>
    <body>
        <h1>🚀 Eventura API Documentation</h1>
        <p class="version">API v1.0 | Flask + MongoDB</p>
        
        <h2>📊 Статистика</h2>
        <div class="endpoint">
            <span class="method">GET</span> <span class="url">/api/v1/stats</span>
            <p>Общая статистика системы</p>
        </div>
        <div class="endpoint">
            <span class="method">GET</span> <span class="url">/api/v1/stats/by-college</span>
            <p>Статистика по каждому колледжу</p>
        </div>
        
        <h2>🎓 Студенты</h2>
        <div class="endpoint">
            <span class="method">GET</span> <span class="url">/api/v1/students?page=1&limit=20&sort=score</span>
            <p>Список студентов с пагинацией и фильтрацией</p>
        </div>
        <div class="endpoint">
            <span class="method">GET</span> <span class="url">/api/v1/students/top3</span>
            <p>Топ-3 студента</p>
        </div>
        <div class="endpoint">
            <span class="method">GET</span> <span class="url">/api/v1/students/{id}</span>
            <p>Информация о конкретном студенте</p>
        </div>
        <div class="endpoint">
            <span class="method">POST</span> <span class="url">/api/v1/students/search</span>
            <p>Поиск студентов по имени</p>
        </div>
        
        <h2>🏫 Колледжи</h2>
        <div class="endpoint">
            <span class="method">GET</span> <span class="url">/api/v1/colleges</span>
            <p>Список всех колледжей (42 штуки)</p>
        </div>
        <div class="endpoint">
            <span class="method">GET</span> <span class="url">/api/v1/colleges/{id}</span>
            <p>Информация о колледже и его студентах</p>
        </div>
        <div class="endpoint">
            <span class="method">GET</span> <span class="url">/api/v1/colleges/leaderboard</span>
            <p>Лидерборд колледжей</p>
        </div>
        
        <h2>🎪 События</h2>
        <div class="endpoint">
            <span class="method">GET</span> <span class="url">/api/v1/events?page=1&limit=20</span>
            <p>Список событий (256 штук)</p>
        </div>
        <div class="endpoint">
            <span class="method">GET</span> <span class="url">/api/v1/events/top</span>
            <p>Топ события по участникам</p>
        </div>
        
        <h2>📋 Рейтинги</h2>
        <div class="endpoint">
            <span class="method">GET</span> <span class="url">/api/v1/ratings/global?page=1&limit=50</span>
            <p>Глобальный рейтинг студентов</p>
        </div>
        <div class="endpoint">
            <span class="method">GET</span> <span class="url">/api/v1/ratings/college/{id}</span>
            <p>Рейтинг студентов по колледжу</p>
        </div>
        
        <h2>📈 Аналитика</h2>
        <div class="endpoint">
            <span class="method">GET</span> <span class="url">/api/v1/analytics/distribution</span>
            <p>Распределение студентов по баллам</p>
        </div>
        <div class="endpoint">
            <span class="method">GET</span> <span class="url">/api/v1/analytics/top-by-college</span>
            <p>Топ студент из каждого колледжа</p>
        </div>
        
        <h2>🏥 Здоровье</h2>
        <div class="endpoint">
            <span class="method">GET</span> <span class="url">/health</span>
            <p>Проверка состояния API</p>
        </div>
    </body>
    </html>
    '''

# ═══════════════════════════════════════════════════════════════
# ERROR HANDLERS
# ═══════════════════════════════════════════════════════════════

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    init_database()
    
    print("╔════════════════════════════════════════════════════════════╗")
    print("║           EVENTURA API ЗАПУЩЕН                            ║")
    print("╠════════════════════════════════════════════════════════════╣")
    print("║  🌐 http://localhost:5000                                  ║")
    print("║  📖 http://localhost:5000/api/v1/docs (документация)       ║")
    print("║  💚 http://localhost:5000/health                           ║")
    print("╠════════════════════════════════════════════════════════════╣")
    print("║  📊 Статистика: 256 событий | 1627 студентов | 42 колледжа")
    print("╚════════════════════════════════════════════════════════════╝")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
