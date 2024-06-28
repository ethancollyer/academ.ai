const express = require('express');  // Web framework module for node.js
const fileUpload = require('express-fileupload');  // Middleware for handling file uploads and express applications
const { exec } = require('child_process');  // Importing exec function from child_process module to execute shell commands from within node.js application
const fs = require('fs');  // API for interacting with file system
const path = require('path');  // Module providing utilities for working with file and directory paths
const { type } = require('os');

process.env.PYTHON = 'C:\\virtual_environments\\acedem.ai_venv\\Scripts\\python.exe';  // Setting path to Python interpreter

// Setting constants and variables
const app = express();
const port = 3000;
var chatHistory = null;

// Configuring express app to use fileUpload and json middleware functions
app.use(fileUpload());
app.use(express.json());

// Endpoint to serve html file to client's browser
app.get('/', (req, res) => {
    console.log("GET request received for root URL");
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Endpoint to handle file uploads
app.post('/upload_file', (req, res) => {
    console.log("POST request recieved for /upload_file");
    const uploadedFile = req.files.file;

    console.log("Uploaded File:", uploadedFile);

    // Ensure the "uploads" directory exists
    const uploadsDir = path.join(__dirname, 'uploads');
    if (!fs.existsSync(uploadsDir)) {
        fs.mkdirSync(uploadsDir);
        console.log("Uploads directory created:", uploadsDir);
    }

    // Specify the correct file path
    const filePath = path.join(uploadsDir, uploadedFile.name);
    uploadedFile.mv(filePath, (err) => {
        if (err) {
            console.error(err);
            res.status(500).json({ error: 'Internal Server Error' }); // Send back an error response
        } else {
            console.log("File uploaded successfully:", filePath);
            console.log("File preprocessing...");
            
            // Execute the load_questions.py script
            exec(`python load_questions.py "${filePath}"`, (error, stdout, stderr) => {
                if (error) {
                    console.error(`exec error: ${error}`);
                    res.status(500).json({ error: 'Internal Server Error' }); // Send back an error response
                    return;
                }
                const questions_json = JSON.parse(stdout.toString());
                console.log("Preprocessing completed successfully:");
                console.log(`stdout: ${stdout}`);
                console.log(`stderr: ${stderr}`);
                console.log("Loaded Questions: ", questions_json);
                res.json({ file_path: filePath, file_name: uploadedFile.name, questions_json: questions_json });
                console.log("[+] Completed Execution");
            });
        }
    });
});

// Endpoint to handle user question selection
app.post('/question_selection', (req, res) => {
    console.log("POST request recieved for /question_selection");
    question = req.body.question;

    // Call your PDF reader script (app.py) with the question and file path
    exec(`python question_selection.py "${question}"`, (error, stdout, stderr) => {
        if (error) {
            console.error(`exec error: ${error}`);
            res.status(500).json({ error: 'Internal Server Error' }); // Send back an error response
            return;
        }
        console.log("Python script executed successfully");
        console.log(`stdout: ${stdout}`);
        console.log(`stderr: ${stderr}`);
        const result = JSON.parse(stdout.toString());
        chatHistory = result.chat_history;
        console.log("Chat History: ", chatHistory)
        res.json(result);
        console.log("[+] Completed Execution");
    });
});

// Endpoint to handle user messages
app.post('/user_message', (req, res) => {
    console.log("POST request recieved for /user_message");
    var question = req.body.question;
    chatHistory = req.body.chat_history;
    console.log("Chat History data type: ", typeof(chatHistory)); //.replace(/"/g, '\\"');
    console.log("Chat History: ", typeof(chatHistory), chatHistory);
    const chatHistoryJson = JSON.stringify(chatHistory).replace(/"/g, '\\"');
    console.log("Chat History JSON: ", typeof(chatHistoryJson), chatHistoryJson);

    // Call your PDF reader script (app.py) with the question and file path
    exec(`python app.py "${chatHistoryJson}" "${question}"`, (error, stdout, stderr) => {
        if (error) {
            console.error(`exec error: ${error}`);
            res.status(500).json({ error: 'Internal Server Error' }); // Send back an error response
            return;
        }
        console.log("Python script executed successfully");
        console.log(`stdout: ${stdout.toString()}`);
        console.log(`stderr: ${stderr}`);
        const result = JSON.parse(stdout.toString());
        chatHistory = result.chat_history;
        res.json(result);
        console.log("[+] Completed Execution");
    });
});

// 
app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});
