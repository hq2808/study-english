# 📘 Smart English Learning App

Ứng dụng web học tiếng Anh giao tiếp trình độ A1, A2, B1 - tích hợp tra từ điển nhanh và ôn tập từ vựng bằng Flashcard.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Tính năng chính

### 1. 📖 Interactive Reading (Đọc tương tác)
- Hiển thị các bài đọc/hội thoại mẫu trình độ A1, A2, B1
- **Hover (Di chuột)** vào bất kỳ từ nào để xem:
  - 🔊 Phiên âm (Text-to-Speech)
  - 🇻🇳 Nghĩa tiếng Việt
- Nút "Save" để lưu từ vào Flashcard

### 2. 🎧 Audio (Luyện nghe)
- Tích hợp Text-to-Speech (gTTS) 
- Nghe phát âm từng từ hoặc toàn bộ bài đọc
- Giọng đọc tiếng Anh chuẩn từ Google

### 3. 🃏 Vocabulary Review (Ôn tập Flashcard)
- Hệ thống Flashcard để ôn lại các từ đã lưu
- Lật thẻ để xem nghĩa
- Theo dõi số lần ôn tập (Review count)
- Đánh dấu từ đã thuộc (Mastered: 5+ reviews)
- Xáo trộn thẻ để ôn tập hiệu quả

---

## 🛠️ Công nghệ sử dụng

| Thành phần | Công nghệ |
|------------|-----------|
| Backend | Python Flask |
| Database | SQLite + SQLAlchemy ORM |
| Frontend | HTML5, TailwindCSS, Vanilla JS |
| Text-to-Speech | gTTS (Google TTS) |
| Dịch thuật | deep-translator |

---

## 🚀 Hướng dẫn cài đặt
docker exec -it postgres_service psql -U postgres

CREATE DATABASE study_english;

\l

\q

python -m venv .venv

.venv\Scripts\activate

pip install -r requirements.txt

python app.py
Truy cập: **http://127.0.0.1:5000**

---

## 📁 Cấu trúc thư mục

```
study-enlish/
├── app.py                 # Flask application chính
├── requirements.txt       # Danh sách thư viện
├── english_learning.db    # SQLite database (tự động tạo)
├── templates/
│   ├── base.html         # Template gốc
│   ├── index.html        # Trang đọc bài
│   └── flashcards.html   # Trang ôn tập Flashcard
└── README.md             # Hướng dẫn sử dụng
```

---

## 📚 Nội dung bài học

### Level A1 (Beginner)
- Greetings - Chào hỏi
- Family - Gia đình  
- Daily Routine - Thói quen hàng ngày
- Shopping - Mua sắm

### Level A2 (Elementary)
- Travel Plans - Kế hoạch du lịch
- At the Restaurant - Tại nhà hàng
- Health and Doctor - Sức khỏe
- Job Interview - Phỏng vấn xin việc

### Level B1 (Intermediate)
- Environmental Issues - Môi trường
- Technology and Society - Công nghệ
- Cultural Differences - Văn hóa
- Future Career Planning - Nghề nghiệp

---

## 🎮 Hướng dẫn sử dụng

### Đọc bài và tra từ
1. Chọn level (A1/A2/B1) từ sidebar
2. Click vào bài học muốn đọc
3. **Di chuột (hover)** vào từ bất kỳ để xem nghĩa
4. Click "🔊 Speak" để nghe phát âm
5. Click "➕ Save" để lưu vào Flashcard

### Ôn tập Flashcard
1. Click "Flashcards" trên thanh navigation
2. Click vào thẻ để lật xem nghĩa
3. Click ✓ để đánh dấu đã ôn
4. Dùng phím ← → để chuyển thẻ
5. Nhấn Space để lật thẻ

### Phím tắt
| Phím | Chức năng |
|------|-----------|
| ← | Thẻ trước |
| → | Thẻ sau |
| Space | Lật thẻ |
| Enter | Đánh dấu đã ôn |

---

## 🔧 API Endpoints

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/` | Trang chính |
| GET | `/flashcards` | Trang Flashcard |
| GET | `/api/lessons` | Lấy danh sách bài học |
| GET | `/api/lessons?level=A1` | Lọc theo level |
| GET | `/api/lessons/<id>` | Chi tiết bài học |
| POST | `/api/translate` | Dịch từ sang tiếng Việt |
| POST | `/api/tts` | Chuyển text thành audio |
| GET | `/api/vocabulary` | Danh sách từ đã lưu |
| POST | `/api/vocabulary` | Lưu từ mới |
| PUT | `/api/vocabulary/<id>/review` | Cập nhật review count |
| DELETE | `/api/vocabulary/<id>` | Xóa từ |

---

## 📝 License

MIT License - Tự do sử dụng cho mục đích học tập.

---

## 👨‍💻 Tác giả

Developed with ❤️ for English learners.
