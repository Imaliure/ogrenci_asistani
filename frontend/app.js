const API_URL = "http://127.0.0.1:8000";

function addMessage(text, sender, extraHtml = "") {
    const chatBox = document.getElementById("chatBox");

    let msg = document.createElement("div");
    msg.classList.add("message", sender);
    msg.innerHTML = text + extraHtml;

    chatBox.appendChild(msg);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Sorulan teknik sorular listesi
let askedQuestions = [];

// --------------------------------------------------------------
// SORU GÖNDERME (Tek, Doğru Sürüm)
// --------------------------------------------------------------
async function sendQuestion() {
    let input = document.getElementById("userInput");
    let question = input.value.trim();
    if (!question) return;

    addMessage(question, "user");
    input.value = "";

    const response = await fetch(API_URL + "/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question })
    });

    const data = await response.json();

    // ❗ Teknik olmayan sorular
    if (
        (data.message && data.message.includes("teknik bir soru değil")) ||
        (data.answer && data.answer.includes("teknik bir soru değil"))
    ) {
        addMessage("Bu soru teknik bir soru değil. Lütfen teknik bir soru sorun.", "bot");
        return;
    }

    // ❗ Teknik soru listesine ekle
    askedQuestions.push(question);

    // ❗ Teknik cevap + feedback
    if (data.answer) {
        addBotMessageWithFeedback(question, data.answer, data.top_question);
    }

     // 🔥 Her 3 soruda bir quiz teklif et
    if (askedQuestions.length % 3 === 0) {
        offerQuiz();
    }
}

// --------------------------------------------------------------
// BOT CEVABI + FEEDBACK BUTONLARI
// --------------------------------------------------------------
function addBotMessageWithFeedback(userInput, answer, originalQuestion) {
    const buttons = `
        <div style="margin-top:10px;">
            <small>Bu cevap yeterli miydi?</small><br>

            <button 
                onclick="handleFeedbackClick(this); sendFeedback('${userInput}', '${answer}', true, '${originalQuestion}')"
                style="margin-right:8px; padding:5px 10px;">
                Evet
            </button>

            <button 
                onclick="handleFeedbackClick(this); sendFeedback('${userInput}', '${answer}', false, '${originalQuestion}')"
                style="padding:5px 10px;">
                Hayır
            </button>
        </div>
    `;

    addMessage(answer, "bot", buttons);
}

// --------------------------------------------------------------
// BUTONA BASINCA BUTONLARI KALDIR
// --------------------------------------------------------------
function handleFeedbackClick(btn) {
    btn.parentNode.remove();
}

// --------------------------------------------------------------
// İLK FEEDBACK ( /feedback )
// --------------------------------------------------------------
async function sendFeedback(userInput, answer, satisfied, originalQuestion) {

    if (satisfied) {
        addMessage("Teşekkürler! Yardımcı olabildiysem ne mutlu. 😊", "bot");
        return;
    }

    const res = await fetch(API_URL + "/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            user_input: userInput,
            answer: answer,
            satisfied: false,
            original_question: originalQuestion
        })
    });

    const data = await res.json();
    const alt = data.alternative_answer;

    const buttons = `
        <div style="margin-top:10px;">
            <small>Bu açıklama daha iyi oldu mu?</small><br>

            <button 
                onclick="handleFeedbackClick(this); sendFinalFeedback('${userInput}', '${answer}', '${alt}', true, '${originalQuestion}')"
                style="margin-right:8px; padding:5px 10px;">
                Evet
            </button>

            <button 
                onclick="handleFeedbackClick(this); sendFinalFeedback('${userInput}', '${answer}', '${alt}', false, '${originalQuestion}')"
                style="padding:5px 10px;">
                Hayır
            </button>
        </div>
    `;

    addMessage(alt, "bot", buttons);
}

// --------------------------------------------------------------
// SON FEEDBACK ( /feedback2 )
// --------------------------------------------------------------
async function sendFinalFeedback(userInput, answer, altAnswer, satisfied, originalQuestion) {

    if (satisfied) {
        addMessage("Harika! Yardımcı olabildiğime sevindim. 🎉", "bot");
        return;
    }

    const note = prompt("Eğitmene iletmek istediğiniz bir not var mı? (Boş bırakılabilir)");

    await fetch(API_URL + "/feedback2", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            user_input: userInput,
            answer: answer,
            alt_answer: altAnswer,
            original_question: originalQuestion,
            satisfied: false,
            user_message: note || ""
        })
    });

    addMessage("Tamamdır! Durum eğitmene iletildi. 📩", "bot");
}

