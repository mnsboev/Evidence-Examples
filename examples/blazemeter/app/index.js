const express = require('express');
const app = express();
const port = 3000;

app.get('/', (req, res) => {
  res.send('Hello Users!');
});

app.get('/api/data', (req, res) => {
  const delay = Math.floor(Math.random() * 200) + 50; 
  setTimeout(() => {
    res.json({
      title: "delectus aut autem",
      completed: false
    });
  }, delay);
});

app.listen(port, () => {
  console.log(`App listening at http://localhost:${port}`);
});
