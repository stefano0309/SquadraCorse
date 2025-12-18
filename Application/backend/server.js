import express from 'express';
import fs from 'fs';
import cors from 'cors';

const app = express();
const path = "./setting.json";
const path2 = "./map.json"

app.use(cors());           
app.use(express.json());  

app.get('/config', (req, res) => {
  let data = '{}';
  if (fs.existsSync(path)) {
    data = fs.readFileSync(path, 'utf-8') || '{}';
  } else {
    fs.writeFileSync(path, '{}');
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
  fs.writeFileSync(path, JSON.stringify(req.body, null, 4));
  res.sendStatus(200);
});

app.get('/map', (req, res) => {
  let data = '{}';
  if (fs.existsSync(path2)) {
    data = fs.readFileSync(path2, 'utf-8') || '{}';
  }else{
    fs.writeFileSync(path2, '{}');
  }
  try {
    res.json(JSON.parse(data));
  } catch {
    res.json({})
  }
})

app.post('/map', (req, res) => {
  console.log("<h1>Impostazioni</h1>")
  console.log("Dati ricevuti:", req.body);
  fs.writeFileSync(path, JSON.stringify(req.body, null, 4));
  res.sendStatus(200);
});

app.listen(3000, () => {
  console.log("Backend avviato su http://localhost:3000");
});
