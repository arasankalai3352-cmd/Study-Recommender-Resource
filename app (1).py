from flask import Flask, render_template, request, jsonify
from model.recommender import StudyRecommender
import json
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Initialize recommender
recommender = StudyRecommender('data/resources.csv')
HISTORY_FILE = 'user_history.json'

# ======================== HISTORY FUNCTIONS ========================
def save_history(query, results):
    """Save search history"""
    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            history = json.load(f)
    
    entry = {
        'query': query,
        'results': [r['title'] for r in results],
        'timestamp': str(__import__('datetime').datetime.now())
    }
    history.append(entry)
    
    if len(history) > 20:
        history = history[-20:]
    
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

def get_history():
    """Get search history"""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    return []

# ======================== ROUTES ========================
@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    query = ""
    difficulty = "All"
    history = get_history()
    quiz = recommender.get_quiz()
    
    if request.method == 'POST':
        query = request.form.get('query', '')
        difficulty = request.form.get('difficulty', 'All')
        
        # Get recommendations
        results = recommender.recommend(query, difficulty_filter=difficulty)
        
        # Save to history
        if results:
            save_history(query, results)
        
        # Get new quiz
        quiz = recommender.get_quiz()
    
    categories = recommender.get_categories()
    difficulties = recommender.get_difficulties()
    
    return render_template('index.html', 
                         results=results, 
                         query=query,
                         difficulty=difficulty,
                         categories=categories,
                         difficulties=difficulties,
                         quiz=quiz,
                         history=history)

@app.route('/rate', methods=['POST'])
def rate_resource():
    """Rating system"""
    data = request.json
    title = data.get('title')
    rating = data.get('rating')
    
    # Update CSV
    recommender.update_rating(title, rating)
    
    return jsonify({'status': 'success', 'message': f'Rated {title} as {rating}/5'})

if __name__ == '__main__':
    app.run(debug=True, port=5001)