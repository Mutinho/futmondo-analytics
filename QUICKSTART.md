# 🚀 Guía Rápida de Inicio

## Inicio Rápido en 3 Pasos

### 1️⃣ Backend (Terminal 1)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

✅ Backend corriendo en: http://localhost:8000

---

### 2️⃣ Frontend (Terminal 2)

```bash
cd frontend
npm install
npm start
```

✅ Frontend corriendo en: http://localhost:3000

---

### 3️⃣ Acceso Público con ngrok (Terminal 3 - Opcional)

```bash
ngrok http 3000
```

✅ Copia la URL pública (ej: `https://xxxx.ngrok.io`) y compártela con tus amigos

---

## 🔍 Verificar que Todo Funciona

1. **Backend**: http://localhost:8000/health
2. **Frontend**: http://localhost:3000
3. **API Docs**: http://localhost:8000/docs

---

## ⚠️ Problemas Comunes

**Backend no inicia:**
- Verifica que el puerto 8000 esté libre
- Asegúrate de tener todas las dependencias instaladas

**Frontend no carga:**
- Verifica que el backend esté corriendo
- Abre la consola del navegador (F12) para ver errores

**ngrok no conecta:**
- Asegúrate de que el frontend esté en puerto 3000
- Verifica que ngrok esté instalado: `ngrok version`








