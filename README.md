# Warsaw AI

Warsaw AI is a full-stack application that provides an AI-powered chat assistant. It features a modern frontend built with Next.js and a robust backend powered by FastAPI.

## Features

- **AI Chat Assistant**: A sophisticated chat interface for interacting with the AI.
- **Voice Transcription**: (In progress) Functionality for transcribing voice to text.
- **Modern Frontend**: A sleek and responsive user interface built with the latest web technologies.
- **Asynchronous Backend**: A high-performance backend that can handle long-running tasks.
- **Modular Architecture**: A clean and organized codebase that is easy to maintain and extend.

## Tech Stack

### Frontend

- **Framework**: Next.js 14
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui

### Backend

- **Framework**: FastAPI
- **Language**: Python
- **Asynchronous Server**: Uvicorn

## Installation

### Prerequisites

- Node.js and npm
- Python 3.8+ and pip

### Backend

1.  **Navigate to the backend directory:**

    ```bash
    cd backend
    ```

2.  **Create a virtual environment:**

    ```bash
    python -m venv venv
    ```

3.  **Activate the virtual environment:**

    - On Windows:
      ```bash
      venv\Scripts\activate
      ```
    - On macOS and Linux:
      ```bash
      source venv/bin/activate
      ```

4.  **Install the dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

5.  **Run the backend server:**
    ```bash
    uvicorn main:app --reload
    ```

### Frontend

1.  **Navigate to the frontend directory:**

    ```bash
    cd frontend
    ```

2.  **Install the dependencies:**

    ```bash
    npm install
    ```

3.  **Run the frontend development server:**
    ```bash
    npm run dev
    ```

## Project Structure

```
.
├── backend
│   ├── main.py
│   ├── requirements.txt
│   └── ...
├── frontend
│   ├── src
│   │   └── ...
│   ├── package.json
│   └── ...
├── docs
│   └── ...
├── tests
│   └── ...
├── LICENSE
└── README.md
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
