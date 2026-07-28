# 💊 Medicine Reminder System

A complete, user-friendly, and feature-rich **Medicine Reminder System** built in Python with a sleek **CustomTkinter** desktop GUI, **SQLite** persistent storage, automated background scheduler for **desktop notifications & visual popups**, and adherence **history report generation**.

---

## 🌟 Key Features

- **🎨 Modern & Attractive Desktop UI**: Dark theme GUI with card layouts, color-coded status badges, and interactive navigation.
- **🔐 User Registration & Authentication**: Secure multi-user login and registration system with salted SHA-256 password hashing.
- **💊 Complete Medicine Management (CRUD)**:
  - **Add, Edit, and Delete** medicine details.
  - **Fields**: Medicine Name, Dosage (e.g. 500mg, 1 tablet), Start/End Date, Time(s) (supports multiple daily doses e.g., `08:00 AM, 02:00 PM, 08:00 PM`), Frequency (Daily, Weekly, Specific Days, As Needed), and Notes.
- **📊 Upcoming Reminders Dashboard**: Displays active medicines count, adherence rate score %, today's total scheduled doses, and quick-action dose cards.
- **⏰ Real-Time Background Scheduler & Notifications**:
  - Automatically polls for due medicine doses every 10 seconds.
  - Triggers native **Desktop Notifications (Toast)** via `plyer` and plays sound chimes.
  - Displays an **Interactive Pop-up Window Alert** directly on screen allowing users to mark doses as **Taken** or **Missed** immediately.
- **✅ Status Tracking**: Mark dose reminders as **Taken**, **Missed**, or leave as **Pending**. Past due doses auto-update to Missed if ignored.
- **🗄️ SQLite Persistent Storage**: Relational schema with index optimizations for users, medicines, and daily dose logs.
- **🔍 Advanced Search & Filtering**:
  - Search by medicine name, dosage, or special instructions.
  - Filter by status (**All**, **Taken**, **Missed**, **Pending**).
  - Date Range Filtering (From Date to To Date).
- **📈 Adherence Reports & Exports**:
  - Calculates real-time adherence rate percentage `(Taken / Completed Doses * 100)`.
  - **Export CSV Report**: Downloads detailed history logs to CSV format.
  - **Export HTML Report**: Generates a printable HTML report document with summary metrics and structured tables.

---

## 📁 Project Folder Structure

```
Medicine Remainder System/
│
├── database/
│   ├── __init__.py
│   └── db_manager.py        # SQLite Database connection, schema creation & query methods
│
├── models/
│   ├── __init__.py
│   ├── user.py              # User authentication, registration & SHA-256 password hashing
│   ├── medicine.py          # Medicine model, scheduling logic & CRUD operations
│   └── reminder.py          # Reminder log model, status management & search/filter queries
│
├── utils/
│   ├── __init__.py
│   ├── notifier.py          # Desktop notification manager (plyer) & audio chimes
│   ├── scheduler.py         # Background daemon thread checking upcoming doses
│   └── reporter.py          # Adherence metrics calculation, CSV & HTML report generators
│
├── gui/
│   ├── __init__.py
│   ├── theme.py             # Design system color tokens, fonts & widget styling
│   ├── login_window.py      # Dual-tab Registration & Login screen
│   ├── dashboard_window.py  # Main Dashboard window with sidebar nav & header metrics
│   ├── views/
│   │   ├── __init__.py
│   │   ├── overview_view.py  # Stat metric cards, quick actions & today's schedule
│   │   ├── medicines_view.py # Add/Edit/Delete medicine management & modal form
│   │   ├── schedule_view.py  # Filterable upcoming reminders schedule
│   │   └── history_view.py   # Historical log list, search/filter & report exporters
│   └── components/
│       ├── __init__.py
│       └── popup_dialog.py  # Interactive pop-up dialog window alert when reminder triggers
│
├── main.py                  # Application entry point & lifecycle manager
├── requirements.txt         # Dependencies list (customtkinter, plyer, Pillow)
└── README.md                # Comprehensive documentation
```

---

## 🚀 Quick Setup & Execution Guide

### Prerequisites
- Python 3.8 or higher installed on your system.

### 1. Install Dependencies
Run the following command in your terminal to install required libraries:

```bash
pip install -r requirements.txt
```

*(Dependencies: `customtkinter`, `plyer`, `Pillow`, `darkdetect`)*

### 2. Launch Application
Run the main script to start the GUI app:

```bash
python main.py
```

---

## 📖 Usage Instructions

1. **User Registration & Login**:
   - On initial launch, switch to the **Register Account** tab.
   - Enter your Full Name, Username, and Password, then click **Create Account**.
   - Switch back to the **Login** tab and sign in.

2. **Managing Medicines**:
   - Navigate to the **Medicines** tab on the sidebar.
   - Click **➕ Add New Medicine**.
   - Fill in Medicine Name, Dosage, Start/End Dates, Scheduled Times (e.g. `08:00 AM, 02:00 PM`), Frequency, and Notes.
   - Click **Save Medicine Details**. You can edit or delete medicines anytime.

3. **Viewing Upcoming Reminders & Taking Doses**:
   - Check the **Overview** or **Schedule** tab for today's scheduled doses.
   - When the scheduled time arrives, the background scheduler will fire a **Desktop Toast Notification** and display an **Interactive Pop-up Window Alert**.
   - Click **✔ Mark as Taken** or **✖ Mark as Missed** directly from the popup or schedule cards.

4. **History & Reports**:
   - Navigate to the **History & Reports** tab.
   - Use the **Search** box or **Status** / **Date Range** filters to analyze history.
   - Click **📥 Export CSV** or **📊 Export HTML Report** to save a complete adherence report to your computer.

---

## 🛡️ License

This project is open-source and free to use for personal or educational purposes.
