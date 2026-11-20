# SE2-1-NovaInspections
**Solinal Label Project**

NovaInspections is a web application designed to facilitate the review of product labels intended for export, helping verify compliance with the labeling requirements and regulations of the destination country or region.

The platform allows users to upload product labels for AI-assisted analysis, identify potential non-compliance issues, and receive observations that can help correct labeling errors before export.

## Deployed Application

| Component | Link | Description |
|---|---|---|
| Frontend | https://se-2-1-nova-inspections.vercel.app/ | NovaInspections web application |
| Backend | https://novainspections-api.onrender.com | Backend API |
| Health Check | https://novainspections-api.onrender.com/health | Checks the backend service status |
| API Documentation | https://novainspections-api.onrender.com/docs | Interactive API documentation |

## Technologies Used

### Frontend
- React
- TypeScript
- Vite

### Backend
- Python
- FastAPI
- Uvicorn

### Artificial Intelligence
- Google Gemini API
- Gemini Flash models for label analysis.

### Deployment and Version Control
- Vercel – Frontend hosting.
- Render – Backend hosting.
- GitHub – Source code and version control.

## Main Features

- Upload product labels and documents.
- File format and upload validation.
- Identification of the product's destination country or region.
- Acceptance of terms and conditions before using the platform and its analysis features.
- AI-assisted analysis to review compliance with labeling requirements.
- Identification of potential non-compliance issues and observations.
- Presentation of analysis results.
- Access to previously performed analyses.

## System Architecture

NovaInspections follows a frontend-backend architecture:

1. Users access the web application deployed on Vercel.
2. Users upload a product label and specify its destination country or region.
3. Users review and accept the platform's terms and conditions.
4. The frontend sends the uploaded file and required information to the backend through HTTP requests.
5. The backend validates and processes the uploaded file.
6. The artificial intelligence service uses Google Gemini to analyze the label and evaluate its compliance with the applicable requirements.
7. The backend returns the analysis results to the frontend for presentation.

## Environment Variables

The backend uses environment variables to configure Google Gemini integration and other service settings.

The main environment variables include:

- `GEMINI_API_KEY`: API key used to access Google Gemini.
- `AI_MODE`: Defines the artificial intelligence operating mode.
- `AI_MODEL`: Primary Gemini model.
- `AI_FALLBACK_MODEL`: Alternative models used if the primary model is unavailable.
- `AI_THINKING`: Configures the model's thinking level.
- `AI_TIMEOUT_S`: Maximum waiting time for an individual request.
- `AI_MAX_PAGES`: Maximum number of pages processed.
- `CORS_ORIGINS`: Authorized origins allowed to send requests to the backend.

**Important:** API keys and other credentials must remain private. They must never be committed to the repository or shared publicly.

## Production Deployment

The project is deployed using the following services:

- **Frontend:** Vercel.
- **Backend:** Render.
- **Artificial Intelligence:** Google Gemini API.

The frontend communicates with the backend through the `VITE_API_URL` environment variable. The backend uses `CORS_ORIGINS` to authorize requests originating from the production frontend domain.

The backend is configured to use Google Gemini in real mode (`AI_MODE=real`).

## Backend Monitoring and Documentation

The backend service status can be checked through the following endpoint:

https://novainspections-api.onrender.com/health

Interactive API documentation is available at:

https://novainspections-api.onrender.com/docs

## Academic Project

Developed as part of the Software Engineering II course.

**Repository:** [SE2-1-NovaInspections](https://github.com/aaortizdev/SE2-1-NovaInspections)