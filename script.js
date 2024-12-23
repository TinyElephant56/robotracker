const canvas = document.getElementById('field');
const ctx = canvas.getContext('2d');

function parseCSV(file) {
    fetch(file)
        .then(response => response.text()) // Convert the response to text
        .then(csvText => {
            // Parse the CSV text using PapaParse
            Papa.parse(csvText, {
                complete: function (results) {
                    const data = results.data;
                    const parsedData = data.map(line => {
                        const values = line.map(Number); // Convert values to numbers
                        const pairs = [];
                        for (let i = 0; i < values.length; i += 2) {
                            pairs.push([values[i], values[i + 1]]);
                        }
                        return pairs;
                    });
                    console.log(parsedData); // This will log the parsed and grouped data
                }
            });
        })
}
const coordinates = parseCSV("dontcommit/482/bluecords.csv")