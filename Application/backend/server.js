import express from 'express';
import fs from 'fs';
import cors from 'cors';

const app = express();
const pathSetting = "./setting.json";
const pathMap = "./map.json";
const pathCredential = "./credential.json";

app.use(cors());           
app.use(express.json());  

//Configurazione

app.get('/config', (req, res) => {
  let data = '{}';
  if (fs.existsSync(pathSetting)) {
    data = fs.readFileSync(pathSetting, 'utf-8') || '{}';
  } else {
    fs.writeFileSync(pathSetting, '{}');
  }
  try {
    res.json(JSON.parse(data));
  } catch {
    res.json({});
  }
});

app.post('/config', (req, res) => {
  console.log("<h1>Impostazioni</h1>")
  console.log("Dati ricevuti:", req.body);
  fs.writeFileSync(pathSetting, JSON.stringify(req.body, null, 4));
  res.sendStatus(200);
});

//Mappatura

app.get('/map', (req, res) => {
  let data = '{}';
  if (fs.existsSync(pathMap)) {
    data = fs.readFileSync(pathMap, 'utf-8') || '{}';
  } else {
    fs.writeFileSync(pathMap, '{}');
  }
  try {
    res.json(JSON.parse(data));
  } catch {
    res.json({});
  }
});

app.post('/map', (req, res) => {
  console.log("<h1>Mappa</h1>")
  console.log("Dati ricevuti:", req.body);
  fs.writeFileSync(pathMap, JSON.stringify(req.body, null, 4));
  res.sendStatus(200);
});

//Credenziali

app.get('/credential', (req, res) => {
  let data = '{}';
  if (fs.existsSync(pathCredential)) {
    data = fs.readFileSync(pathCredential, 'utf-8') || '{}';
  } else {
    fs.writeFileSync(pathCredential, '{}');
  }
  try {
    res.json(JSON.parse(data));
  } catch {
    res.json({});
  }
});

app.post('/credential', (req, res) => {
  console.log("<h1>Mappa</h1>")
  console.log("Dati ricevuti:", req.body);
  fs.writeFileSync(pathCredential, JSON.stringify(req.body, null, 4));
  res.sendStatus(200);
});

app.listen(3000, () => {
  console.log("Backend avviato su http://localhost:3000");
});
