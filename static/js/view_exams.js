// static/js/view_exams.js

let currentPage = 1;
const rowsPerPage = 6;

function displayTable() {
  const table = document.getElementById("examsTable");
  const rows = table.getElementsByTagName("tr");
  const totalRows = rows.length - 1; // exclude header row
  const totalPages = Math.ceil(totalRows / rowsPerPage);

  // Hide all rows except header
  for (let i = 1; i < rows.length; i++) {
    rows[i].style.display = "none";
  }

  // Display rows for the current page
  const start = (currentPage - 1) * rowsPerPage + 1;
  const end = Math.min(start + rowsPerPage - 1, totalRows);
  for (let i = start; i <= end; i++) {
    rows[i].style.display = "";
  }

  // Update page number
  document.getElementById("pageNumber").textContent = `Page ${currentPage}`;
}

function nextPage() {
  const table = document.getElementById("examsTable");
  const totalRows = table.getElementsByTagName("tr").length - 1; // exclude header row
  const totalPages = Math.ceil(totalRows / rowsPerPage);

  if (currentPage < totalPages) {
    currentPage++;
    displayTable();
  }
}

function prevPage() {
  if (currentPage > 1) {
    currentPage--;
    displayTable();
  }
}

function searchFunction() {
  const input = document.getElementById("searchInput").value.toLowerCase();
  const table = document.getElementById("examsTable");
  const rows = table.getElementsByTagName("tr");

  for (let i = 1; i < rows.length; i++) {
    const cells = rows[i].getElementsByTagName("td");
    let match = false;
    for (let j = 0; j < cells.length - 1; j++) {
      // exclude last cell (Action)
      if (cells[j].textContent.toLowerCase().includes(input)) {
        match = true;
        break;
      }
    }
    rows[i].style.display = match ? "" : "none";
  }

  // Reset pagination
  currentPage = 1;
  displayTable();
}

// Initial display
displayTable();
