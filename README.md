# AI Tutor Chat Application

This Chainlit-based application serves as an AI tutor, leveraging various large language models (LLMs) to provide interactive learning experiences. It includes features for student assessment, knowledge tracking, and adaptive responses.

## Features

- **Multiple Model Support**: Configurable to use different LLMs including OpenAI's GPT-4 and Mistral AI models.
- **Student Assessment**: Automatically assesses student interactions and updates a student record.
- **Knowledge Tracking**: Maintains and updates a knowledge base for each student.
- **Adaptive Responses**: Uses conversation history and student records to provide context-aware responses.
- **Streamed Responses**: Delivers model responses in real-time as they are generated.
- **Configurable System Prompts**: Allows enabling/disabling of system prompts and class context.

## Prerequisites

- Python 3.7+
- API keys for OpenAI and/or RunPod (depending on chosen model)

## Installation and Setup

1. **Clone the Repository**:
   ```sh
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Create a Virtual Environment**:
   ```sh
   python -m venv .venv
   source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
   ```

3. **Install Dependencies**:
   ```sh
   pip install -r requirements.txt
   ```

## Configuration

1. **API Keys**: 
   - Copy the `.env.sample` file and rename it to `.env`
   - Replace the placeholder values with your actual API keys and Runpod endpoints
   - Note: Runpod keys are optional

2. **Model Selection**:
   - Choose the desired model by setting the `config_key` variable in `app.py`.

3. **System Prompts and Class Context**:
   - Adjust the `ENABLE_SYSTEM_PROMPT` and `ENABLE_CLASS_CONTEXT` flags as needed.

4. **Customize Prompts**:
   - Modify the prompt templates in the `prompts.py` file to suit your educational context.

## Running the Application

1. **Activate the Virtual Environment** (if not already activated):
   ```sh
   source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
   ```

2. **Run the Chainlit App**:
   ```sh
   chainlit run app.py -w
   ```

3. Open your browser and navigate to the URL displayed in the terminal.

## Usage

- Start a conversation with the AI tutor by typing a message.
- The application will process your input, update the student record, and provide a contextual response.
- Student records are automatically updated and stored in `student_record.md`.

## Key Components

- `app.py`: Main application file containing the Chainlit setup and message handling logic.
- `prompts.py`: Contains prompt templates for system instructions and assessments.
- `student_record.py`: Handles reading, writing, and formatting of student records.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request with your proposed changes.

## License

This project is licensed under the MIT License.



