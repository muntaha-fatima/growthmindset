import streamlit as st
import pandas as pd
from datetime import datetime
import random
import requests
import sqlite3
import hashlib
from streamlit_extras.app_logo import add_logo
from streamlit_extras.badges import badge

# Page config
st.set_page_config(
    page_title="Growth Mindset App",
    page_icon="🧠",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        background-color: #4a148c;
        color: white;
    }
    .stButton>button:hover {
        background-color: #6a1b9a;
        color: white;
    }
    .success-message {
        padding: 1rem;
        background-color: #d4edda;
        color: #155724;
        border-radius: 4px;
        margin: 1rem 0;
    }
    .quote-box {
        padding: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .crown-button {
        position: fixed;
        top: 20px;
        right: 20px;
        background: linear-gradient(45deg, #FF416C, #FF4B2B);
        border-radius: 50%;
        width: 50px;
        height: 50px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        box-shadow: 0 4px 15px rgba(255, 75, 43, 0.4);
        transition: all 0.3s ease;
        z-index: 999999;
    }
    .crown-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 75, 43, 0.6);
    }
    .crown-button img {
        width: 28px;
        height: 28px;
        filter: brightness(0) invert(1);
    }
    .crown-badge {
        position: absolute;
        top: -5px;
        right: -5px;
        background: #4CAF50;
        color: white;
        border-radius: 50%;
        width: 20px;
        height: 20px;
        font-size: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 2px solid white;
    }
    .streamlit-footer {
        position: fixed;
        bottom: 20px;
        right: 20px;
        display: flex;
        align-items: center;
        background: white;
        padding: 10px 20px;
        border-radius: 100px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        z-index: 999999;
        cursor: pointer;
    }
    .streamlit-footer:hover {
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transform: translateY(-2px);
    }
    .streamlit-footer img {
        width: 30px;
        height: 30px;
        margin-right: 10px;
    }
    .divider {
        width: 1px;
        height: 20px;
        background: #ddd;
        margin: 0 10px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize database
def init_db():
    conn = sqlite3.connect('mindset.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS challenges
                 (id INTEGER PRIMARY KEY, user_id INTEGER, challenge_id INTEGER, completed_at TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS quiz_attempts
                 (id INTEGER PRIMARY KEY, user_id INTEGER, score FLOAT, taken_at TIMESTAMP)''')
    conn.commit()
    conn.close()

# Initialize session state
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'page' not in st.session_state:
    st.session_state.page = 'home'

# Authentication functions
def login_user(username, password):
    conn = sqlite3.connect('mindset.db')
    c = conn.cursor()
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    c.execute('SELECT id FROM users WHERE username=? AND password=?', (username, hashed_pw))
    result = c.fetchone()
    conn.close()
    if result:
        st.session_state.user_id = result[0]
        return True
    return False

def register_user(username, password):
    if not username or not password:
        return False, "Username and password are required"
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    
    conn = sqlite3.connect('mindset.db')
    c = conn.cursor()
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    try:
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_pw))
        conn.commit()
        conn.close()
        return True, "Registration successful!"
    except:
        conn.close()
        return False, "Username already exists"

# Navigation
with st.sidebar:
    st.title('🧠 Growth Mindset')
    if st.session_state.user_id:
        pages = ['Home', 'Challenges', 'Daily Motivation', 'Quiz']
        choice = st.selectbox('Navigate', pages, key='navigation')
        if st.button('Logout', key='logout'):
            st.session_state.user_id = None
            st.rerun()
    else:
        choice = st.radio('Select Option', ['Login', 'Register'], key='auth_choice')

# Main content
if not st.session_state.user_id:
    if choice == 'Login':
        st.title('Welcome Back! 👋')
        with st.form('login_form'):
            username = st.text_input('Username', key='login_username')
            password = st.text_input('Password', type='password', key='login_password')
            submit = st.form_submit_button('Login')
            if submit:
                if login_user(username, password):
                    st.success('Logged in successfully!')
                    st.rerun()
                else:
                    st.error('Invalid credentials')
    else:
        st.title('Create Account 📝')
        with st.form('register_form'):
            username = st.text_input('Username', key='register_username')
            password = st.text_input('Password', type='password', key='register_password')
            submit = st.form_submit_button('Register')
            if submit:
                success, message = register_user(username, password)
                if success:
                    st.success(message)
                else:
                    st.error(message)

else:
    if choice == 'Home':
        st.title('Welcome to Your Growth Journey 🌱')
        st.write("""
        A growth mindset is the belief that you can develop your abilities through dedication and hard work.
        Your basic qualities are things you can cultivate through effort.
        """)
        
        with st.expander("🎯 Key Principles"):
            st.write("""
            - 💪 Embrace challenges
            - 📝 Learn from criticism
            - 🌟 Find inspiration in others' success
            - 🔄 View effort as path to mastery
            """)

    elif choice == 'Challenges':
        st.title('Daily Challenges 💪')
        
        challenges = [
            {
                'id': 1,
                'title': 'Learn Something New',
                'description': 'Spend 30 minutes learning a completely new skill',
                'difficulty': 'Easy'
            },
            {
                'id': 2,
                'title': 'Face Your Fear',
                'description': 'Do one thing that scares you today',
                'difficulty': 'Medium'
            },
            {
                'id': 3,
                'title': 'Embrace Feedback',
                'description': 'Ask for constructive criticism and implement it',
                'difficulty': 'Hard'
            }
        ]

        cols = st.columns(3)
        for idx, challenge in enumerate(challenges):
            with cols[idx]:
                st.markdown(f"### {challenge['title']}")
                st.write(challenge['description'])
                st.markdown(f"**Difficulty:** _{challenge['difficulty']}_")
                if st.button('Complete ✅', key=f"btn_{challenge['id']}"):
                    conn = sqlite3.connect('mindset.db', 
                                         detect_types=sqlite3.PARSE_DECLTYPES | 
                                         sqlite3.PARSE_COLNAMES)
                    c = conn.cursor()
                    completed_at = datetime.now()
                    c.execute('''INSERT INTO challenges (user_id, challenge_id, completed_at)
                               VALUES (?, ?, ?)''', 
                            (st.session_state.user_id, challenge['id'], completed_at))
                    conn.commit()
                    conn.close()
                    st.success('Challenge completed! 🎉')

    elif choice == 'Daily Motivation':
        st.title('Daily Inspiration ⭐')
        
        try:
            response = requests.get('https://api.quotable.io/random?tags=inspirational')
            quote = response.json()
            with st.container():
                st.markdown(f"""
                <div class="quote-box">
                    <h3>"{quote['content']}"</h3>
                    <p>- {quote['author']}</p>
                </div>
                """, unsafe_allow_html=True)
        except:
            st.error('Failed to fetch quote. Please try again.')

        st.subheader('Success Story of the Day 🌟')
        stories = [
            "Sarah struggled with math but kept practicing. Now she's a data scientist!",
            "John failed his first business but learned and now runs a successful startup.",
            "Maria couldn't speak English 2 years ago. Today she's fluent!"
        ]
        st.info(random.choice(stories))

    elif choice == 'Quiz':
        st.title('Mindset Quiz 📝')
        
        questions = [
            {
                "question": "When facing a challenge, I usually:",
                "options": [
                    "Give up if it seems too hard",
                    "Try different approaches until I succeed",
                    "Only attempt it if I'm sure I can do it",
                    "See it as an opportunity to learn"
                ],
                "growth_indices": [1, 3]
            },
            {
                "question": "When I receive criticism, I:",
                "options": [
                    "Take it personally and feel discouraged",
                    "See it as a chance to improve",
                    "Ignore it completely",
                    "Use it to learn and grow"
                ],
                "growth_indices": [1, 3]
            },
            {
                "question": "I believe intelligence is:",
                "options": [
                    "Fixed from birth",
                    "Something that grows with effort",
                    "Determined by genetics",
                    "Developed through learning"
                ],
                "growth_indices": [1, 3]
            }
        ]

        if 'quiz_answers' not in st.session_state:
            st.session_state.quiz_answers = {}

        for i, q in enumerate(questions):
            st.write(f"**Question {i+1}:** {q['question']}")
            answer = st.radio(
                label=f"Select your answer for question {i+1}:",
                options=q['options'],
                key=f'q_{i}',
                label_visibility="collapsed"
            )
            st.session_state.quiz_answers[i] = q['options'].index(answer)
            st.markdown("---")

        if st.button('Submit Quiz 📊'):
            score = 0
            total_growth_answers = 0
            for i, q in enumerate(questions):
                if st.session_state.quiz_answers[i] in q['growth_indices']:
                    score += 1
                total_growth_answers += len(q['growth_indices'])
            
            percentage = (score / len(questions)) * 100
            
            conn = sqlite3.connect('mindset.db', 
                                 detect_types=sqlite3.PARSE_DECLTYPES | 
                                 sqlite3.PARSE_COLNAMES)
            c = conn.cursor()
            taken_at = datetime.now()
            c.execute('INSERT INTO quiz_attempts (user_id, score, taken_at) VALUES (?, ?, ?)',
                     (st.session_state.user_id, percentage, taken_at))
            conn.commit()
            conn.close()

            st.balloons()
            st.success(f'Your Growth Mindset Score: {percentage:.1f}% 🎉')
            
            if percentage >= 75:
                st.markdown("### Excellent! You show strong signs of a growth mindset! 🌟")
            elif percentage >= 50:
                st.markdown("### Good start! You're developing a growth mindset! 💪")
            else:
                st.markdown("### There's room to develop your growth mindset further! 🌱")

with st.sidebar:
    st.markdown("---")  # Separator line
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("👑", help="Premium Features"):
            st.toast("Premium features coming soon!", icon="👑")
    with col2:
        st.markdown("**Premium**")

if __name__ == '__main__':
    init_db()

st.markdown("""
<div class="crown-button">
    <img src="https://cdn-icons-png.flaticon.com/512/2611/2611703.png" />
    <div class="crown-badge">3</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="streamlit-footer">
    <a href="https://streamlit.io" target="_blank" style="text-decoration: none; color: inherit;">
        <img src="https://streamlit.io/images/brand/streamlit-mark-color.png">
        <span>host by seerat fatima</span>
    </a>
    <div class="divider"></div>
  
      

</div>
""", unsafe_allow_html=True) 