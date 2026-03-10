# File Service

A microservice for centralized file management using Firebase Storage (binary files) and Firestore (metadata).

## Architecture

- **Firebase Storage**: Stores binary file blobs
- **Firestore**: Stores file metadata (filename, size, checksum, uploader, timestamps, etc.)
- **Local Fallback**: Uses local JSON files (in `local_store/`) when Firebase credentials are not configured (ideal for development)

## Setup

### 1. Environment Configuration

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

### 2. Firebase Credentials (Optional for Production)

For production, set up a Firebase project:

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a project or use an existing one
3. Go to **Project Settings** → **Service Accounts**
4. Click **Generate New Private Key** and save the JSON file
5. Place the JSON file at `services/file_service/serviceAccountKey.json`
6. Set `GOOGLE_APPLICATION_CREDENTIALS=./serviceAccountKey.json` in `.env`

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Service

```bash
python -m flask --app app run --port 5010
```

## API Endpoints

### Upload a File

**Request:**
```bash
curl -X POST http://localhost:5010/upload \
  -F "file=@your_file.csv"
```

**Response:**
```json
{
  "success": true,
  "file_id": "uuid-1234-5678"
}
```

Alternatively, upload via JSON (base64):
```bash
curl -X POST http://localhost:5010/upload \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "data.csv",
    "content_base64": "..."
  }'
```

### Get File Metadata & Signed URL

**Request:**
```bash
curl http://localhost:5010/file/<file_id>
```

**Response:**
```json
{
  "file_id": "uuid-1234-5678",
  "metadata": {
    "file_id": "uuid-1234-5678",
    "filename": "data.csv",
    "content_type": "text/csv",
    "size": 12345,
    "checksum": "sha256...",
    "created_at": "2026-02-24T...",
    "uploader": "user123",
    "storage_path": "files/uuid-1234-5678"
  },
  "signed_url": "https://firebasestorage.googleapis.com/... (expires in 1 hour)"
}
```

Clients can download the file using the `signed_url`.

### Real-time Previews

The File Service publishes lightweight JSON previews of files to Firestore under the `previews/{file_id}` document and also streams updates over Server-Sent Events (SSE) for low-latency frontend updates.

- Firestore preview document: `previews/{file_id}` — contains the same JSON returned by `/file/<file_id>/preview`.
- SSE endpoint: `/stream/preview/<file_id>` — connect with an `EventSource` to receive JSON `message` events when previews update.

Example frontend subscription using EventSource:

```javascript
const fileId = '...';
const es = new EventSource(`http://localhost:5010/stream/preview/${fileId}`);
es.onmessage = (evt) => {
  try {
    const preview = JSON.parse(evt.data);
    // update UI table with preview.rows / preview.headers
  } catch (e) {
    console.warn('Invalid preview data', e);
  }
};
es.onerror = (err) => {
  console.warn('Preview stream error', err);
};

// Alternatively, listen to Firestore document `previews/{file_id}` for updates
// if you use Firebase client SDK on the frontend.
```

## Supported File Types

- CSV, XLS, XLSX (data files)
- TXT, PDF, JSON (documents)

## Development Notes

- Without Firebase credentials, the service falls back to local JSON storage in `local_store/`.
- Signed URLs are valid for 1 hour by default (configurable).
- All file metadata is stored with checksums for integrity verification.
