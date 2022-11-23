const express = require('express')
const { readFile } = require('fs')

// Use Express library to handle  the server side
const app = express()

// Read html file and serve it to Node.js
app.get('/', (request, response) => {

    readFile('template/index.html', 'utf-8', (err, html) => {
        
        response.send(html)
        
    })
});

// Send static files to the server
app.use("/static", express.static('template'));
app.use("/static", express.static('scripts'));

// Run the website
app.listen(process.env.PORT || 3000, () => console.log("Website running at: \t http://localhost:3000"))