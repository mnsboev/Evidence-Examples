const http = require("http");
const fs = require("fs");
const path = require("path");
const server = http.createServer((req, res) => {
    let filePath;
    if (req.url === "/" || req.url === "/form.html") {
        filePath = path.join("C:\\app\\dist\\html", "form.html");
    } else {
        filePath = path.join("C:\\app\\dist", req.url);
    }
    fs.readFile(filePath, (err, data) => {
        if (err) {
            console.log("File not found: " + filePath);
            res.writeHead(404);
            res.end("File not found: " + req.url);
        } else {
            const ext = path.extname(filePath);
            const mimeTypes = { ".html": "text/html", ".css": "text/css", ".js": "application/javascript" };
            res.writeHead(200, { "Content-Type": mimeTypes[ext] || "text/plain", "Access-Control-Allow-Origin": "*" });
            res.end(data);
        }
    });
});
server.listen(8080, () => console.log("Server running on port 8080"));
