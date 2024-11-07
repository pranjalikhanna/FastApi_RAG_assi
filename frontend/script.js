document.getElementById("ingestForm").addEventListener("submit", async function (e) {
    e.preventDefault();
    const formData = new FormData();
    formData.append("file", document.getElementById("documentFile").files[0]);

    const response = await fetch("/ingest", {
        method: "POST",
        body: formData,
    });

    const result = await response.json();
    alert(result.message || result.error);
});

async function queryDocument() {
    const query = document.getElementById("queryInput").value;
    
    const response = await fetch("/query", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: query }),
    });

    const data = await response.json();
    const resultsList = document.getElementById("resultsList");
    resultsList.innerHTML = "";

    if (data.results) {
        data.results.forEach(result => {
            const li = document.createElement("li");
            li.textContent = result.content;  // Displaying content of matched documents
            resultsList.appendChild(li);
        });
    } else {
        const li = document.createElement("li");
        li.textContent = "No results found.";
        resultsList.appendChild(li);
    }
}
