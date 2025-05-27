document.addEventListener('DOMContentLoaded', () => {

  // --- Обробник для акордеону локацій ---
  const locationCards = document.querySelectorAll('.location-card');
  locationCards.forEach(card => {
    card.addEventListener('click', () => toggleDetails(card));
    card.addEventListener('keydown', (event) => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault(); // Запобігаємо прокрутці сторінки при натисканні пробілу
        toggleDetails(card);
      }
    });
  });

  // --- Обробники для QR-кодів ---
  const qrButtons = document.querySelectorAll('.social-icons button');
  qrButtons.forEach(button => {
    const platform = button.classList.contains('viber') ? 'viber' :
                     button.classList.contains('telegram') ? 'telegram' : 'instagram';
    button.addEventListener('click', () => showQR(platform));
  });

  // --- Закриття QR-попапу ---
  const qrPopup = document.getElementById('qrPopup');
  const closeQrBtn = document.querySelector('.close-btn');
  if (closeQrBtn) {
    closeQrBtn.addEventListener('click', hideQR);
    closeQrBtn.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' || event.key === ' ') {
            hideQR();
        }
    });
  }
   // Додаємо обробник подій для закриття QR-попапу при кліку поза ним
   if (qrPopup) {
     qrPopup.addEventListener('click', function(event) {
        const qrBox = document.querySelector('.qr-box');
        if (event.target === qrPopup && qrBox) { // Закриваємо тільки якщо клік по фону
            hideQR();
        }
     });
   }


  // --- Обробник для кнопки генерації рекомендацій ---
  const generateButton = document.getElementById('generateSuggestionBtn');
  if (generateButton) {
    generateButton.addEventListener('click', generateServiceSuggestion);
  }

  // --- Обробник для відправки контактної форми ---
  const contactForm = document.getElementById('contactForm');
  if (contactForm) {
    contactForm.addEventListener('submit', handleFormSubmit);
  }

});

/**
 * Показує спливаюче вікно з QR-кодом для обраної платформи.
 * @param {string} platform - Назва соціальної платформи ('viber', 'telegram', 'instagram').
 */
