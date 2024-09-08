const fs = require('fs');
const path = require('path');

exports.handler = async function(event, context) {
    const filePath = path.resolve(__dirname, '../db.json'); // Adjust path if necessary
    const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));

    return {
        statusCode: 200,
        headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*', // Allow all origins (adjust for security as needed)
            'Access-Control-Allow-Methods': 'GET'
        },
        body: JSON.stringify(data)
    };
};
