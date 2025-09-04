
// Theme management
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    // Update icon
    const icon = document.querySelector('.fa-moon');
    if (icon) {
        icon.className = newTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    }
}

// Load saved theme
document.addEventListener('DOMContentLoaded', function() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    
    // Update icon
    const icon = document.querySelector('.fa-moon');
    if (icon) {
        icon.className = savedTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    }
});

// Notification system
function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

// Live session functionality
class LiveSession {
    constructor() {
        this.isActive = false;
        this.participants = [];
        this.whiteboard = null;
        this.drawing = false;
    }
    
    startSession() {
        this.isActive = true;
        showNotification('تم بدء الجلسة المباشرة', 'success');
        this.initializeWhiteboard();
    }
    
    endSession() {
        this.isActive = false;
        showNotification('تم إنهاء الجلسة المباشرة', 'info');
    }
    
    initializeWhiteboard() {
        const canvas = document.getElementById('whiteboard');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        this.whiteboard = { canvas, ctx };
        
        let isDrawing = false;
        let lastX = 0;
        let lastY = 0;
        
        canvas.addEventListener('mousedown', (e) => {
            isDrawing = true;
            [lastX, lastY] = [e.offsetX, e.offsetY];
        });
        
        canvas.addEventListener('mousemove', (e) => {
            if (!isDrawing) return;
            
            ctx.beginPath();
            ctx.moveTo(lastX, lastY);
            ctx.lineTo(e.offsetX, e.offsetY);
            ctx.strokeStyle = '#2563eb';
            ctx.lineWidth = 2;
            ctx.lineCap = 'round';
            ctx.stroke();
            
            [lastX, lastY] = [e.offsetX, e.offsetY];
        });
        
        canvas.addEventListener('mouseup', () => isDrawing = false);
        canvas.addEventListener('mouseout', () => isDrawing = false);
    }
    
    clearWhiteboard() {
        if (this.whiteboard) {
            this.whiteboard.ctx.clearRect(0, 0, this.whiteboard.canvas.width, this.whiteboard.canvas.height);
        }
    }
}

// Chat functionality
class ChatSystem {
    constructor() {
        this.messages = [];
        this.currentRoom = 'general';
    }
    
    sendMessage(message, userType = 'student') {
        const messageObj = {
            id: Date.now(),
            text: message,
            sender: 'أنت',
            timestamp: new Date(),
            type: userType
        };
        
        this.messages.push(messageObj);
        this.displayMessage(messageObj);
        
        // Simulate response (in real app, this would be via WebSocket)
        if (userType === 'student') {
            setTimeout(() => {
                const response = {
                    id: Date.now() + 1,
                    text: 'شكراً لك على المشاركة',
                    sender: 'الأستاذ',
                    timestamp: new Date(),
                    type: 'teacher'
                };
                this.messages.push(response);
                this.displayMessage(response);
            }, 1000);
        }
    }
    
