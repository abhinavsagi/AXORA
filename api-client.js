// AXORA API client. The UI can call these methods when the FastAPI service is running.
const AXORA_API = 'http://127.0.0.1:8000/api';
async function axoraGet(path){
  const r = await fetch(`${AXORA_API}${path}`);
  if(!r.ok) throw new Error(`AXORA API ${r.status}`);
  return r.json();
}
async function getDashboard(){ return axoraGet('/dashboard'); }
async function getTelemetry(){ return axoraGet('/telemetry'); }
async function analyzeTelemetry(payload){
  const r = await fetch(`${AXORA_API}/analyze`, {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
  if(!r.ok) throw new Error(`AXORA API ${r.status}`);
  return r.json();
}
