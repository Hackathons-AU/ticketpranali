const fs = require('fs');
const path = require('path');

exports.handler = async function(event, context) {
    try {
        const filePath = path.resolve(__dirname, 'db.json'); // Correct the path if needed
        const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));

        return {
            statusCode: 200,
            headers: {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',  // Allow all origins
                'Access-Control-Allow-Methods': 'GET'
            },
            body: JSON.stringify(data)
        };
    } catch (error) {
        return {
            statusCode: 500,
            headers: {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',  // Allow all origins in error response
            },
            body: JSON.stringify({ error: 'Failed to load data' })
        };
    }
};
