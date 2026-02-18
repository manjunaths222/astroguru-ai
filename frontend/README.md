# AstroGuru AI Frontend

React-based frontend for AstroGuru AI application.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start development server:
```bash
npm run dev
```

3. Build for production:
```bash
npm run build
```

The build output will be in `dist/` directory, which will be served by the FastAPI backend.

## Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_BASE_URL=http://localhost:8002
```

## Development

- Development server runs on `http://localhost:3000`
- API proxy is configured to forward `/api` requests to `http://localhost:8002`
- Hot module replacement (HMR) is enabled

## Production Build

After building, the `dist/` folder should be placed in the `astroguru-ai/` directory so the backend can serve it.