// --------------------------------------------------------------
// QUIZ BAŞLAT
// --------------------------------------------------------------
async function startQuiz() {
    const response = await fetch(API_URL + "/quiz", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            questions: askedQuestions,
            num_questions: 3
        })
    });

    const data = await response.json();

    quizData = data.quiz;
    currentQuizIndex = 0;
    quizResults = [];

    showQuizStep();
}

// --------------------------------------------------------------
// QUIZ GÖSTER
// --------------------------------------------------------------
let currentQuizIndex = 0;
let quizData = [];
let quizResults = [];

function showQuizStep() {
    const quizContainer = document.getElementById("quizContainer");
    quizContainer.innerHTML = "";
    quizContainer.style.display = "block";

    const q = quizData[currentQuizIndex];

    let qDiv = document.createElement("div");
    qDiv.innerHTML = `<h3>${currentQuizIndex + 1}) ${q.question}</h3>`;

    q.options.forEach((opt, i) => {
        let btn = document.createElement("div");
        btn.className = "quiz-option";
        btn.innerText = opt;

        btn.onclick = function () {

            // 🔥 Önce tüm seçenekleri kilitle
            const siblings = qDiv.querySelectorAll(".quiz-option");
            siblings.forEach(s => s.onclick = null);

            // 🔥 Kullanıcının seçimine göre renk ver
            if (i === q.correct_index) {
                btn.classList.add("correct");
                quizResults.push(true);
            } else {
                btn.classList.add("wrong");
                quizResults.push(false);
            }

            // 🔥 Doğru şık her durumda yeşil olsun
            siblings[q.correct_index].classList.add("correct");

            // 🔥 Biraz bekleyip sonraki soruya geç
            setTimeout(() => {
                currentQuizIndex++;

                if (currentQuizIndex < quizData.length) {
                    showQuizStep();
                } else {
                    showQuizSummary();
                }

            }, 800);
        };

        qDiv.appendChild(btn);
    });

    quizContainer.appendChild(qDiv);
}


// --------------------------------------------------------------
// QUIZ TEKLİFİ (Her 3 soruda bir)
// --------------------------------------------------------------
function offerQuiz() {
    const buttons = `
        <div class="quiz-offer" style="margin-top:10px; padding:10px;">
            <small>Hazır mısın? Küçük bir quiz yapmak ister misin?</small><br>

            <button 
                onclick="startQuiz()"
                style="margin-top:8px; padding:8px 14px; background:#28a745; color:white; border:none; border-radius:6px;">
                Quiz Başlat
            </button>
        </div>
    `;

    addMessage("", "bot", buttons);
}

function showQuizSummary() {
    removeQuizOffers();  // 🔥 tüm quiz butonlarını kaldır

    const quizContainer = document.getElementById("quizContainer");

    const total = quizResults.length;
    const correct = quizResults.filter(x => x === true).length;
    const wrong = total - correct;
    const percent = ((correct / total) * 100).toFixed(1);

    quizContainer.innerHTML = `
        <h2>🎉 Quiz tamamlandı!</h2>
        <p><strong>Doğru sayısı:</strong> ${correct}</p>
        <p><strong>Yanlış sayısı:</strong> ${wrong}</p>
        <p><strong>Başarı oranı:</strong> %${percent}</p>
        <br>
        <button onclick="closeQuiz()" 
                style="padding:8px 14px; background:#4f8cff; color:white; border:none; border-radius:6px;">
            Kapat
        </button>
    `;
}

function closeQuiz() {
    document.getElementById("quizContainer").style.display = "none";
    removeQuizOffers(); // 🔥 sohbet içindeki butonları da kaldır
}


function removeQuizOffers() {
    const chatBox = document.getElementById("chatBox");

    // Sohbet içindeki bütün quiz butonlarını sil
    const offers = chatBox.querySelectorAll(".quiz-offer");
    offers.forEach(offer => offer.remove());
}

