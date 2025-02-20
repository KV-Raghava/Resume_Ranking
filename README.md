# Resume Ranking

This repository provides a solution for automating resume ranking using FastAPI and OpenAI. It handles extracting key criteria from job descriptions and evaluates resumes based on these criteria, enabling automated HR processes for candidate evaluation.

## Features

- Extracts key criteria from job descriptions.
- Evaluates resumes based on extracted criteria.
- Automates HR processes for candidate evaluation.
- Built with FastAPI and OpenAI.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/KV-Raghava/Resume_Ranking.git
    cd Resume_Ranking
    ```

2. Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4. Add your open ai key in env file
   ```OPENAI_API_KEY = "enter your open api key here" ```


## Usage

1. Start the FastAPI server:
    ```bash
    fastapi run app.py
    ```

2. Access the API documentation at `http://127.0.0.1:8000/docs`.

## API Endpoints

- `POST /extract-criteria`: Extracts ranking criteria from a job description.
- `POST /evaluate-resume`: Evaluates a resume based on the extracted criteria.

## File Structure

- `app.py`: The main entry point of the application.
- `routes/criteria.py`: Contains the routes for extracting criteria and evaluating resumes.
- `routes/scoring.py`: Contains the routes for resume scoring api



## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/)
- [OpenAI](https://www.openai.com/)