function showQR(platform) {
  const urls = {
    viber: 'viber://chat?number=%2B380951053838',
    telegram: 'https://t.me/KoSAService_Official',
    instagram: 'https://www.instagram.com/kosa_service/'
  };
  const texts = {
    viber: 'Відскануйте для зв\'язку у Viber',
    telegram: 'Відскануйте для зв\'язку у Telegram',
    instagram: 'Відскануйте для переходу в Instagram'
  };

  const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(urls[platform])}`;
  document.getElementById('qrImage').src = qrUrl;
  document.getElementById('qrText').textContent = texts[platform];
  document.getElementById('qrPopup').style.display = 'flex';
}

/**
 * Приховує спливаюче вікно з QR-кодом.
 */
function hideQR() {
  document.getElementById('qrPopup').style.display = 'none';
}

/**
 * Перемикає видимість деталей картки локації (акордеон).
 * Закриває всі інші відкриті картки.
 * @param {HTMLElement} card - Елемент картки локації, яку потрібно перемкнути.
 */
function toggleDetails(card) {
  document.querySelectorAll('.location-card.open').forEach(openCard => {
    if (openCard !== card) {
      openCard.classList.remove('open');
    }
  });
  card.classList.toggle('open');
}


/**
 * Генерує рекомендації щодо послуг на основі опису проблеми користувача за допомогою Gemini API.
 */
async function generateServiceSuggestion() {
  const problemDescription = document.getElementById('problemDescription').value;
  const suggestionResult = document.getElementById('suggestionResult');
  const loadingSpinner = document.getElementById('loadingSpinner');
  const generateButton = document.getElementById('generateSuggestionBtn');

  if (!problemDescription.trim()) {
    suggestionResult.innerHTML = '<p style="color: red;">Будь ласка, опишіть вашу проблему.</p>';
    return;
  }

  suggestionResult.innerHTML = '';
  loadingSpinner.style.display = 'block';
  generateButton.disabled = true;

  const servicesList = `
    - Ремонт побутової техніки (телевізорів, мультиварок, мікрохвильовок, пилососів, духовок)
    - Ремонт комп'ютерної техніки (смартфонів, ноутбуків, моноблоків, системних блоків)
    - Заправка картриджів (для принтерів та ремонт копіювальної техніки)
    - Ремонт електротранспорту (електросамокатів, гіроскутерів)
    - Ремонт ручного електроінструменту (дрелей, шуруповертів, відбійних молотків)
    - Ремонт бензоінструменту та транспорту (генераторів, бензопил, квадроциклів)
  `;

  const prompt = \`Ви - експерт з ремонту техніки компанії KoSA Service. Користувач описує свою проблему. Надайте коротку попередню діагностику (1-2 речення) та запропонуйте, яка з перерахованих нижче послуг KoSA Service найбільше підходить для вирішення цієї проблеми. Також вкажіть, яку інформацію користувачу варто підготувати для майстра. Відповідь має бути українською мовою.

Опис проблеми користувача: "\${problemDescription}"

Наші послуги:
\${servicesList}

Формат відповіді:
**Попередня діагностика:** [Ваша діагностика]
**Рекомендована послуга:** [Назва послуги з переліку]
**Що підготувати для майстра:** [Список інформації]\`;

  // !!! УВАГА: API ключ НІКОЛИ не повинен бути у фронтенд-коді.
  // Цей запит має йти через твій бекенд, який вже буде додавати ключ.
  // Поки що залишаю поле для ключа порожнім.
  const apiKey = "";
  const apiUrl = \`https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=\${apiKey}\`;

  try {
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ contents: [{ parts: [{ text: prompt }] }] })
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(\`API error: \${response.status} - \${errorData.error.message}\`);
    }

    const result = await response.json();
    const text = result.candidates[0].content.parts[0].text;
    suggestionResult.innerHTML = \`<p>\${text.replace(/\\n/g, '<br>')}</p>\`;

  } catch (error) {
    console.error('Error calling Gemini API:', error);
    suggestionResult.innerHTML = \`<p style="color: red;">Виникла помилка: \${error.message}. Будь ласка, спробуйте пізніше.</p>\`;
  } finally {
    loadingSpinner.style.display = 'none';
    generateButton.disabled = false;
  }
}

/**
 * Обробляє відправку контактної форми.
 * @param {Event} e - Подія відправки форми.
 */
async function handleFormSubmit(e) {
  e.preventDefault();
  const form = e.target;
  const statusDiv = document.getElementById('formStatus');
  statusDiv.textContent = '';

  const formData = new FormData(form);
  const data = Object.fromEntries(formData.entries());

  if (!data.name || !data.phone || !data.message) {
    statusDiv.style.color = 'red';
    statusDiv.textContent = 'Будь ласка, заповніть усі поля.';
    return;
  }

  statusDiv.style.color = 'black';
  statusDiv.textContent = 'Відправка...';

  try {
    // Ось тут ми відправляємо дані на наш майбутній бекенд, а не в Telegram напряму
    const response = await fetch('/api/sendMessage', { // ЦЕ УЯВНА АДРЕСА! ЇЇ ТРЕБА БУДЕ СТВОРИТИ.
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });

    if (response.ok) {
      statusDiv.style.color = 'green';
      statusDiv.textContent = 'Дякуємо! Ваше повідомлення надіслано.';
      form.reset();
    } else {
      statusDiv.style.color = 'red';
      statusDiv.textContent = 'Помилка відправки. Спробуйте ще раз або напишіть нам у месенджер.';
    }
  } catch (err) {
    console.error('Form submission error:', err);
    statusDiv.style.color = 'red';
    statusDiv.textContent = 'Виникла помилка з\'єднання. Спробуйте ще раз.';
  }
}
