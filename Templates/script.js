// Function to convert JSON data to HTML table
function convertJsonToTable(jsonData) {
    // Get the table body element
    let tableBody = document.getElementById("userData");

    // Loop through the JSON data
    for (const [username, userData] of Object.entries(jsonData)) {
        // Create a new row
        let row = tableBody.insertRow();

        // Insert cells into the row
        let cell1 = row.insertCell(0);
        let cell2 = row.insertCell(1);
        let cell3 = row.insertCell(2);

        // Set the cell values
        cell1.textContent = username;
        cell2.textContent = userData.password;
        cell3.textContent = JSON.stringify(userData.chathistory);
    }
}

// Fetch JSON data and convert to table
fetch('./users.json')
    .then(response => response.json())
    .then(data => convertJsonToTable(data))
    .catch(error => console.error('Error:', error));