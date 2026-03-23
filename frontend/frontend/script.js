let selectedAlgo = "FCFS";
let chart;
let count = 1;

window.onload = function () {
  const saved = localStorage.getItem("algo");

  if (saved) {
    selectedAlgo = saved;
    document.getElementById("selected").innerText = saved;

    if (saved === "RR") {
      document.getElementById("tqBox").style.display = "block";
    }
  }
};

function addProcess() {
  const tbody = document.getElementById("inputs");

  const tr = document.createElement("tr");

  tr.innerHTML = `
    <td class="pname">P${count}</td>
    <td><input type="number" min="0"></td>
    <td><input type="number" min="1"></td>
    <td><button class="delete-btn">Delete</button></td>
  `;

  tr.querySelector(".delete-btn").onclick = function () {
    tr.remove();
    renumber();
  };

  tbody.appendChild(tr);

  count++;
}

function deleteRow(btn) {
  btn.closest("tr").remove();
  renumber();
}

function renumber() {
  const rows = document.querySelectorAll("#inputs tr");
  let i = 1;

  rows.forEach(row => {
    row.querySelector(".pname").innerText = "P" + i;
    i++;
  });

  count = i;
}

async function run() {
  const rows = document.querySelectorAll("#inputs tr");
  const processes = [];

  // SKIP HEADER ROW if your table has <th> in <thead>
  // If your rows includes the header, start loop from 1. 
  // Assuming #inputs is <tbody>, this is fine.
  
  rows.forEach((row, i) => {
    const inputs = row.querySelectorAll("input");
    // Only add if inputs exist
    if(inputs.length >= 2) {
        processes.push({
          pid: "P" + (i + 1),
          arrival: Number(inputs[0].value),
          burst: Number(inputs[1].value)
        });
    }
  });

  const tq = document.getElementById("tq").value;

  try {
      console.log("1. Sending data to backend:", processes);
      const res = await fetch("http://127.0.0.1:8000/schedule", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
          algorithm: selectedAlgo.toLowerCase(),
          processes: processes,
          // CHANGE THIS LINE: Use snake_case to match Pydantic model
          time_quantum: selectedAlgo === "RR" ? Number(tq) : null 
        })
      });

      console.log("2. Backend responded with status:", res.status);

      if (!res.ok) {
          alert("Error: " + res.statusText);
          return;
      }

      const data = await res.json();
      console.log("3. Data received:", data);

      showTable(data.processes);
      showGantt(data.gantt);
      showMetrics(data.metrics);
      showChart(data.comparison);
      
  } catch (err) {
      console.error("CRITICAL ERROR:", err);
      alert("JavaScript crashed! Check the F12 Console for details.");
  }
}

function showTable(data) {
  let html = `<table class="results-table">
              <thead>
                <tr>
                    <th>PID</th><th>AT</th><th>BT</th><th>CT</th><th>TAT</th><th>WT</th><th>RT</th>
                </tr>
              </thead>
              <tbody>`;

  data.forEach(p => {
    html += `
      <tr>
        <td>${p.pid}</td>
        <td>${p.arrival}</td>
        <td>${p.burst}</td>
        <td>${p.completion}</td>
        <td>${p.tat}</td>
        <td>${p.wt}</td>
        <td>${p.rt}</td>
      </tr>
    `;
  });

  html += "</tbody></table>";
  // Ensure you are targeting the DIV, not the TABLE tag itself if you are replacing innerHTML
  document.getElementById("table").innerHTML = html;
}

function showGantt(gantt) {
  const ganttContainer = document.getElementById("gantt");
  
  if (!gantt || gantt.length === 0) {
    ganttContainer.innerHTML = "<p class='text-muted'>No execution data to visualize.</p>";
    return;
  }

  const startTime = gantt[0].start;
  const endTime = gantt[gantt.length - 1].end;
  const totalTime = endTime - startTime;
  const safeTotalTime = totalTime > 0 ? totalTime : 1; 

  ganttContainer.style.display = "flex";
  ganttContainer.style.width = "100%";
  ganttContainer.style.height = "85px"; 
  ganttContainer.style.borderRadius = "8px";
  ganttContainer.style.overflow = "hidden";
  ganttContainer.style.backgroundColor = "#f0f0f0";
  ganttContainer.style.boxShadow = "inset 0 2px 4px rgba(0,0,0,0.1)";
  
  let html = "";
  let lastEndTime = gantt[0].start; // Track the end of the previous block

  gantt.forEach(g => {
    // 1. CHECK FOR GAPS: If there's a jump in time, add an Idle block first
    if (g.start > lastEndTime) {
      const idleDuration = g.start - lastEndTime;
      const idleWidth = (idleDuration / safeTotalTime) * 100;
      
      html += `
        <div class="gantt-box" style="
            width: ${idleWidth}%; 
            background: repeating-linear-gradient(45deg, #ccc, #ccc 10px, #dbdbdb 10px, #dbdbdb 20px);
            color: #555;
            display: flex; align-items: center; justify-content: center;
            border-right: 1px solid rgba(255,255,255,0.4);
            min-width: 20px;">
          <strong style="font-size: 11px;">Idle</strong>
        </div>`;
    }

    // 2. RENDER THE ACTUAL PROCESS
    const duration = g.end - g.start;
    const widthPercent = (duration / safeTotalTime) * 100; 
    const hue = (parseInt(g.pid.replace(/^\D+/g, '')) * 137) % 360;

    html += `
      <div class="gantt-box" style="
          width: ${widthPercent}%; 
          background-color: hsl(${hue}, 65%, 55%);
          color: white;
          display: flex; flex-direction: column; align-items: center; justify-content: center;
          border-right: 1px solid rgba(255,255,255,0.4);
          min-width: 30px;">
        <strong style="font-size: 13px;">${g.pid}</strong>
        <span style="font-size: 10px; font-weight: bold;">${g.start}-${g.end}</span>
      </div>
    `;

    lastEndTime = g.end; // Update the marker for the next iteration
  });

  ganttContainer.innerHTML = html;
}

function showMetrics(m) {
  document.getElementById("metrics").innerText =
    `Avg TAT: ${m.avg_tat} | Avg WT: ${m.avg_wt} | Avg RT: ${m.avg_rt} | CPU: ${m.cpu_util}% | Throughput: ${m.throughput}`;
}

function showChart(data) {
  if (chart) chart.destroy();

  const ctx = document.getElementById("chart").getContext("2d");
  
  chart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: data.map(d => d.name),
      datasets: [
        {
          label: "Avg TAT",
          data: data.map(d => d.avgTAT),
          backgroundColor: "rgba(79, 140, 255, 0.8)",
          borderColor: "#4f8cff",
          borderWidth: 1
        },
        {
          label: "Avg WT",
          data: data.map(d => d.avgWT),
          backgroundColor: "rgba(255, 77, 79, 0.8)",
          borderColor: "#ff4d4f",
          borderWidth: 1
        },
        {
          label: "Avg RT",
          data: data.map(d => d.avgRT),
          backgroundColor: "rgba(40, 167, 69, 0.8)",
          borderColor: "#28a745",
          borderWidth: 1
        }
      ]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: 'top' },
        title: { display: true, text: 'Algorithm Efficiency Comparison' }
      },
      scales: {
        y: { beginAtZero: true, title: { display: true, text: 'Time Units' } }
      }
    }
  });
}

function resetAll() {
  localStorage.removeItem("algo");
  window.location.href = "index.html";
}