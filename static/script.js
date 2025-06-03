let currentYear = 2025;
let currentMonth = 5;
let tagChart = null;
let topChart = null;
let monthChart = null;

// 태그별 사용량
function fetchAndRenderTagStats(year, month) {
  fetch(`/api/tag-stats?year=${year}&month=${month}`)
    .then(res => res.json())
    .then(result => {
      const ctx = document.getElementById('tagChart').getContext('2d');
      const greens = ['#C8F7C5', '#95FF8F', '#5DB075', '#388E3C', '#205D27'];
      if (!tagChart) {
        tagChart = new Chart(ctx, {
          type: 'bar',
          data: {
            labels: result.labels,
            datasets: [{
              label: '사용량',
              data: result.data,
              backgroundColor: greens.slice(0, result.labels.length)
            }]
          },
          options: {
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true } }
          }
        });
      } else {
        tagChart.data.labels = result.labels;
        tagChart.data.datasets[0].data = result.data;
        tagChart.data.datasets[0].backgroundColor = greens.slice(0, result.labels.length);
        tagChart.update();
      }
    });
}

// 제일 많이 쓴 재료
function fetchAndRenderTopIngredients(year, month) {
  fetch(`/api/top-ingredients?year=${year}&month=${month}`)
    .then(res => res.json())
    .then(result => {
      const ctx = document.getElementById('topChart').getContext('2d');
      const greens = ['#C8F7C5', '#95FF8F', '#5DB075', '#388E3C', '#205D27'];
      if (!topChart) {
        topChart = new Chart(ctx, {
          type: 'bar',
          data: {
            labels: result.labels,
            datasets: [{
              label: '사용량',
              data: result.data,
              backgroundColor: greens.slice(0, result.labels.length)
            }]
          },
          options: {
            indexAxis: 'y',
            plugins: { legend: { display: false } },
            scales: { x: { beginAtZero: true } }
          }
        });
      } else {
        topChart.data.labels = result.labels;
        topChart.data.datasets[0].data = result.data;
        topChart.data.datasets[0].backgroundColor = greens.slice(0, result.labels.length);
        topChart.update();
      }
    });
}

// 월별 소비량 (여러 연도)
function fetchAndRenderMonthStats() {
  fetch('/api/month-stats')
    .then(res => res.json())
    .then(result => {
      const ctx = document.getElementById('monthChart').getContext('2d');
      if (!monthChart) {
        monthChart = new Chart(ctx, {
          type: 'line',
          data: {
            labels: result.labels,
            datasets: [
              {
                label: '소비량',
                data: result.consume,
                borderColor: '#5db075',
                backgroundColor: 'rgba(93,176,117,0.15)',
                tension: 0.3,
                pointBackgroundColor: '#5db075'
              },
              {
                label: '버린 양',
                data: result.discard,
                borderColor: '#388E3C',
                backgroundColor: 'rgba(56,142,60,0.10)',
                tension: 0.3,
                pointBackgroundColor: '#388E3C'
              }
            ]
          },
          options: {
            plugins: { legend: { display: true } },
            scales: { y: { beginAtZero: true } }
          }
        });
      } else {
        monthChart.data.labels = result.labels;
        monthChart.data.datasets[0].data = result.consume;
        monthChart.data.datasets[1].data = result.discard;
        monthChart.update();
      }
    });
}


function updateMonthNav() {
  document.getElementById('currentMonth').textContent = `${currentYear}년 ${currentMonth}월`;
}

// 월 이동 버튼 이벤트
document.getElementById('prevMonth').onclick = function() {
  if (currentMonth === 1) {
    currentMonth = 12;
    currentYear -= 1;
  } else {
    currentMonth -= 1;
  }
  updateMonthNav();
  fetchAndRenderTagStats(currentYear, currentMonth);
  fetchAndRenderTopIngredients(currentYear, currentMonth);
};
document.getElementById('nextMonth').onclick = function() {
  if (currentMonth === 12) {
    currentMonth = 1;
    currentYear += 1;
  } else {
    currentMonth += 1;
  }
  updateMonthNav();
  fetchAndRenderTagStats(currentYear, currentMonth);
  fetchAndRenderTopIngredients(currentYear, currentMonth);
};

// 최초 실행
window.onload = function() {
  updateMonthNav();
  fetchAndRenderTagStats(currentYear, currentMonth);
  fetchAndRenderTopIngredients(currentYear, currentMonth);
  fetchAndRenderMonthStats();
};
