document.addEventListener('DOMContentLoaded', function () {
  const sidebar = document.querySelector('.sidebar');
  const toggleBtn = document.querySelector('.sidebar-toggle');

  toggleBtn.addEventListener('click', () => {
    sidebar.classList.toggle('active');
  });
});

document.addEventListener("DOMContentLoaded", () => {
    const brokerSelect = document.getElementById("broker-select");
    const instructionDivs = document.querySelectorAll(".broker-instructions");

    brokerSelect.addEventListener("change", function () {
        // Hide all instruction boxes
        instructionDivs.forEach(div => div.style.display = "none");

        // Show only selected broker instructions
        const selected = this.value;
        const activeDiv = document.getElementById(`${selected}-instructions`);
        if (activeDiv) activeDiv.style.display = "block";
    });
});