    displayMessage(message) {
        const chatContainer = document.getElementById('chatMessages');
        if (!chatContainer) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${message.type === 'teacher' ? 'teacher' : (message.sender === 'أنت' ? 'sent' : 'received')}`;
        messageDiv.innerHTML = `
            <div class="message-header">
                <strong>${message.sender}</strong>
                <small class="text-muted">${message.timestamp.toLocaleTimeString('ar-SA')}</small>
            </div>
            <div class="message-text">${message.text}</div>
        `;
        
        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
}

// Quran functionality
class QuranReader {
    constructor() {
        this.currentPage = 1;
        this.totalPages = 604;
        this.audio = null;
        this.isPlaying = false;
    }
    
    loadPage(pageNumber) {
        this.currentPage = pageNumber;
        this.trackPageRead(pageNumber);
        // In real implementation, load actual Quran text
        document.getElementById('quranText').innerHTML = `
            <div class="quran-page">
                <h4 class="text-center mb-4">صفحة ${pageNumber}</h4>
                <p>بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ</p>
                <p>هذه صفحة تجريبية من القرآن الكريم. في التطبيق الحقيقي، سيتم تحميل النص الفعلي للقرآن.</p>
            </div>
        `;
        
        showNotification(`تم تحميل صفحة ${pageNumber}`, 'info');
    }
    
    trackPageRead(pageNumber) {
        // Send to server to track progress
        fetch('/api/track_quran_progress', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                page_number: pageNumber,
                action: 'read'
            })
        });
    }
    
    markAsMemorized(pageNumber) {
        fetch('/api/track_quran_progress', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                page_number: pageNumber,
                action: 'memorized'
            })
        });
        
        showNotification(`تم تحديد صفحة ${pageNumber} كمحفوظة`, 'success');
    }
    
    playAudio(surahNumber) {
        if (this.audio) {
            this.audio.pause();
        }
        
        // In real implementation, use actual audio URLs
        this.audio = new Audio(`/static/audio/mishary_${surahNumber}.mp3`);
        this.audio.play().catch(() => {
            showNotification('عذراً، لا يمكن تشغيل الصوت حالياً', 'warning');
        });
        
        this.isPlaying = true;
        this.updateAudioControls();
    }
    
    pauseAudio() {
        if (this.audio) {
            this.audio.pause();
            this.isPlaying = false;
            this.updateAudioControls();
        }
    }
    
    updateAudioControls() {
        const playBtn = document.getElementById('playBtn');
        const pauseBtn = document.getElementById('pauseBtn');
        
        if (playBtn && pauseBtn) {
            playBtn.style.display = this.isPlaying ? 'none' : 'inline-block';
            pauseBtn.style.display = this.isPlaying ? 'inline-block' : 'none';
        }
    }
}

// Quiz functionality
class QuizSystem {
    constructor() {
        this.currentQuestion = 0;
        this.score = 0;
        this.answers = [];
        this.timeRemaining = 0;
        this.timer = null;
    }
    
    startQuiz(questions) {
        this.questions = questions;
        this.currentQuestion = 0;
        this.score = 0;
        this.answers = [];
        this.timeRemaining = questions.length * 120; // 2 minutes per question
        
        this.displayQuestion();
        this.startTimer();
    }
    
    displayQuestion() {
        const question = this.questions[this.currentQuestion];
        const quizContainer = document.getElementById('quizContainer');
        
        if (!quizContainer || !question) return;
        
        quizContainer.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <h5>السؤال ${this.currentQuestion + 1} من ${this.questions.length}</h5>
                    <div class="progress">
                        <div class="progress-bar" style="width: ${((this.currentQuestion + 1) / this.questions.length) * 100}%"></div>
                    </div>
                </div>
                <div class="card-body">
                    <h6>${question.question}</h6>
                    <div class="mt-3">
                        <div class="form-check mb-2">
                            <input class="form-check-input" type="radio" name="answer" value="a" id="option_a">
                            <label class="form-check-label" for="option_a">${question.option_a}</label>
                        </div>
                        <div class="form-check mb-2">
                            <input class="form-check-input" type="radio" name="answer" value="b" id="option_b">
                            <label class="form-check-label" for="option_b">${question.option_b}</label>
                        </div>
                        <div class="form-check mb-2">
                            <input class="form-check-input" type="radio" name="answer" value="c" id="option_c">
                            <label class="form-check-label" for="option_c">${question.option_c}</label>
                        </div>
                        <div class="form-check mb-2">
                            <input class="form-check-input" type="radio" name="answer" value="d" id="option_d">
                            <label class="form-check-label" for="option_d">${question.option_d}</label>
                        </div>
                    </div>
                    <div class="mt-3">
                        <button class="btn btn-primary" onclick="quiz.nextQuestion()">
                            ${this.currentQuestion === this.questions.length - 1 ? 'إنهاء الاختبار' : 'السؤال التالي'}
                        </button>
                    </div>
                    <div class="mt-2">
                        <small class="text-muted">الوقت المتبقي: <span id="timeRemaining">${this.formatTime(this.timeRemaining)}</span></small>
                    </div>
                </div>
            </div>
        `;
    }
    
