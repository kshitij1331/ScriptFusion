let isEditing = false;
let editedRows = {}; // Tracks edited rows

async function fetchData() {
    try {
        const response = await fetch('/controls'); 
        const data = await response.json();

        if (!Array.isArray(data) || data.length === 0) {
            console.error("Invalid API response format");
            return;
        }

        const tableHeader = document.getElementById("table-header");
        const tableBody = document.getElementById("table-body");
        const filterRow = document.getElementById("filter-row");

        tableHeader.innerHTML = "";
        tableBody.innerHTML = "";
        filterRow.innerHTML = "";

        editedRows = {}; // Reset changes tracking

        const requiredColumns = {
            "id": ["id"],
            "ControlID": ["refId"],  
            "ControlName": ["controlName"],
            "ControlType": ["controlType"],
            "Severity": ["severity"],
            "ControlDataType": ["controlDataType"],
            "ThresholdCondition": ["thresholdCondition"],
            "ThresholdValue": ["thresholdValue"]
        };

        Object.keys(requiredColumns).forEach(header => {
            let filterTh = document.createElement("th");
            let input = document.createElement("input");
            input.type = "text";
            input.placeholder = "Filter...";
            input.className = "filter-input";
            input.dataset.column = header;  
            input.addEventListener("input", filterTable);
            filterTh.appendChild(input);
            filterRow.appendChild(filterTh);
        });

        Object.keys(requiredColumns).forEach(header => {
            let th = document.createElement("th");
            th.textContent = header;
            tableHeader.appendChild(th);
        });

        function findValue(obj, possibleKeys) {
            for (let key of possibleKeys) {
                if (obj.hasOwnProperty(key)) {
                    return obj[key];
                }
            }
            return "N/A";
        }

        data.forEach(item => {
            let row = document.createElement("tr");
            row.dataset.id = item.id;

            Object.values(requiredColumns).forEach((possibleKeys, index) => {
                let td = document.createElement("td");
                td.textContent = findValue(item, possibleKeys);
                td.contentEditable = false;

                td.addEventListener("input", () => {
                    editedRows[row.dataset.id] = getRowData(row);
                    document.getElementById("submit-btn").disabled = false;
                });

                row.appendChild(td);
            });

            tableBody.appendChild(row);
        });

        updateRowCount();

    } catch (error) {
        console.error("Error fetching data:", error);
    }
}

function filterTable() {
    const filters = {};
    document.querySelectorAll(".filter-input").forEach(input => {
        filters[input.dataset.column] = input.value.toLowerCase();
    });

    let visibleRows = 0;
    document.querySelectorAll("#table-body tr").forEach(row => {
        let showRow = true;
        row.querySelectorAll("td").forEach((td, index) => {
            const columnName = Object.keys(filters)[index];  
            if (filters[columnName] && !td.textContent.toLowerCase().includes(filters[columnName])) {
                showRow = false;
            }
        });

        row.style.display = showRow ? "" : "none";
        if (showRow) visibleRows++;
    });

    updateRowCount(visibleRows);
}

function updateRowCount(count = null) {
    count = document.querySelectorAll("#table-body tr:not([style*='display: none'])").length;
    document.getElementById("row-count").textContent = `Total Rows: ${count}`;
}

function toggleEditMode() {
    isEditing = !isEditing;
    document.querySelectorAll("#table-body tr td").forEach(td => {
        td.contentEditable = isEditing;
    });
    document.getElementById("edit-btn").textContent = isEditing ? "Disable Editing" : "Enable Editing";
}

function getRowData(row) {
    const cells = row.querySelectorAll("td");
    return {
        id: row.dataset.id,
        refId: cells[1].textContent,
        controlName: cells[2].textContent,
        controlType: cells[3].textContent,
        severity: cells[4].textContent,
        controlDataType: cells[5].textContent,
        thresholdCondition: cells[6].textContent,
        thresholdValue: cells[7].textContent
    };
}

async function submitChanges() {
    const changes = Object.values(editedRows);
    for (let change of changes) {
        try {
            const response = await fetch(`/controls/${change.id}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(change)
            });

            if (!response.ok) throw new Error(await response.text());
        } catch (error) {
            console.error("Error updating row:", error);
        }
    }

    alert("Changes submitted successfully!");
    document.getElementById("submit-btn").disabled = true;
    document.getElementById("edit-btn").textContent = "Enable Editing";
    isEditing = false;  // Reset editing mode
    fetchData(); // Refresh table with updated data
}


document.getElementById("edit-btn").addEventListener("click", toggleEditMode);
document.getElementById("submit-btn").addEventListener("click", submitChanges);

fetchData();
