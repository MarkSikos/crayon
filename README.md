# Crayon: Educational Software with Artificial Intelligence

Welcome to **Crayon**, an innovative educational software designed to address teaching challenges in primary schools, particularly in lower grades. This project aims to provide solutions for teachers who face the burden of manually correcting and checking students' work. The software integrates handwriting processing modules to facilitate the learning process and provide immediate feedback to students.

## Features

### Teacher Dashboard
- **Task Assignment:** Teachers can create, assign, and manage tasks for students.
- **Automatic Evaluation:** The software can evaluate students' handwritten answers, reducing the workload for teachers.
- **Performance Tracking:** View detailed statistics and performance metrics of students.

### Student Interface
- **Handwriting Practice:** Students can practice handwriting just as they would in their notebooks.
- **Immediate Feedback:** Get instant feedback on handwriting and spelling.
- **Task Management:** Access and complete assigned tasks and homework.

## Installation Guide

### System Requirements
- **Operating System:** Windows 10/11
- **RAM:** Minimum 4 GB, recommended 8 GB
- **Python Version:** 3.8

### Required Libraries
Install the required libraries using pip:
```sh
pip install PyQt6 sqlite3 pytesseract keras-ocr numpy fuzzywuzzy opencv-python unidecode bcrypt matplotlib
```

### Running the Application
1. Clone the repository:
    ```sh
    git clone <repository_url>
    ```
2. Navigate to the project directory:
    ```sh
    cd crayon
    ```
3. Run the application:
    ```sh
    python AppController.py
    ```

## Technical Overview

### Architecture
The software follows a Model-View (MV) architecture:
- **Model:** Handles the core logic and data management.
- **View:** Manages the user interface.

### Technologies Used
- **PyQt6:** For developing the graphical user interface.
- **TensorFlow & Keras OCR:** For handwriting recognition and text processing.
- **SQLite:** For database management.
- **Matplotlib:** For generating graphs and charts in the teacher dashboard.

## How It Works

### Handwriting Recognition
The software uses a combination of Keras OCR and Tesseract OCR for text recognition. It processes handwritten input from students and provides immediate feedback.

### Task Management
Teachers can create tasks and assignments which are automatically assigned to all students. The software allows for real-time evaluation and feedback on these tasks.

## Future Improvements
- **Online Multi-user Environment:** Expanding the application to support multiple users online.
- **Enhanced OCR Capabilities:** Improving the OCR model to better handle diverse handwriting styles, including special characters and accents.
- **Advanced Features:** Adding more functionalities like collaborative tools for students and advanced analytics for teachers.

## Contributing
We welcome contributions to improve Crayon! Feel free to open issues or submit pull requests.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgements
Special thanks to the Eötvös Loránd University, Department of Artificial Intelligence, and all contributors to this project.
