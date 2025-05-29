let currentMonth = 5;
let tagChart = null;
let topChart = null;
let monthChart = null;

// 태그별 사용량
function fetchAndRenderTagStats(month) {
  fetch(`/api/tag-stats?month=${month}`)
    .then(res => res.json())
    .then(result => {
      const ctx = document.getElementById('tagChart').getContext('2d');
      if (!tagChart) {
        tagChart = new Chart(ctx, {
          type: 'bar',
          data: {
            labels: result.labels,
            datasets: [{
              label: '사용량',
              data: result.data,
              backgroundColor: ['#C8F7C5', '#95FF8F', '#5DB075', '#388E3C', '#205D27']
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
        tagChart.update();
      }
    });
}

// 제일 많이 쓴 재료
function fetchAndRenderTopIngredients(month) {
  fetch(`/api/top-ingredients?month=${month}`)
    .then(res => res.json())
    .then(result => {
      const ctx = document.getElementById('topChart').getContext('2d');
      if (!topChart) {
        topChart = new Chart(ctx, {
          type: 'bar',
          data: {
            labels: result.labels,
            datasets: [{
              label: '사용량',
              data: result.data,
              backgroundColor: '#5db075'
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
        topChart.update();
      }
    });
}

// 월별 소비량 (12달)
function fetchAndRenderMonthStats() {
  fetch('/api/month-stats')
    .then(res => res.json())
    .then(result => {
      const ctx = document.getElementById('monthChart').getContext('2d');
      if (!monthChart) {
        monthChart = new Chart(ctx, {
          type: 'line',
          data: {
            labels: ['1월','2월','3월','4월','5월','6월','7월','8월','9월','10월','11월','12월'],
            datasets: [{
              label: '소비량',
              data: result.data,
              borderColor: '#5db075',                   
              backgroundColor: 'rgba(93,176,117,0.15)',
              tension: 0.3,
              pointBackgroundColor: '#5db075'
            }]
          },
          options: {
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true } }
          }
        });
      } else {
        monthChart.data.datasets[0].data = result.data;
        monthChart.update();
      }
    });
}

const monthNames = ['1월','2월','3월','4월','5월','6월','7월','8월','9월','10월','11월','12월'];
function updateMonthNav() {
  document.getElementById('currentMonth').textContent = monthNames[currentMonth-1];
}

// 월 이동 버튼 이벤트
document.getElementById('prevMonth').onclick = function() {
  currentMonth = currentMonth === 1 ? 12 : currentMonth - 1;
  updateMonthNav();
  fetchAndRenderTagStats(currentMonth);
  fetchAndRenderTopIngredients(currentMonth);
};
document.getElementById('nextMonth').onclick = function() {
  currentMonth = currentMonth === 12 ? 1 : currentMonth + 1;
  updateMonthNav();
  fetchAndRenderTagStats(currentMonth);
  fetchAndRenderTopIngredients(currentMonth);
};

// 최초 실행
window.onload = function() {
  updateMonthNav();
  fetchAndRenderTagStats(currentMonth);
  fetchAndRenderTopIngredients(currentMonth);
  fetchAndRenderMonthStats();
};