    nextQuestion() {
        const selectedAnswer = document.querySelector('input[name="answer"]:checked');
        
        if (!selectedAnswer) {
            showNotification('يرجى اختيار إجابة', 'warning');
            return;
        }
        
        const question = this.questions[this.currentQuestion];
        const isCorrect = selectedAnswer.value === question.correct_answer;
        
        this.answers.push({
            question: this.currentQuestion,
            answer: selectedAnswer.value,
            correct: isCorrect
        });
        
        if (isCorrect) {
            this.score++;
        }
        
        this.currentQuestion++;
        
        if (this.currentQuestion >= this.questions.length) {
            this.finishQuiz();
        } else {
            this.displayQuestion();
        }
    }
    
    finishQuiz() {
        clearInterval(this.timer);
        
        const percentage = Math.round((this.score / this.questions.length) * 100);
        const quizContainer = document.getElementById('quizContainer');
        
        quizContainer.innerHTML = `
            <div class="card text-center">
                <div class="card-body">
                    <h3 class="text-success">انتهى الاختبار!</h3>
                    <h4>نتيجتك: ${this.score} من ${this.questions.length}</h4>
                    <h5 class="text-primary">${percentage}%</h5>
                    <div class="mt-3">
                        ${percentage >= 80 ? 
                            '<div class="alert alert-success">ممتاز! لقد نجحت بامتياز</div>' :
                            percentage >= 60 ?
                            '<div class="alert alert-warning">جيد! يمكنك تحسين نتيجتك</div>' :
                            '<div class="alert alert-danger">يرجى مراجعة الدرس والمحاولة مرة أخرى</div>'
                        }
                    </div>
                    <button class="btn btn-primary" onclick="window.location.reload()">
                        إعادة الاختبار
                    </button>
                </div>
            </div>
        `;
        
        // Save results to server
        this.saveQuizResults(percentage);
    }
    
    saveQuizResults(percentage) {
        fetch('/api/save_quiz_results', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                lesson_id: window.currentLessonId || 1,
                score: percentage,
                answers: this.answers
            })
        });
    }
    
    startTimer() {
        this.timer = setInterval(() => {
            this.timeRemaining--;
            const timeElement = document.getElementById('timeRemaining');
            
            if (timeElement) {
                timeElement.textContent = this.formatTime(this.timeRemaining);
            }
            
            if (this.timeRemaining <= 0) {
                this.finishQuiz();
            }
        }, 1000);
    }
    
    formatTime(seconds) {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
    }
}

// Initialize global objects
let liveSession = new LiveSession();
let chatSystem = new ChatSystem();
let quranReader = new QuranReader();
let quiz = new QuizSystem();

// Utility functions
function connectToTeacher(studentCode) {
    fetch('/api/connect_to_teacher', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            student_code: studentCode
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('تم ربطك بالأستاذ بنجاح', 'success');
        } else {
            showNotification('خطأ في الربط: ' + data.message, 'danger');
        }
    });
}

function loadDashboardStats() {
    fetch('/api/dashboard_stats')
    .then(response => response.json())
    .then(data => {
        // Update dashboard with real data
        updateDashboardCards(data);
    });
}

function updateDashboardCards(stats) {
    // Update various dashboard elements with real statistics
    const elements = {
        'lessons-completed': stats.lessons_completed || 0,
        'quran-pages-read': stats.quran_pages_read || 0,
        'quiz-average': stats.quiz_average || 0,
        'attendance-days': stats.attendance_days || 0
    };
    
    Object.entries(elements).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    });
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize any page-specific functionality
    const currentPage = window.location.pathname;
    
    if (currentPage.includes('/dashboard')) {
        loadDashboardStats();
    }
    
    // Add smooth scrolling to all anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        setTimeout(() => {
            card.classList.add('fade-in-up');
        }, index * 100);
    });
});
